import time
import bottle
from bottle import route, static_file, template, run, view, request
import sqlite3

version = "0.0.1"
uhrzeit = time.strftime(" " + "%H:%M:%S")
datum = time.strftime(" " + "%d.%m.%Y")


# Main Webseite
@route('/', method=['GET'])
def index():
    # Array neu erzeugen (leer)
    id_anwesenheit = []
    id_mitarbeiter = []
    time_kommen = []
    time_gehen = []

    # Datenbank verbinden
    conn = sqlite3.connect('Timedb.sqlite')
    c = conn.cursor()
    sql = "SELECT * FROM Anwesenheit ORDER BY id_anwesenheit ASC"
    c.execute(sql)
    dbout = (c.fetchall())
    for row in dbout:
        convrow0 = str(row[0])
        id_anwesenheit.append(convrow0)
        id_mitarbeiter.append(row[1])
        time_kommen.append(row[2])
        time_gehen.append(row[3])
    c.close()
    dis_id_anwesenheit = ("\n".join(id_anwesenheit))
    dis_id_mitarbeiter = ("\n".join(id_mitarbeiter))
    dis_time_kommen = ("\n".join(time_kommen))
    dis_time_gehen = ("\n".join(time_gehen))



    ids = []
    ids_mitarbeiter = []
    ids_status = []


    conn = sqlite3.connect('Timedb.sqlite')
    c = conn.cursor()
    sql = "SELECT * FROM Status"
    c.execute(sql)
    dbout = (c.fetchall())
    for row in dbout:
        convrow1 = str(row[0])
        ids.append(convrow1)
        ids_mitarbeiter.append(row[1])
        convrow2 = str(row[2])
        ids_status.append(convrow2)
    c.close()
    dis_ids_mitarbeiter = ("\n".join(ids_mitarbeiter))
    dis_ids_status = ("\n".join(ids_status))

    return template("index.html", uhrzeit=uhrzeit, version=version, dis_id_anwesenheit=dis_id_anwesenheit,
                    dis_id_mitarbeiter=dis_id_mitarbeiter, dis_time_kommen=dis_time_kommen,
                    dis_time_gehen=dis_time_gehen, dis_ids_mitarbeiter=dis_ids_mitarbeiter, dis_ids_status=dis_ids_status)


@route('/app/checkin.html', method=['GET', 'POST'])
def checkin():
    checkin_id = bottle.request.params.get("in_id", default="NULL")
    print(checkin_id)
    msg = ""
    msg = "Erfolgreich eingetragen! Zeitstempel -->" + datum + uhrzeit
    if checkin_id == "NULL":
        pass
    elif checkin_id == "":
        pass
    else:
        conn = sqlite3.connect('Timedb.sqlite')
        c = conn.cursor()
        sql = ("UPDATE Status SET ""status""=1 WHERE id_mitarbeiter=" +"'" + checkin_id +"'")
        print(sql)
        c.execute(sql)
        conn.commit()
        c.close()
    return template("./app/checkin.html", uhrzeit=uhrzeit, version=version, msg=msg)


@route('/app/checkout.html', method=['GET', 'POST'])
def checkout():
    checkout_id = bottle.request.params.get("out_id", default="NULL")
    print(checkout_id)
    msg = ""
    msg = "Erfolgreich ausgetragen! Zeitstempel -->" + datum + uhrzeit
    if checkout_id == "NULL":
        pass
    elif checkout_id == "":
        pass
    else:
        conn = sqlite3.connect('Timedb.sqlite')
        c = conn.cursor()
        sql = ("UPDATE Status SET ""status""=0 WHERE id_mitarbeiter=" +"'" + checkout_id +"'")
        print(sql)
        c.execute(sql)
        conn.commit()
        c.close()
    return template("./app/checkout.html", uhrzeit=uhrzeit, version=version, msg=msg)


@route('/app/src/:filename#.*#')
def static(filename):
    return static_file(filename, root='./app/src')


run(host="0.0.0.0", port=8080, reloader=True, debug=True)
