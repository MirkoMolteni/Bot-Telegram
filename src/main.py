import requests
from time import sleep
from bot import Bot
from database import Database

ENDPOINT = f'https://api.telegram.org/bot{open("./docs/token_bot.txt", "r").read()}/'

bot = Bot(open("./docs/token_bot.txt", "r").read())
db = Database("localhost", "root", "", "db_benzinaio")

last_update_id = 0
args = ["","","","","",""]  # 0: chat_id, 1: user_id, 2: nome, 3: tipocarburante, 4: capacita, 5: maxkm
start_executed = False
def main():
    print("Inizio")

    text = ""
    global start_executed
    
    while True:
        global last_update_id
        response = bot.get_updates(last_update_id)
        print(response)
        #TODO: non loopare lo start
        if len(response['result']) > 0:
            last_update_id = response['result'][0]['update_id'] + 1
            text = response['result'][0]['message']['text']
            args[0] = response['result'][0]['message']['chat']['id']
            args[1] = response['result'][0]['message']['from']['id']
            
        if text == '/start' and not start_executed:
            startChat()
            start_executed = True
            
        
        if len(response['result']) > 0:
            last_update_id = response['result'][0]['update_id'] + 1

        sleep(5)

def startChat():
    global last_update_id
    global args
    query = "SELECT * FROM chat WHERE id = " + str(args[0])
    result = db.esegui_query(query)
    #controllo che la chat non esista nel db
    if(len(result)==0):
        #se non esiste la creo
        bot.send_message(args[0], 'Per prima cosa inserisci i tuoi dati')
        bot.send_message(args[0], 'Inserisci il tuo nome: ')
        sleep(5)
        data = bot.get_updates(last_update_id)
        last_update_id = last_update_id + 1
        args[2] = data['result'][0]['message']['text']
        
        bot.send_message(args[0], 'Inserisci il tipo di carburante del tuo veicolo: ')
        sleep(5)
        data = bot.get_updates(last_update_id)
        last_update_id = last_update_id + 1
        args[3] = data['result'][0]['message']['text']
        
        bot.send_message(args[0], 'Inserisci la capacita del serbatoio: ')
        sleep(5)
        data = bot.get_updates(last_update_id)
        last_update_id = last_update_id + 1
        args[4] = data['result'][0]['message']['text']
        
        bot.send_message(args[0], 'Inserisci i km massimi che percorreresti: ')
        sleep(5)
        data = bot.get_updates(last_update_id)
        last_update_id = last_update_id + 1
        args[5] = data['result'][0]['message']['text']
        print(args)
        
        query = "INSERT INTO user (id, nome, tipocarburante, capacita, maxkm) VALUES (" + str(args[1]) + ", '" + str(args[2]) + "', '" + str(args[3]) + "', " + str(args[4]) + ", " + str(args[5]) + ")"
        db.esegui_query(query)
        query = "INSERT INTO chat (id, user_id) VALUES (" + str(args[0]) + ", " + str(args[1]) + ")"
        db.esegui_query(query)
    else:
        #se esiste prendo i dati e li salvo in args
        userid = result[0][1]
        query = "SELECT * FROM user WHERE id = " + str(userid)
        result = db.esegui_query(query)
        args[1] = result[0][0]
        args[2] = result[0][1]
        args[3] = result[0][2]
        args[4] = result[0][3]
        args[5] = result[0][4]
        bot.send_message(args[0], 'Bentornato ' + str(args[2]) + '!')
        print(args)


if __name__ == '__main__':
    main()
