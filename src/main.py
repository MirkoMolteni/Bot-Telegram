import requests
from time import sleep

file = open("./src/token_bot.txt", "r")
token = file.read()

last_update_id = 0
while True:
    ENDPOINT = f'https://api.telegram.org/{token}/'
    method = "getUpdates"
    parametri = {'offset': 0}

    url = ENDPOINT + method
    response = requests.get(url, params=parametri)
    data = response.json()
    #elaboro i dati
    #last_update_id = ... + 1
    print(data)

    sleep(5)