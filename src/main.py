import requests
from time import sleep
from bot import Bot
from database import Database

ENDPOINT = f'https://api.telegram.org/bot{open("./docs/token_bot.txt", "r").read()}/'
bot = Bot(open("./docs/token_bot.txt", "r").read())
db = Database("localhost", "root", "", "db_benzinaio")
last_update_id = 0
args = ["","","","","",""]  # 0: chat_id, 1: user_id, 2: nome, 3: tipocarburante, 4: capacita, 5: maxkm

def main():
    print("Inizio")

    text = ""
    start_executed = False
    
    # loadPrezzi()
    
    while True:
        global last_update_id
        
        response = bot.get_updates(last_update_id)
        print(response)
        
        if len(response['result']) > 0:
            last_update_id = response['result'][0]['update_id'] + 1
            text = response['result'][0]['message']['text']
            args[0] = response['result'][0]['message']['chat']['id']
            args[1] = response['result'][0]['message']['from']['id']
            
        if text == '/start' and not start_executed:
            startChat()
            start_executed = True
        elif text == '/find':
            cercaBenzinaio()
            
        
        if len(response['result']) > 0:
            last_update_id = response['result'][0]['update_id'] + 1

        sleep(5)

def cercaBenzinaio():
    global args
    print(args)

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

def loadPrezzi():
    print("Caricamento prezzi...")
    
    db.esegui_query("DELETE FROM prezzi")
    # db.esegui_query("DELETE FROM anagrafica")
    
    # anagrafica = "https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"
    # r = requests.get(anagrafica)
    # with open("./docs/Csv/anagrafica.csv", "wb") as f:
    #     f.write(r.content)       
    # anagrafica = r.content.decode("utf-8").split("\n")
    # anagrafica.pop(0)
    # anagrafica.pop(0)
    # anagrafica.pop(len(anagrafica)-1)
    
    # for i in range(len(anagrafica)):
    #     anagrafica[i] = anagrafica[i].replace('NULL','').replace("'"," ").split(";")
        
    #     query = ""
    #     if len(anagrafica[i]) == 10:
    #         query = "INSERT INTO anagrafica (ID, Gestore, Bandiera, Tipo, Nome, Indirizzo, Comune, Provincia, Latitudine, Longitudine) VALUES (" + str(anagrafica[i][0]) + ", '" + str(anagrafica[i][1]) + "', '" + str(anagrafica[i][2]) + "', '" + str(anagrafica[i][3]) + "', '" + str(anagrafica[i][4]) + "', '" + str(anagrafica[i][5]) + "', '" + str(anagrafica[i][6]) + "', '" + str(anagrafica[i][7]) + "', " + str(anagrafica[i][8]) + ", " + str(anagrafica[i][9]) + ")"
    #     else:
    #         query = "INSERT INTO anagrafica (ID, Gestore, Bandiera, Tipo, Nome, Indirizzo, Comune, Provincia, Latitudine, Longitudine) VALUES (" + str(anagrafica[i][0]) + ", '" + str(anagrafica[i][1]) + "', '" + str(anagrafica[i][2]) + "', '" + str(anagrafica[i][3]) + "', '" + str(anagrafica[i][4]) + "', '" + str(anagrafica[i][5]) + " " +  str(anagrafica[i][6]) + "', '" + str(anagrafica[i][7]) + "', '" + str(anagrafica[i][8]) + "', " + str(anagrafica[i][9]) + ", " + str(anagrafica[i][10]) + ")"
        
    #     db.esegui_query(query)       
    
    prezzi = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
    r = requests.get(prezzi)
    with open("./docs/Csv/prezzi.csv", "wb") as f:
        f.write(r.content)
    prezzi = r.content.decode("utf-8").split("\n")
    prezzi.pop(0)
    prezzi.pop(0)
    prezzi.pop(len(prezzi)-1)
    
    for i in range(len(prezzi)):
        prezzi[i] = prezzi[i].replace('NULL','').replace("'","").split(";")
        query = "INSERT INTO prezzi (IDImpianto, TipoCarburante, Prezzo, IsSelf, DtComu) VALUES (" + str(prezzi[i][0]) + ", '" + str(prezzi[i][1]) + "', " + str(prezzi[i][2]) + ", " + str(prezzi[i][3]) + ", '" + str(prezzi[i][4]) + "')"
        db.esegui_query(query)
    
    print("Prezzi caricati")

if __name__ == '__main__':
    main()
