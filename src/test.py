import requests
from time import sleep

file = open("./docs/token_bot.txt", "r")
token = file.read()

last_update_id = 0
ENDPOINT = f'https://api.telegram.org/{token}/'
while True:
    method = "getUpdates"
    parametri = {'offset': last_update_id}

    url = ENDPOINT + method
    response = requests.get(url, params=parametri)
    data = response.json()

    if len(data['result']) > 0:
        last_update_id = data['result'][0]['update_id'] + 1

        chat_id = data['result'][0]['message']['chat']['id']
        text = data['result'][0]['message']['text']

        # Invia il messaggio alla chat
        method = "sendMessage"
        parametri = {'chat_id': chat_id, 'text': 'Hai inviato ' + text}
        url = ENDPOINT + method
        requests.get(url, params=parametri)
        print(chat_id, text)


    print(response.json())

    sleep(5)