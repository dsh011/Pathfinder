import sqlite3
import wx


def createDefTable(c):
	sql_create_default_table = """CREATE TABLE IF NOT EXISTS exifdata (
	id integer PRIMARY KEY, name text NOT NULL,date_time text, Address text, date_unixtimestamp REAL, Latitude REAL,Longitude REAL, SHA1 varchar(255) UNIQUE); """
	c.execute(sql_create_default_table)

def insertInto(c, picname, picdate, picAddress, pictimestamp, piclat, piclong, pichash):
	c.execute("""INSERT INTO exifdata(name, date_time, Address, date_unixtimestamp, Latitude, Longitude, SHA1) VALUES (?,?,?,?,?,?,?)""", (picname, picdate, picAddress, pictimestamp, piclat, piclong, pichash))
	
	