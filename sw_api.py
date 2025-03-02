import base64
import json
import time
import requests
import datetime
from datetime import timedelta, timezone


'''
New refresh token URL, then use original auth method
url = f'https://api.schwabapi.com/v1/oauth/authorize?client_id=NKZXXztAlpiGiyZc44errtsrsMInsF60&redirect_uri=https://127.0.0.1'

ACCOUNTHASHNUM = 'F4CD9DB8470C0BB53D322E6157336D31D07D0D3549F8D85CFD6615E618806376'

'''

class SWclient:

    def __init__(self):

        # "accountNumber": "69464639",
        # "hashValue": "7AB7448405301904073BD521EEC25E1E727C5EC5C5959501EE8732497E91BE4F"

        # 'F4CD9DB8470C0BB53D322E6157336D31D07D0D3549F8D85CFD6615E618806376' new hash value from new auth key, using own acc fx

        self.refresh_token = 'iwsGxBkOnzYFBMPnbLzm-l-1gq1MIlf5KrOxo4ab_QnxgxaJd4V0bKbxda0WgrvoK4Nojv-oM6ziu9GebC-N92kR_TBIcTHZ3SOmvodDpYMJv41WdsDGCMpJii0gxbSBU_WAUSQxLfk@'
        self.authorization_token = 'Bearer I0.b2F1dGgyLmJkYy5zY2h3YWIuY29t.ODFIPxGN5JChwQ1T1ddN_GAH7ev5WrvpT537qlTmDR4@'

        self.account_hash_num = 'F4CD9DB8470C0BB53D322E6157336D31D07D0D3549F8D85CFD6615E618806376'

    def quote_data(self, stocks):

        headers = {
            'accept': 'application/json',
            'Authorization': self.authorization_token,
        }

        params = {
            'symbols': stocks,  # 'NFLX, COST, TSLA, NVDA, HD, LLY' comma separated string
            'fields': 'quote',
            'indicative': 'false',
        }

        try:

            response = requests.get('https://api.schwabapi.com/marketdata/v1/quotes', params=params, headers=headers)

            return response.json()

        except Exception as error:
            print(error)
            return None

    def get_positions(self):

        headers = {
            'accept': 'application/json',
            'Authorization': self.authorization_token
        }

        params = {
            'fields': 'positions',
        }

        response = requests.get('https://api.schwabapi.com/trader/v1/accounts', params=params, headers=headers)
        #print(response.content)
        return response.json()

    def get_orders(self, type, from_time):  # FILLED or WORKING

        headers = {
            'accept': 'application/json',
            'Authorization': self.authorization_token
        }

        TO = str(datetime.datetime.now().isoformat())[0:-3] + 'Z'
        #print(TO)
        params = {
            'maxResults': 100,
            'fromEnteredTime': from_time,
            # (datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(minutes=420)).isoformat(),
            'toEnteredTime': '2025-04-25T09:46:33.027Z',
            # (datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(minutes=5)).isoformat(),
            'status': type,
        }

        try:

            response = requests.get(
                'https://api.schwabapi.com/trader/v1/accounts/' + self.account_hash_num + '/orders',
                params=params,
                headers=headers,
                timeout=None
            )

            return response.json()

        except Exception as error:
            print(error)
            return None

    def del_order(self, order_id):  # string

        order_id = str(order_id)

        url = 'https://api.schwabapi.com/trader/v1/accounts/' + self.account_hash_num + '/orders/' + order_id

        headers = {
            'accept': '*/*',
            'Authorization': self.authorization_token
        }

        response = requests.delete(
            url=url,
            headers=headers,
        )

        # print(response.content)

    def market_order(self, symbol, buysell, amount):
        headers = {
            'accept': '*/*',
            'Authorization': self.authorization_token,
            'Content-Type': 'application/json',
        }

        json_data = {
            'orderType': 'MARKET',
            'session': 'NORMAL',
            'duration': 'DAY',
            'orderStrategyType': 'SINGLE',
            'orderLegCollection': [
                {
                    'instruction': buysell,  # string
                    'quantity': amount,  # int
                    'instrument': {
                        'symbol': symbol,  # string
                        'assetType': 'EQUITY',
                    },
                },
            ],
        }

        response = requests.post(
            'https://api.schwabapi.com/trader/v1/accounts/' + self.account_hash_num + '/orders',
            headers=headers,
            json=json_data,
        )


    def limit_order(self, symbol, price, amount, buysell, ct=None, ret_json=False):

        headers = {
            'accept': '*/*',
            'Authorization': self.authorization_token,
            'Content-Type': 'application/json',

        }

        duration = 'DAY'
        if buysell == 'BUY':
            pass

        json_data = {

            'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',  # FILL_OR_KILL DAY, GOOD_TILL_CANCEL
            'price': price,  # string
            'orderStrategyType': 'SINGLE',
            'cancelable': True,
            #'specialInstruction': 'ALL_OR_NONE',
            'orderLegCollection': [
                {
                    'instruction': buysell,  # string
                    'quantity': amount,  # int
                    'instrument': {
                        'symbol': symbol,  # string
                        'assetType': 'EQUITY',

                    },
                },
            ],
        }

        if ct:
            json_data['cancelTime'] = ct # not a real functionality
            json_data['duration'] = 'GOOD_TILL_CANCEL'

        if ret_json:
            return json_data

        response = requests.post(
            'https://api.schwabapi.com/trader/v1/accounts/' + self.account_hash_num + '/orders',
            headers=headers,
            json=json_data,
        )
        print(response.content)

    def blast_all(self, orders):


        headers = {
            'accept': '*/*',
            'Authorization': self.authorization_token,
            'Content-Type': 'application/json',
        }

        json_data = {
            #'orderType': 'LIMIT',
            'session': 'NORMAL',
            'duration': 'DAY',  # FILL_OR_KILL DAY
            #'price': price,  # string
            'orderStrategyType': 'BLAST_ALL', # BLAST_ALL
            'childOrderStrategies': orders
            }

        response = requests.post(
            'https://api.schwabapi.com/trader/v1/accounts/' + self.account_hash_num + '/orders',
            headers=headers,
            json=json_data,
        )
        print(response.content)

    def original_auth(self):

        # get link buy putting URL into google and signing in

        # put link in here
        link = 'https://127.0.0.1/?code=C0.b2F1dGgyLmJkYy5zY2h3YWIuY29t.7YvbPS38dNoYMOaicxjoQXVtppGJ6LN52osMDpxudZE%40&session=de39aa32-e6c8-40b8-860d-6303ee275329'
        code = f'{link[link.index('code=') + 5:link.index('%40')]}@'

        byte_data = 'NKZXXztAlpiGiyZc44errtsrsMInsF60:YUdGqUhkkz7r7gHt'
        headers = {
            'accept': 'application/json',
            'Authorization': 'Basic ' + str(base64.b64encode(bytes(byte_data, 'utf-8')).decode('utf-8'))
        }

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'https://127.0.0.1'
        }

        response = requests.post('https://api.schwabapi.com/v1/oauth/token', data=data, headers=headers)
        dd = response.json()
        print(dd)
        at = dd['access_token']
        rt = dd['refresh_token']
        print(at)  # I0.b2F1dGgyLmNkYy5zY2h3YWIuY29t.e_N-h8YbSPDlTO7XBupG-PjejThbZ8lnxoiA8Pm2eeA@
        print(rt)  # lSMTBnzHeK8Nfs0JTOVCNWnlc3Zuy3Y3hLO2nrOMiGNwCwr-TAsEXyl3nzm5GSshXRBR2oJC4kozJa5Y-6jRt3rRRQP419_g
        return response.json()

    def refresh_token_auth(self):
        # post

        byte_data = 'NKZXXztAlpiGiyZc44errtsrsMInsF60:YUdGqUhkkz7r7gHt'
        headers = {
            'accept': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + str(base64.b64encode(bytes(byte_data, 'utf-8')).decode('utf-8'))
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'redirect_uri': 'https://127.0.0.1'
        }

        response = requests.post('https://api.schwabapi.com/v1/oauth/token', data=data, headers=headers)
        response_dictionary = response.json()
        print(response_dictionary)
        self.authorization_token = 'Bearer ' + str(response_dictionary['access_token'])

    def acc_nums(self):
        headers = {
            'accept': 'application/json',
            'Authorization': self.authorization_token
        }

        response = requests.get('https://api.schwabapi.com/trader/v1/accounts/accountNumbers', headers=headers)
        dd = response.json()
        print(dd)

    def put_replace(self, order_id_replacing, price, buysell, amount, symbol, market=False, stop = False):

        headers = {
            'accept': '*/*',
            'Authorization': self.authorization_token,
            'Content-Type': 'application/json',
        }

        if market:
            json_data = {
                'orderType': 'MARKET',
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'orderLegCollection': [
                    {
                        'instruction': buysell,  # string
                        'quantity': amount,  # int
                        'instrument': {
                            'symbol': symbol,  # string
                            'assetType': 'EQUITY',
                        },
                    },
                ],
            }

        else:

            if stop:

                json_data = {
                    "orderType": "STOP",  # or stop_limit
                    "session": "NORMAL",
                    # "price": stop[1], # where limit order is placed || must be less than trigger
                    "stopPrice": price,  # where trigger occurs
                    "duration": "DAY",
                    "orderStrategyType": "SINGLE",
                    "orderLegCollection": [
                        {
                            "instruction": buysell,
                            "quantity": amount,
                            "instrument": {
                                "symbol": symbol,
                                "assetType": "EQUITY"
                            }
                        }
                    ]
                }

            else:

                json_data = {
                    'orderType': 'LIMIT',
                    'session': 'NORMAL',
                    'duration': 'DAY',
                    'price': price,  # string
                    #'specialInstruction': 'ALL_OR_NONE',

                    'orderStrategyType': 'SINGLE',
                    'orderLegCollection': [
                        {
                            'instruction': buysell,  # string
                            'quantity': amount,  # int
                            'instrument': {
                                'symbol': symbol,  # string
                                'assetType': 'EQUITY',
                            },
                        },
                    ],
                }

        response = requests.put(
            'https://api.schwabapi.com/trader/v1/accounts/' + self.account_hash_num + '/orders/' + str(
                order_id_replacing),
            headers=headers,
            json=json_data,
        )
        print(response.content)

    def conditional_order(self, price, buysell, amount, symbol, duration='DAY', mark=False):
        headers = {
            'accept': '*/*',
            'Authorization': self.authorization_token,
            'Content-Type': 'application/json',
        }

        json_data = {
            'orderType': 'LIMIT',
            #'orderTypeRequest':'LIMIT',
            'session': 'NORMAL',
            'duration': duration,
            'price': price[0],  # string
            'orderStrategyType': 'TRIGGER',
            'orderLegCollection': [
                {
                    'instruction': buysell[0],  # string
                    'quantity': amount[0],  # int
                    'instrument': {
                        'symbol': symbol[0],  # string
                        'assetType': 'EQUITY',
                    },
                },
            ],

            'childOrderStrategies': [

                        {
                            'orderType': 'LIMIT',
                            'session': 'NORMAL',
                            'duration': 'DAY',
                            'price': price[1],  # string
                            'orderStrategyType': 'SINGLE',
                            'orderLegCollection': [
                                {
                                    'instruction': buysell[1],  # string
                                    'quantity': amount[1],  # int
                                    'instrument': {
                                        'symbol': symbol[1],  # string
                                        'assetType': 'EQUITY',
                                    },
                                },
                            ],

                        }


            ]


        }

        if mark:
            del json_data['childOrderStrategies'][0]['price']
            del json_data['childOrderStrategies'][0]['duration']
            json_data['childOrderStrategies'][0]['orderType'] = 'MARKET'

        response = requests.post(
            'https://api.schwabapi.com/trader/v1/accounts/' + self.account_hash_num + '/orders',
            headers=headers,
            json=json_data,
        )
        print(response.content)
        print(response)



