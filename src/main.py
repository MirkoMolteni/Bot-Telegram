import requests
from time import sleep
import mysql.connector
from mysql.connector import Error
import pandas as pd
ENDPOINT = f'https://api.telegram.org/bot{
    open("./docs/token_bot.txt", "r").read()}/'

args = ["","","","","",""]  # 0: chat_id, 1: user_id, 2: nome, 3: tipocarburante, 4: capacita, 5: maxkm

def main():
    print("Inizio")
    connection = database_connection("","root","","db_benzinaio")

    text = ""
    last_update_id = 0
    
    while True:
        method = "getUpdates"
        response = sendMessage(method, {'offset': last_update_id})
        data = response
        print(data)
        if len(data['result']) > 0:
            last_update_id = data['result'][0]['update_id'] + 1
            text = data['result'][0]['message']['text']
            args[0] = data['result'][0]['message']['chat']['id']
            args[1] = data['result'][0]['message']['from']['id']
            
        if text == '/start':
            startChat(last_update_id)
        
        if len(data['result']) > 0:
            last_update_id = data['result'][0]['update_id'] + 1

        sleep(5)

def startChat(last_update_id):
    sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Ciao, benvenuto nel bot benzinaio!'})
    data = sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Inserisci il tuo nome: '})
    sleep(5)
    data = sendMessage("getUpdates", {'offset': last_update_id})
    last_update_id = data['result'][0]['update_id'] + 1
    args[2] = data['result'][0]['message']['text']
    
    data = sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Inserisci il tipo di carburante del tuo veicolo: '})
    sleep(5)
    data = sendMessage("getUpdates", {'offset': last_update_id})
    last_update_id = data['result'][0]['update_id'] + 1
    args[3] = data['result'][0]['message']['text']
    
    data = sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Inserisci la capacita del serbatoio: '})
    sleep(5)
    data = sendMessage("getUpdates", {'offset': last_update_id})
    last_update_id = data['result'][0]['update_id'] + 1
    args[4] = data['result'][0]['message']['text']
    
    data = sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Inserisci i km massimi che percorreresti: '})
    sleep(5)
    data = sendMessage("getUpdates", {'offset': last_update_id})
    last_update_id = data['result'][0]['update_id'] + 1
    args[5] = data['result'][0]['message']['text']
    
    
    print(args)
    #controllo che la chat non esista nel db
    #se esiste prendo i dati e li salvo in args
    #se non esiste la creo

def sendMessage(method, parametri):
    url = ENDPOINT + method
    response = requests.get(url, params=parametri)
    return response.json()


def database_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")


if __name__ == '__main__':
    main()
