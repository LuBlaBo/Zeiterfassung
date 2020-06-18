import time
from bottle import route, static_file, template, run, view, request
import sqlite3

version = "0.0.1"
uhrzeit = time.strftime("%H:%M:%S")



@route(['/', 'GET'])
@view('')
def index():

    #Array neu erzeugen (leer)
    id_anwesenheit = []
    id_mitarbeiter = []
    time_kommen = []
    time_gehen = []

    #Datenbank verbinden
    conn = sqlite3.connect('Timedb.db')
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
    print("\n")
    print("----------")

    dis_id_anwesenheit = ("\n".join(id_anwesenheit))
    dis_id_mitarbeiter = ("\n".join(id_mitarbeiter))
    dis_time_kommen = ("\n".join(time_kommen))
    dis_time_gehen =  ("\n".join(time_gehen))

    return template("index", uhrzeit=uhrzeit, version=version, dis_id_anwesenheit=dis_id_anwesenheit,
                    dis_id_mitarbeiter=dis_id_mitarbeiter, dis_time_kommen=dis_time_kommen,
                    dis_time_gehen=dis_time_gehen)


@route('/src/:filename#.*#')
def static(filename):
    return static_file(filename, root='./app/src')


run(host="0.0.0.0", port=8080, reloader=True)
