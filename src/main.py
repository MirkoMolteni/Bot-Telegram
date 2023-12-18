import requests
from time import sleep
import mysql.connector
from mysql.connector import Error
import pandas as pd
ENDPOINT = f'https://api.telegram.org/bot{
    open("./docs/token_bot.txt", "r").read()}/'


def main():
    print("Inizio")

    last_update_id = 0
    wait_mex = True
    method = "sendMessage"
    parametri = {'chat_id': chat_id, 'text': 'Hai inviato ' + text}
    response = sendMessage(method, parametri)
    while True:
        if wait_mex:
            method = "getUpdates"
            response = sendMessage(method, {'offset': last_update_id})
            data = response.json()
            print(data)

        if len(data['result']) > 0:
            last_update_id = data['result'][0]['update_id'] + 1

        sleep(5)


def sendMessage(method, parametri):
    url = ENDPOINT + method
    response = requests.get(url, params=parametri)
    return response


def create_db_connection(host_name, user_name, user_password, db_name):
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
