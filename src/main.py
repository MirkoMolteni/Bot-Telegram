import requests
from bot import Bot
from database import Database
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from time import sleep
import json

ENDPOINT = f'https://api.telegram.org/bot{open("./docs/token_bot.txt", "r").read()}/'
bot = Bot(open("./docs/token_bot.txt", "r").read())
db = Database("localhost", "root", "", "db_benzinaio")
last_update_id = 0
args = ["","","","","",""]  # 0: chat_id, 1: user_id, 2: nome, 3: tipocarburante, 4: capacita, 5: maxkm

def main():
    print("Inizio")

    text = ""
    start_executed = False
    find_executed = False
    
    # loadPrezzi()
    
    while True:
        global last_update_id
        
        text=""
        
        response = bot.get_updates(last_update_id)
        print(response)
        
        if len(response['result']) > 0:
            last_update_id = response['result'][0]['update_id'] + 1
            try:
                text = response['result'][0]['message']['text']
            except:
                text = ""
            args[0] = response['result'][0]['message']['chat']['id']
            args[1] = response['result'][0]['message']['from']['id']
            
        if text == '/start' and not start_executed:
            startChat()
            start_executed = True
        elif text == '/redefine' and start_executed:
            redefine()
        elif text == '/find' and start_executed and not find_executed:
            cercaBenzinaio()
            find_executed = True
        elif text == '/test':
            test()
            
        
        if len(response['result']) > 0:
            last_update_id = response['result'][0]['update_id'] + 1

        sleep(5)
        
def test():
    print("Test")

def redefine():
    #UPDATE `user` SET `id` = '46153681', `Nome` = 'Mirk', `TipoCarburante` = 'Benzin', `Capacita` = '50', `MaxKM` = '3' WHERE `user`.`id` = 461536811
    global args
    global last_update_id
    
    domandeInizio()
    
    query = "UPDATE user SET Nome = '" + str(args[2]) + "', TipoCarburante = '" + str(args[3]) + "', Capacita = " + str(args[4]) + ", MaxKM = " + str(args[5]) + " WHERE id = " + str(args[1])
    db.esegui_query(query)
    
def getRisposta():
    global last_update_id
    while True:
        sleep(5)
        data = bot.get_updates(last_update_id)
        if len(data['result']) > 0:
            last_update_id = last_update_id + 1
            return data

def cercaBenzinaio():
    global args
    global last_update_id
    
    bot.send_message(args[0], 'Inserisci la tua posizione: ')

    data = getRisposta()
    myLat = data['result'][0]['message']['location']['latitude']
    myLon = data['result'][0]['message']['location']['longitude']

    bot.send_message(args[0], 'Distributore più vicino o distributore più economico? (vicino/economico)')
    sendKeyboard(args[0], ['Vicino', 'Economico'])
    data = getRisposta()
    tipoBenzinaio = data['result'][0]['message']['text'].lower()
    
    bot.send_message(args[0], 'Quanta benzina vuoi? (1/4, 2/4, 3/4, 4/4))')
    sendKeyboard(args[0], ['1/4', '2/4', '3/4', '4/4'])
    data = getRisposta()
    quantita = data['result'][0]['message']['text']
    
    if tipoBenzinaio == 'vicino':
        query = "SELECT * FROM anagrafica ORDER BY SQRT(POW(Latitudine - " + str(myLat) + ", 2) + POW(Longitudine - " + str(myLon) + ", 2)) ASC LIMIT 1"
        result = db.esegui_query(query)
        bot.send_message(args[0], 'Il distributore più vicino è: ' + str(result[0][4]) + ' ' + str(result[0][5]) + ', ' + str(result[0][6]) + ', ' + str(result[0][7]) + ', ' + str(result[0][8]))
    elif tipoBenzinaio == 'economico':
        #TODO: utilizzare anche il raggio
        query = f"""SELECT a.*, p.prezzo 
                FROM anagrafica as a 
                JOIN prezzi as p ON a.ID = p.IDImpianto
                WHERE p.TipoCarburante = '{args[3]}'""";
        result = db.esegui_query(query)
        valid = []
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        }
        maxKm = args[5]
        for i in range(len(result)):
            latBenzinaio = result[i][8]
            lonBenzinaio = result[i][9]
            call = requests.get(f'https://api.openrouteservice.org/v2/directions/driving-car?api_key={open("./docs/token_directions.txt", "r").read()}&start={myLon},{myLat}&end={lonBenzinaio},{latBenzinaio}', headers=headers).json()
            if call['features'][0]['properties']['summary']['distance'] < maxKm:
                valid.append(result[i])
            
        
        
        bot.send_message(args[0], 'Il distributore più economico è: ' + str(result[0][4]) + ' ' + str(result[0][5]) + ', ' + str(result[0][6]) + ', ' + str(result[0][7]) + ', ' + str(result[0][8]))
    
def startChat():
    global last_update_id
    global args
    query = "SELECT * FROM chat WHERE id = " + str(args[0])
    result = db.esegui_query(query)
    #controllo che la chat non esista nel db
    if(len(result)==0):
        bot.send_message(args[0], 'Ciao! Benvenuto sul bot benzinaio!')
        #se non esiste la creo
        domandeInizio()
        
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
        
def domandeInizio():
    global args
    global last_update_id
    
    bot.send_message(args[0], 'Per prima cosa inserisci i tuoi dati')
    bot.send_message(args[0], 'Inserisci il tuo nome: ')
    data = getRisposta()
    args[2] = data['result'][0]['message']['text']
    
    bot.send_message(args[0], 'Inserisci il tipo di carburante del tuo veicolo: ')
    data = getRisposta()
    args[3] = data['result'][0]['message']['text']
    
    bot.send_message(args[0], 'Inserisci la capacita del serbatoio: ')
    data = getRisposta()
    args[4] = data['result'][0]['message']['text']
    
    bot.send_message(args[0], 'Inserisci i km massimi che percorreresti: ')
    data = getRisposta()
    args[5] = data['result'][0]['message']['text']

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

def sendKeyboard(chat_id, options):
        url = f"{ENDPOINT}sendMessage"
        keyboard = {
            "keyboard": [[{"text": option} for option in options]],
            "resize_keyboard": True, 
            "one_time_keyboard": True
        }
        payload = {
            "chat_id": chat_id,
            "text": "Seleziona un opzione",
            "reply_markup": json.dumps(keyboard)
        }
        requests.post(url, data=payload)


if __name__ == '__main__':
    main()
