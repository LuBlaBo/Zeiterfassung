##############################
# SQLITE fuer die Stechuhr   #
##############################

import sqlite3
from time import strftime
from typing import List

verbindung = sqlite3.connect("./Timedb.db")
cursor = verbindung.cursor()

############ SQL-Section ############

befehle: List[str] = []

#Tabelle Anwesenheit erstellen (Array id:0)
befehle.append('''CREATE TABLE IF NOT EXISTS Anwesenheit (
	id_anwesenheit INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	id_mitarbeiter CHAR NOT NULL,
	time_kommen TEXT NOT NULL,
	time_gehen TEXT)
	''')

#Tabelle Status erstellen (Array id:1)
befehle.append('''CREATE TABLE IF NOT EXISTS Status (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	id_mitarbeiter CHAR NOT NULL,
	status BOOL NOT NULL)
	''')

cursor.execute(befehle[0])
cursor.execute(befehle[1])
verbindung.commit()
