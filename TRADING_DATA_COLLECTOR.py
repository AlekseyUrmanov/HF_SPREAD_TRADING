import sw_api
import time
from datetime import datetime, timezone
import json

X = sw_api.SWclient()


def grab_auth_token():

    with open("auth_token.txt", "r") as file:
        auth_token = file.read().strip()
        X.authorization_token = str(auth_token)


grab_auth_token()


def update_prices():

    data = X.quote_data(stocks='BX, ABNB, FUTU, APO, DECK')

    price_dict = {}

    for key in data.keys():

        ask = data[key]['quote']['askPrice']
        bid = data[key]['quote']['bidPrice']

        price_dict[key] = {'bid':bid, 'ask':ask}

    with open("price_data.txt", "w") as file:
        print('Writing '+str(price_dict))
        file.write(json.dumps(price_dict))


while True:

    update_prices()
    grab_auth_token()

    time.sleep(1)
