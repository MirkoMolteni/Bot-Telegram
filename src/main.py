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
    #controllo che la chat non esista nel db
    query = "SELECT * FROM chat WHERE id = " + str(args[0])
    result = execute_query(query)
    if(len(result)==0):
        #se non esiste la creo
        sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Ciao, benvenuto nel bot benzinaio!'})
        data = sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Inserisci il tuo nome: '})
        sleep(5)
        data = sendMessage("getUpdates", {'offset': last_update_id})
        # last_update_id = data['result'][0]['update_id'] + 1
        last_update_id = last_update_id + 1
        args[2] = data['result'][0]['message']['text']
        
        data = sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Inserisci il tipo di carburante del tuo veicolo: '})
        sleep(5)
        data = sendMessage("getUpdates", {'offset': last_update_id})
        last_update_id = last_update_id + 1
        args[3] = data['result'][0]['message']['text']
        
        data = sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Inserisci la capacita del serbatoio: '})
        sleep(5)
        data = sendMessage("getUpdates", {'offset': last_update_id})
        last_update_id = last_update_id + 1
        args[4] = data['result'][0]['message']['text']
        
        data = sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Inserisci i km massimi che percorreresti: '})
        sleep(5)
        data = sendMessage("getUpdates", {'offset': last_update_id})
        last_update_id = last_update_id + 1
        args[5] = data['result'][0]['message']['text']
        print(args)
        
        query = "INSERT INTO user (id, nome, tipocarburante, capacita, maxkm) VALUES (" + str(args[1]) + ", '" + str(args[2]) + "', '" + str(args[3]) + "', " + str(args[4]) + ", " + str(args[5]) + ")"
        execute_query(query)
        query = "INSERT INTO chat (id, user_id) VALUES (" + str(args[0]) + ", " + str(args[1]) + ")"
        execute_query(query)
    else:
        #se esiste prendo i dati e li salvo in args
        userid = result[0][1]
        query = "SELECT * FROM user WHERE id = " + str(userid)
        result = execute_query(query)
        args[1] = result[0][0]
        args[2] = result[0][1]
        args[3] = result[0][2]
        args[4] = result[0][3]
        args[5] = result[0][4]
        sendMessage("sendMessage", {'chat_id': args[0], 'text': 'Ciao ' + str(args[2]) + '!'})

def sendMessage(method, parametri):
    url = ENDPOINT + method
    response = requests.get(url, params=parametri)
    return response.json()

def connect_to_database():
    try:
        myDB = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_benzinaio"
        )
        if myDB.is_connected():
            print("Connessione al database avvenuta con successo.")
            return myDB
    except Error as e:
        print("Errore durante la connessione al database:", e)
        return None

def execute_query(query):
    try:
        myDB = connect_to_database()
        if myDB is not None:
            print("Query:", query)
            cursor = myDB.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            print("Risultato della query:", result)
            myDB.commit()
            return result
        else:
            print("Errore durante l'esecuzione della query")
            return None
    except Error as e:
        print("Errore: ", e)
        return None
    finally:
        if myDB is not None and myDB.is_connected():
            cursor.close()
            myDB.close()
            print("Database connection closed.")


if __name__ == '__main__':
    main()
