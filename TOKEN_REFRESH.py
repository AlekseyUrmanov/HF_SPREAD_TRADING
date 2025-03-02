import time

import sw_api
from datetime import datetime, timezone
X = sw_api.SWclient()


X.refresh_token_auth()


with open("auth_token.txt", "w") as file:
    file.write(X.authorization_token)

t = str(datetime.now().isoformat())[0:-3] + 'Z'


def check_refresh_token():

    global t

    time_obj = datetime.fromisoformat(t.replace("Z", "+00:00"))

    now = datetime.now(timezone.utc)

    elapsed_seconds = ((now - time_obj).total_seconds()) - 18000

    if elapsed_seconds > (60* 15):

        X.refresh_token_auth()

        with open("auth_token.txt", "w") as file:
            file.write(X.authorization_token)

        t = str(datetime.now().isoformat())[0:-3] + 'Z'

    else:

        pass


while True:

    check_refresh_token()

    time.sleep(300)

