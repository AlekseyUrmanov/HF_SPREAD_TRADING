import time
import sw_api
import datetime
from datetime import datetime, timezone
import numpy as np
import json


X = sw_api.SWclient()
t = str(datetime.now().isoformat())[0:-3] + 'Z'


def grab_auth_token():

    with open("TRADING_DATA/auth_token.txt", "r") as file:
        auth_token = file.read().strip()
        X.authorization_token = str(auth_token)


def grab_prices():

    with open("TRADING_DATA/price_data.txt", "r") as file:
        pdata = json.loads(file.read())  # Convert JSON string back to dict

    return pdata


def compute_profit(transaction_array):
    pl = 0
    pair = []
    operator = -1
    past_value = 0

    for oto in transaction_array:

        oto = float(oto)

        if (oto * operator) > 0:

            pass

        else:

            pair.append(past_value)
            if len(pair) == 2:
                pl += sum(pair)
                pair = []
            else:
                pass

            operator = operator * -1

        past_value = oto

    return pl

grab_auth_token()

sent_requests = 0

sleep_time = 1

blast_order_collection = []

avg_spreads = {}

long_term_data = {'rolling_spread': [], 'pl': [], 'trans': []}


transactions = []



while True:


    try:
        data = grab_prices()
    except Exception:
        continue


    c = datetime.now()

    trading_shares = 1

    working_orders = X.get_orders(type='WORKING', from_time=t)
    open_order_stocks = set()

    batch_sell_orders = []
    for order in working_orders:
        try:
            order_symbol = order['orderLegCollection'][0]['instrument']['symbol']

        except Exception as error:

            print(error)
            break

        if order_symbol not in data.keys():
            continue

        order_status = order['status']

        if order_status == 'WORKING':

            open_order_stocks.add(order_symbol)
        else:
            continue

        order_price = order['price']
        old_order_id = order['orderId']
        filled = order['filledQuantity']
        remains = order['remainingQuantity']
        buy_or_sell = order['orderLegCollection'][0]['instruction']
        enter_time = order['enteredTime']
        ask_price = data[order_symbol]['ask']
        pos_effect = order['orderLegCollection'][0]['positionEffect']

        if buy_or_sell == 'BUY':

            timestamp = datetime.strptime(enter_time, "%Y-%m-%dT%H:%M:%S%z")

            now = datetime.now(timezone.utc)

            diff_seconds = (now - timestamp).total_seconds()

            if diff_seconds > 50:

                X.del_order(order_id=old_order_id)
                print('Delete Time Expired Order')
                sent_requests += 1


        else:
            gap = 0.03
            new_price = round(ask_price - gap, 2)

            if pos_effect == 'OPENING':
                X.del_order(order_id=old_order_id)
                sent_requests += 1

                print('Redundant Sell Order')
                continue

            if new_price >= order_price:
                pass

            else:

                sell_order_data = X.limit_order(symbol=order_symbol, amount=trading_shares,
                                                buysell=buy_or_sell, price=new_price,
                                                ret_json=True)
                transactions.append(new_price)
                batch_sell_orders.append(sell_order_data)
                '''X.put_replace(order_id_replacing=old_order_id,
                              price=round(new_price, 2),
                              amount=trading_shares,
                              symbol=order_symbol,
                              buysell=buy_or_sell,
                              market=False,
                              stop=False)'''


    if batch_sell_orders:
        X.blast_all(orders=batch_sell_orders)
        sent_requests += 1

    grab_auth_token()
    time.sleep(sleep_time)
    print(sent_requests)

