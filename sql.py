DB_FILENAME = "/home/pi/Heizung/mesurement_log.db"

import sqlite3

with sqlite3.connect(DB_FILENAME, timeout=100) as connection:
#    connection.execute("DROP TABLE measurement_log")
#    connection.execute("DROP TABLE error_log")
    connection.execute("CREATE TABLE IF NOT EXISTS measurement_log (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP, tOutdoor FLOAT, tHc1Current FLOAT, tHc1Target FLOAT)")
    connection.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value FLOAT)")
    connection.execute("CREATE TABLE IF NOT EXISTS error_log (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP, errorLevel TEXT, errorType TEXT, text TEXT)")

def measurement_log(tOutdoor, tHc1Current, tHc1Target):
    with sqlite3.connect(DB_FILENAME, timeout=100) as connection:
        connection.execute("INSERT INTO measurement_log (timestamp, tOutdoor, tHc1Current, tHc1Target) VALUES (CURRENT_TIMESTAMP, ?, ?, ?)", (float(tOutdoor), float(tHc1Current), float(tHc1Target)))


def getLast24HourMeasurements():
    with sqlite3.connect(DB_FILENAME, timeout=100, detect_types=sqlite3.PARSE_COLNAMES) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT timestamp as 'ts [timestamp]', tOutdoor, tHc1Current, tHc1Target FROM measurement_log WHERE timestamp > datetime('now', '-1 day') ORDER BY id ASC")
        return cursor.fetchall()


def setConfigValue(key, value):
    with sqlite3.connect(DB_FILENAME, timeout=100) as connection:
        connection.execute("REPLACE INTO config (key, value) VALUES (?, ?)", (str(key), float(value)))

def getConfigValue(key):
    with sqlite3.connect(DB_FILENAME, timeout=100) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", ([str(key)]) )
        result = cursor.fetchall()
        if result:
            return result[0][0]
        else:
            return None

def reportError(errorLevel, errorType, text):
    with sqlite3.connect(DB_FILENAME, timeout=100) as connection:
        connection.execute("INSERT INTO error_log (timestamp, errorLevel, errorType, text) VALUES (CURRENT_TIMESTAMP, ?, ?, ?)", ( str(errorLevel), str(errorType), str(text) ) )

def getLastWeekErrors():
    with sqlite3.connect(DB_FILENAME, timeout=100, detect_types=sqlite3.PARSE_COLNAMES) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT timestamp as 'ts [timestamp]', errorLevel, errorType, text FROM error_log WHERE timestamp > datetime('now', '-7 days') ORDER BY id DESC LIMIT 200")
        return cursor.fetchall()

def resetErrorLog():
    with sqlite3.connect(DB_FILENAME, timeout=100) as connection:
        connection.execute("DELETE FROM error_log")


