import sw_api
import time
from datetime import datetime, timezone
import json

X = sw_api.SWclient()


def grab_auth_token():

    with open("TRADING_DATA/auth_token.txt", "r") as file:
        auth_token = file.read().strip()
        X.authorization_token = str(auth_token)


grab_auth_token()


def grab_prices():

    with open("TRADING_DATA/price_data.txt", "r") as file:
        pdata = json.loads(file.read())  # Convert JSON string back to dict

    return pdata


while True:

    try:
        price_data = grab_prices()
    except Exception:
        continue

    for s in price_data.keys():

        buy_price = price_data[s]['bid']
        sell_price = price_data[s]['ask']

        X.conditional_order(price=[round(buy_price-0.05, 2), round(buy_price+0.30, 2)], buysell=['BUY', 'SELL'], amount=[1,1],
                            symbol=[s, s])

    grab_auth_token()

    time.sleep(60)
