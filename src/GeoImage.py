from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import glob
from SQLConn import *
import sqlite3
import hashlib
import time, os
import wx
import geocoder
import WxPathfinder as main
from pubsub import pub
from threading import Thread



class ProcessThread(Thread):
    """Worker Thread Class."""
 
    #----------------------------------------------------------------------
    def __init__(self, WxObject, filecount, pathname, connection):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.mainWindow = WxObject
        self.filecount = filecount
        self.pathname = pathname
        self.conn = connection
        self.c = connection.cursor()
        self.start()    # start the thread
        
 
    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # Processes the photos in a separate thread for faster processing and allows a progress bar to be 
        # displayed for the user.
        types = ['*.jpg', '*.jpeg', '*.tiff']
        gps_data = {}
        exif_data = {}
        dup_hash = []
        no_gps = []
        files_processed = []
        generateThumbnails(self.pathname)
        for imgtype in types:
        	for ImgName in glob.glob(str(self.pathname) + '/' + imgtype):
        		imgFile = Image.open(ImgName)
        		filehash = hash_file(ImgName)
        		ImgRename = os.path.basename(ImgName) #Renaming for Database and Tree View Visibility
        		info = imgFile._getexif()
        		if info:
        			for tag, value in info.items():
        				decoded = TAGS.get(tag, tag)
        				if decoded == 'GPSInfo':
        					for t in value:
        						sub_decoded = GPSTAGS.get(t, t)
        						gps_data[sub_decoded] = value[t]
        						exif_data[decoded] = gps_data
        					lat, lon = get_lat_lon(exif_data)
        					try:
        						g = geocoder.osm([lat, lon], method='reverse')
        						zipcode = g.postal
        						if zipcode == None:
        							zipcode = 12345
        						insertZip(self.c, zipcode)
        					except sqlite3.IntegrityError:
        						print()
        					try:
        						g = geocoder.osm([lat, lon], method='reverse')
        						self.c.execute(("""SELECT zip_id from zipcodes WHERE Zip = {}""").format(zipcode))
        						ZipID = self.c.fetchall()
        						insertInto(self.c, ImgRename,  imgFile._getexif()[36867], g.address, ZipID[0][0], time.mktime(time.strptime(imgFile._getexif()[36867], '%Y:%m:%d %H:%M:%S')),lat, lon, filehash)
        						self.conn.commit()
        						files_processed.append(ImgRename)
        						wx.CallAfter(pub.sendMessage, "update", msg="")
        					except sqlite3.IntegrityError:
        						dup_hash.append(ImgRename)
        						wx.CallAfter(pub.sendMessage, "update", msg="")
        				else:
        					exif_data[decoded] = value
        					
        reportDoc(no_gps, dup_hash, files_processed, self.pathname, self.mainWindow)        

#Progress Bar Dialog Box Creation Class
class MyProgressDialog(wx.Dialog):
    def __init__(self, filecount):
        wx.Dialog.__init__(self, None, title="Processing")
        self.filecount = filecount
        self.count = 0
        self.progress = wx.Gauge(self, range=self.filecount)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.progress, 0, wx.EXPAND, 10)
        self.SetSizer(sizer)
 
        pub.subscribe(self.updateProgress, "update")

    def updateProgress(self, msg):
    	self.count += 1
    	if self.count >= self.filecount:
    		self.Destroy()

    	self.progress.SetValue(self.count)


#Establishes a permanent connection to the Database in the session      
def createconnection(db_file):
	try:
		conn = sqlite3.connect(db_file, check_same_thread=False, timeout=10)
		c = conn.cursor()
		c.execute("pragma foreign_keys = 1")
		createZipTable(c)
		createDefTable(c)
		return conn
	except Error as e:
		print(e)

#Extracts Longitude and Latitude from the Images

def displayTAGS():
	f = open("tags.txt", 'w')

	f.write(str(TAGS) + '\n')

#Retrieves the Latitude and Longitude in the exif data
def get_lat_lon(exif_data):
    lat = None
    lon = None
    for x in exif_data:
	    if x == 'GPSInfo':		
	        gps_info = exif_data["GPSInfo"]
	        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
	        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
	        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
	        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

	        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
	            lat = _convert_to_degrees(gps_latitude)
	            if gps_latitude_ref != "N":                     
	                lat = 0 - lat

	            lon = _convert_to_degrees(gps_longitude)
	            if gps_longitude_ref != "E":
	                lon = 0 - lon
	        return lat, lon
	    	

	    
#Checks to see if the coordinates exist, if not, returns nothing
def _get_if_exist(data, key):
    if key in data:
        return data[key]
		
    return None

#Needed to convert coordinates from radians to degrees for processing
def _convert_to_degrees(value):
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

#Returns the hash of the file
def hash_file(filename):

   h = hashlib.sha1()

   with open(filename,'rb') as file:
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   return h.hexdigest()



"""Reads all Exif data, if any, on the image and inserts it into a SQLite database.

User selects the directory to scan, preferably the directory all the photos are in, and it scans
all the photos with the extensions listed in the types list. If it has GPS coordinates, it goes through a 
conversion process, if the image in the database has a duplicate hash it lets the user know at the end,
if the photo has no exif data it lets the user know at the end.

"""
def preProcessingExif(self, conn):
	types = ['*.jpg', '*.jpeg', '*.tiff']
	totalcount = 0
	dlg = wx.DirDialog(self, "Choose Directory to Scan")
	if dlg.ShowModal() == wx.ID_CANCEL:
		return     # the user changed their mind
	pathname = dlg.GetPath()

	for imgtype in types:
		for ImgName in glob.glob(str(pathname) + '/' + imgtype):
        		imgFile = Image.open(ImgName)
        		filehash = hash_file(ImgName)
        		ImgRename = os.path.basename(ImgName) #Renaming for Database and Tree View Visibility
        		info = imgFile._getexif()
        		if info:
        			for tag, value in info.items():
        				decoded = TAGS.get(tag, tag)
        				if decoded == 'GPSInfo':
        					totalcount = totalcount + 1

	ProcessThread(self, totalcount, pathname, conn)
	dlgProg = MyProgressDialog(totalcount)
	dlgProg.ShowModal()


#Thumbnail Creation, needed to cut down size of photos. Reason: Pathfinder crashes if it uses full image.
def generateThumbnails(pathname):
	directory = 'Thumbnails'
	if not os.path.exists(directory):
		os.makedirs(pathname + '/' + directory)
	types = ['*.jpg', '*.jpeg', '*.tiff']
	for imgtype in types:
		for Img in glob.glob(str(pathname) + '/' + imgtype):
			im = Image.open(Img)
			info = im._getexif()
			ImgName = os.path.basename(Img)
			if info:
				for tag, value in info.items():
					decoded = TAGS.get(tag, tag)
					if decoded == 'GPSInfo':
						# convert to thumbnail image
						im.thumbnail((128, 128), Image.ANTIALIAS)
						# don't save if thumbnail already exists
						if ImgName[0:2] != "T_":
							# prefix thumbnail file with T_
							im.save((str(pathname) + '/' + directory + '/' + "T_" + ImgName), 'PNG')
						else:
							continue

def reportDoc(no_gps, dup_hash, files_processed, pathname, mainWindow):

	f = open(pathname + "/PathfinderReport.txt", "w")
	f.write("Files Processed:\n")
	f.write("--------------------------------------------------\n")
	for i in files_processed:
		f.write(i + "\n")
	f.write("\n")
	f.write("Files Containing No GPS\n")
	f.write("--------------------------------------------------\n")
	for j in no_gps:
		f.write(j + "\n")
	f.write("\n")
	f.write("Error Files: Duplicate Hashes \n")
	f.write("--------------------------------------------------\n")
	for k in dup_hash:
		f.write(k + "\n")

	dlg = wx.MessageDialog(mainWindow, "Processing is complete. Please check your report for more details.", "Processing Complete", wx.OK | wx.ICON_INFORMATION)
	dlg.ShowModal()
	dlg.Destroy()


"""
def testForExif():
	for ImgName in glob.glob("*.jpeg"):
		exifData = {}
		exifGPS = {}
		imgFile = Image.open(ImgName)
		info = imgFile._getexif()
		if info:
			for (tag, value) in info.items():
				decoded = TAGS.get(tag, tag)
				print(str(decoded))
				exifData[decoded] = value
			if 'GPSInfo' in exifData:
				print ('[*] ' + ImgName + ' contains GPS info')
				for t in value:
					decodeGPS = GPSTAGS.get(t,t)
					exifGPS[decodeGPS] = value[t]
				print(_convert_to_degrees(exifGPS['GPSLatitude']))
				
			else:
				print ('[*]' + ImgName + ' does not contain GPS info')
		else:
			print("Image has no exif data")
"""