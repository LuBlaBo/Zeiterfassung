##############################
# SQLITE fuer die Stechuhr   #
##############################
import sqlite3
from typing import List
import configparser
import random, string

#################
#               #
#    CONFIG     #
#               #
#################
configparser = configparser.RawConfigParser()
configFilePath = r'conf/app.conf'
configparser.read(configFilePath)

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


db = configparser.get('ServerSettings', 'db')

verbindung = sqlite3.connect("./conf/testdb.sqlite")
cursor = verbindung.cursor()
befehle: List[str] = []

############ SQL-Section ############

print(
    "SQL-Tool zur Zeiterfassung"
    "\n"
    "Vorsicht bei der Anwendung!"
)

print(
    "\n"
    "Bitte Auswahl treffen \n"
    "1 - Neuen Benutzer  \n"
    "2 - Datenbank aufsetzen \n"
    "q - Beenden \n"
)
while True:
    eingabe = input("Auswahl eingeben: ")
    print(eingabe)
    if (eingabe == "1"):
        print("Neuen Benutzer anlegen")
        id_mitarbeiter = "NULL"
        name = input("Name eingeben: ")
        nachname = input("Nachname eingaben: ")
        raum = input("Raum eingeben: ")
        raum = str(raum)
        position = input("Position eingaben: ")
        position = str(position)

        random_id = randomword(5)
        cursor.execute('INSERT INTO mitarbeiter VALUES ('"?"', '"?"', '"?"', '"?"', '"?"', 0)', (random_id, name, nachname,
                                                                                   raum, position))
        verbindung.commit()
    elif (eingabe == "2"):
        #Tabelle Anwesenheit erstellen (Array id:0)
        befehle.append('''CREATE TABLE IF NOT EXISTS anwesenheit (
        	id_anwesenheit INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        	id_mitarbeiter TEXT NOT NULL,
        	datum TEXT NOT NULL,
        	time_in TEXT NOT NULL,
        	time_out TEXT,
        	raum TEXT)
        	''')

        #Tabelle Status erstellen (Array id:1)
        befehle.append('''CREATE TABLE IF NOT EXISTS mitarbeiter (
        	id_mitarbeiter TEXT NOT NULL PRIMARY KEY,
        	name TEXT NOT NULL,
        	nachname TEXT NOT NULL,
        	raum TEXT,
        	position TEXT,
        	status BOOL NOT NULL)
        	''')

        cursor.execute(befehle[0])
        cursor.execute(befehle[1])
        verbindung.commit()
        cursor.close()
    elif (eingabe == "q"):
        cursor.close()
        break
    else:
        print("Fehler bei der Eingabe. Bitte erneut versuchen")