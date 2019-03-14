import sqlite3
import wx


def createDefTable(c):
	sql_create_default_table = """CREATE TABLE IF NOT EXISTS exifdata (
	id integer PRIMARY KEY, name text NOT NULL,date_time text, Address text, zip_id integer, date_unixtimestamp REAL, Latitude REAL,Longitude REAL, SHA1 varchar(255) UNIQUE, FOREIGN KEY(zip_id) REFERENCES zipcodes(zip_id) ); """
	c.execute(sql_create_default_table)

def createZipTable(c):
	sql_create_zip_table = """CREATE TABLE IF NOT EXISTS zipcodes (
	zip_id integer PRIMARY KEY, Zip REAL UNIQUE);"""
	c.execute(sql_create_zip_table)

def insertInto(c, picname, picdate, picAddress, ZipID, pictimestamp, piclat, piclong, pichash):
	c.execute("""INSERT INTO exifdata(name, date_time, Address, zip_id, date_unixtimestamp, Latitude, Longitude, SHA1) VALUES (?,?,?,?,?,?,?,?)""", (picname, picdate, picAddress, ZipID, pictimestamp, piclat, piclong, pichash))

def insertZip(c, picZip):
	c.execute("""INSERT INTO zipcodes(Zip) VALUES (?)""", (picZip,))
	
	