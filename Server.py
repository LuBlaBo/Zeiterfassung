version = "0.0.2"


import time
import bottle
from bottle import route, static_file, template, run, view, request
import sqlite3
import configparser
import csv
import random, string

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


#################
#               #
#    CONFIG     #
#               #
#################
configparser = configparser.RawConfigParser()
configFilePath = r'conf/app.conf'
configparser.read(configFilePath)


host = configparser.get('ServerSettings', 'host')
port = configparser.get('ServerSettings', 'port')
autoreload = configparser.get('ServerSettings', 'autoreload')
debug = configparser.get('ServerSettings', 'debug')
db = configparser.get('ServerSettings', 'db')


conn = sqlite3.connect(db)
c = conn.cursor()
conn.commit()


# Main Webseite
@route('/', method=['GET'])
def index():
    uhrzeit = time.strftime(" " + "%H:%M:%S")
    ids = []
    ids_name = []
    ids_nachname = []
    ids_status = []

    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = "SELECT id_mitarbeiter, name, nachname, status FROM mitarbeiter"
    c.execute(sql)
    dbout = (c.fetchall())
    for row in dbout:
        ids.append(row[0])
        ids_name.append(row[1])
        ids_nachname.append(row[2])
        conv3 = str(row[3])
        ids_status.append(conv3)

    c.close()
    dis_ids = ("\n".join(ids))
    dis_ids_name = ("\n".join(ids_name))
    dis_ids_nachname = ("\n".join(ids_nachname))
    dis_ids_status = ("\n".join(ids_status))

    return template("index.html", uhrzeit=uhrzeit, version=version, dis_ids=dis_ids, dis_ids_name=dis_ids_name,
                    dis_ids_nachname=dis_ids_nachname, dis_ids_status=dis_ids_status)


@route('/app/checkin.html', method=['GET', 'POST'])
def checkin():
    uhrzeit = time.strftime(" " + "%H:%M:%S")
    datum = time.strftime(" " + "%d.%m.%Y")
    checkin_id = bottle.request.params.get("in_id", default="NULL")
    print(checkin_id)
    msg = ""
    if checkin_id == "NULL":
        pass
    elif checkin_id == "":
        pass
    elif "'" in checkin_id:
        msg = "Zeichen nicht zulässig!"
    elif len(checkin_id) < 5:
        msg = "ID zu kurz!"
    else:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("UPDATE mitarbeiter SET ""status""=1 WHERE id_mitarbeiter=" + "'" + checkin_id + "'")
        c.execute('INSERT INTO anwesenheit VALUES (NULL, '"?"', '"?"', '"?"', "Noch anwesend...", 0)', (checkin_id, datum, uhrzeit,))
        conn.commit()
        c.close()
        msg = "Erfolgreich eingetragen! Zeitstempel -->" + datum + uhrzeit
    return template("./app/checkin.html", uhrzeit=uhrzeit, version=version, msg=msg)


@route('/app/checkout.html', method=['GET', 'POST'])
def checkout():
    uhrzeit = time.strftime(" " + "%H:%M:%S")
    datum = time.strftime(" " + "%d.%m.%Y")
    checkout_id = bottle.request.params.get("out_id", default="NULL")
    msg = ""
    if checkout_id == "NULL":
        pass
    elif checkout_id == "":
        pass
    elif "'" in checkout_id:
        msg = "Zeichen nicht zulässig!"
    else:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("UPDATE mitarbeiter SET ""status""=0 WHERE id_mitarbeiter=" + "'" + checkout_id + "'")
        c.execute("UPDATE anwesenheit SET ""time_out""=" + "'" + uhrzeit + "' WHERE id_mitarbeiter=" + "'" + checkout_id + "'"" AND datum=" + "'" + datum + "'")
        conn.commit()
        c.close()
        msg = "Erfolgreich ausgetragen! Zeitstempel -->" + datum + uhrzeit
    return template("./app/checkout.html", uhrzeit=uhrzeit, version=version, msg=msg)


@route('/app/export.html', method=['GET', 'POST'])
def export():
    uhrzeit = time.strftime("%H:%M:%S")
    datum = time.strftime("%d.%m.%Y")
    export = bottle.request.params.get("export", default="false")


    # Array neu erzeugen (leer)
    id_anwesenheit = []
    id_mitarbeiter = []
    time_datum = []
    time_kommen = []
    time_gehen = []


    random_id = randomword(5)
    # Datenbank verbinden
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM anwesenheit")
    dbout = (c.fetchall())
    for row in dbout:
        convrow0 = str(row[0])
        id_anwesenheit.append(convrow0)
        id_mitarbeiter.append(row[1])
        time_datum.append((row[2]))
        time_kommen.append(row[3])
        time_gehen.append(row[4])
    dis_id_anwesenheit = ("\n".join(id_anwesenheit))
    dis_id_mitarbeiter = ("\n".join(id_mitarbeiter))
    dis_time_datum = ("\n".join(time_datum))
    dis_time_kommen = ("\n".join(time_kommen))
    dis_time_gehen = ("\n".join(time_gehen))


    if export == "true":
        csvWriter = csv.writer(open("app/src/export/" + datum + "_" + "export.csv", "w"))
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT * FROM anwesenheit")
        rows = c.fetchall()
        for row in rows:
            csvWriter.writerows([row])
    else:
        pass
    c.close()


    return template("./app/export.html", uhrzeit=uhrzeit, datum=datum, version=version, dis_id_anwesenheit=dis_id_anwesenheit,
                    dis_id_mitarbeiter=dis_id_mitarbeiter, dis_time_datum=dis_time_datum,
                    dis_time_kommen=dis_time_kommen,
                    dis_time_gehen=dis_time_gehen)


@route('/app/src/:filename#.*#')
def static(filename):
    return static_file(filename, root='./app/src')


run(host=host, port=port, reloader=autoreload, debug=debug)
