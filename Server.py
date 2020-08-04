import bottle
from bottle import route, static_file, template, run, request
import sqlite3
import configparser
import csv
import time
import smtplib
from email.mime.text import MIMEText

version = "0.0.2"
banner = ("""

  ___ ___ _ _____ ___ ___ ___ __    __   __  _  _ __  _  __  
 |_  | __| |_   _| __| _ \ __/  \ /' _//' _/| || |  \| |/ _] 
  / /| _|| | | | | _|| v / _| /\ |`._`.`._`.| \/ | | ' | [/\ 
 |___|___|_| |_| |___|_|_\_||_||_||___/|___/ \__/|_|\__|\__/ 

      """)

print(banner + "\n" + "Version: " + version)


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

mailer_enabled = configparser.get('MailSettings', 'enabled')
server = configparser.get('MailSettings', 'server')
mport = configparser.get('MailSettings', 'mport')
user = configparser.get('MailSettings', 'user')
password = configparser.get('MailSettings', 'password')
sender = configparser.get('MailSettings', 'sender')
receiver = configparser.get('MailSettings', 'receiver')


def mail(subject, message):
    """
    Mail module for sending mails via STARTTLS. Adopts "subject" and "message" to send mails in html form.
    :param subject:
    :param message:
    :return:
    """
    if mailer_enabled == "true":
        html = open("conf/mail.html", "r")
        html = html.read()
        html = html.format(message)

        msg = MIMEText(html, 'html')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver

        with smtplib.SMTP(server, mport) as mserver:
            mserver.starttls()  # Secure the connection
            mserver.login(user, password)
            mserver.sendmail(sender, receiver, msg.as_string())
            print("Mail successfully sent")
    else:
        print("Mailer disabled")


def sql_get_user(mitarbeiter_id):
    """
    SQL module for compiling user information. Name, Surname [and Mail Address]
    :param mitarbeiter_id:
    :return:
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT name, nachname FROM mitarbeiter WHERE id_mitarbeiter=?", (mitarbeiter_id,))
    mailuser = c.fetchall()
    c.close()
    for row in mailuser:
        dictmailuser = [row[0], row[1]]
        namenachname = (dictmailuser[0] + " " + dictmailuser[1])

        return namenachname


def export_csv():
    """
    Function to generate CSV-File with Checkin / Checkout values
    :return:
    """
    csvwriter = csv.writer(open("app/src/export/" + datum() + "_" + "export.csv", "w"))
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM anwesenheit")
    rows = c.fetchall()
    for row in rows:
        csvwriter.writerows([row])


def uhrzeit():
    uhrzeit = time.strftime("%H:%M:%S")

    return uhrzeit


def datum():
    datum = time.strftime("%d.%m.%Y")

    return datum


# Main Webseite
@route('/', method=['GET'])
def index():
    """
    Main website
    :return:
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT id_mitarbeiter, name, nachname, status FROM mitarbeiter")
    dbout = c.fetchall()
    c.close()

    return template("index.html", uhrzeit=uhrzeit(), version=version,
                    dis_rows=dbout)


@route('/app/checkin.html', method=['GET', 'POST'])
def checkin():
    checkin_id = bottle.request.params.get("in_id", default="NULL")
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
        c.execute("UPDATE mitarbeiter SET status=1 WHERE id_mitarbeiter=?", (checkin_id,))
        c.execute("INSERT INTO anwesenheit VALUES (NULL, ?, ?, ?, 'Noch anwesend...', 0)",
                  (checkin_id, datum(), uhrzeit(),))
        conn.commit()
        c.close()
        msg = "Hallo {0}! Erfolgreich eingetragen... Zeitstempel --> {1} {2}".format(sql_get_user(checkin_id), datum(),
                                                                                     uhrzeit())
        mail("Zeiterfassung - Checkin", msg)

    return template("./app/checkin.html", uhrzeit=uhrzeit(), version=version, msg=msg)


@route('/app/checkout.html', method=['GET', 'POST'])
def checkout():
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
        c.execute("UPDATE mitarbeiter SET status=0 WHERE id_mitarbeiter=?", (checkout_id,))
        c.execute("UPDATE anwesenheit SET time_out=? WHERE id_mitarbeiter=? AND datum=?",
                  (uhrzeit(), checkout_id, datum(),))
        conn.commit()
        c.close()
        msg = "Hallo {0}! Erfolgreich ausgetragen... Zeitstempel --> {1} {2}".format(sql_get_user(checkout_id), datum(),
                                                                                     uhrzeit())
        print(msg)
        mail("Zeiterfassung - Checkout", msg)
    return template("./app/checkout.html", uhrzeit=uhrzeit(), version=version, msg=msg)


@route('/app/export.html', method=['GET', 'POST'])
def export():
    export = bottle.request.params.get("export", default="false")

    # Array neu erzeugen (leer)
    id_anwesenheit = []
    id_mitarbeiter = []
    time_datum = []
    time_kommen = []
    time_gehen = []

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
        export_csv()
    else:
        pass
    c.close()

    return template("./app/export.html", uhrzeit=uhrzeit(), datum=datum(), version=version,
                    dis_id_anwesenheit=dis_id_anwesenheit,
                    dis_id_mitarbeiter=dis_id_mitarbeiter, dis_time_datum=dis_time_datum,
                    dis_time_kommen=dis_time_kommen,
                    dis_time_gehen=dis_time_gehen)


@route('/app/src/:filename#.*#')
def static(filename):
    return static_file(filename, root='./app/src')


@bottle.get('/api')
def api():
    mitarbeiter_id = request.query.id
    uhrzeit = time.strftime("%H:%M:%S")
    datum = time.strftime("%d.%m.%Y")

    if len(mitarbeiter_id) < 5 or len(mitarbeiter_id) > 5:
        return "Check ID length"
    else:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT status from mitarbeiter WHERE id_mitarbeiter=?", (mitarbeiter_id,))
        status = c.fetchone()
        status = status[0]

        if str(status) == "1":  # Wenn da, dann austragen
            c.execute("UPDATE mitarbeiter SET status=0 WHERE id_mitarbeiter=?", (mitarbeiter_id,))
            c.execute("UPDATE anwesenheit SET time_out=? WHERE id_mitarbeiter=? AND datum=?",
                      (uhrzeit, mitarbeiter_id, datum,))
            conn.commit()
            return "Erfolgreich ausgetragen! Zeitstempel -->{0} {1}".format(datum, uhrzeit)
        elif str(status) == "0":  # Wenn nicht da, eintragen
            c.execute("UPDATE mitarbeiter SET status=1 WHERE id_mitarbeiter=?", (mitarbeiter_id,))
            c.execute("INSERT INTO anwesenheit VALUES (NULL, ?, ?, ?, 'Noch anwesend...', 0)",
                      (mitarbeiter_id, datum, uhrzeit,))
            conn.commit()
            return "Erfolgreich eingetragen! Zeitstempel -->{0} {1}".format(datum, uhrzeit)
        else:
            return "Got incorrect values"
    c.close()

    return "ID: {0} Status: {1}".format(abfrage[0], abfrage[1])


run(host=host, port=port, reloader=autoreload, debug=debug)
