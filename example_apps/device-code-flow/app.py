import json
import time

import requests


def main():
    print("Starting the application...", end="\n\n")
    time.sleep(1)
    # Stage 1: Client requests a device code
    request_params = {"client_id": "spider_man", "scope": "openid profile"}
    response = requests.post("http://localhost:8000/device/", data=request_params)

    response_data = response.json()
    device_code = response_data.get("device_code")
    user_code = response_data.get("user_code")
    verification_uri = response_data.get("verification_uri")
    time.sleep(1)

    # Stage 2: User navigates to the device login form and enters the user_code
    print(f"Please navigate to {verification_uri} and enter the USER code")
    print(f"User code: {user_code}", end="\n\n")

    # Stage 3: Waiting for user to enter the user code and log in
    while True:
        response = requests.post("http://localhost:8000/token/",
                                 data={"client_id": "spider_man",
                                       "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                                       "device_code": device_code,
                                       "redirect_uri": "https://www.google.com/"},
                                 )
        if response.status_code != 200:
            # Stage 3.1: Waiting for user to enter the user code and log in
            print("Waiting for you to enter the code and authenticate yourself...", end="\r")
        else:
            # Stage 4: User has been authenticated, and we got the tokens
            print("\n\nYou have been successfully authenticated!")
            print("Here is your info we got:")
            print(json.dumps(response.json(), indent=4), end="\n\n")
            break

        time.sleep(1)


if __name__ == '__main__':
    main()
