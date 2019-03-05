import wx
import wx.lib.inspection

import wx.html2, os
import folium
from folium import IFrame
from folium import plugins
from folium.plugins import Draw
from folium.plugins import routingmachine as rm
import routingmachine
from SQLConn import *
import base64
import time
import geocoder
from GeoImage import *
import wx.grid as gridlib
import sqlite3
from geojson import Feature, Point, FeatureCollection
import openrouteservice


__attrStringGeneral = 'Map creation by <a href="https://python-visualization.github.io/folium/">Folium</a> | \
Routes from <a href="http://project-osrm.org/">OSRM</a>, \
Data uses <a href="https://opendatacommons.org/licenses/odbl/">ODbL</a> license'

__attrStringMain = 'Map creation by <a href="https://python-visualization.github.io/folium/">Folium</a> | \
&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> | \
Routes from <a href="http://project-osrm.org/">OSRM</a>,\
Data uses <a href="https://opendatacommons.org/licenses/odbl/">ODbL</a> license'

class MyTree(wx.TreeCtrl):
    '''Our customized TreeCtrl class
    '''
    def __init__(self, parent, id, position, size, style):
        '''Initialize our tree
        '''
        wx.TreeCtrl.__init__(self, parent, id, position, size, style)
        
class Init(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title)

		self.CreateStatusBar()
		self.filemenu = wx.Menu()

		menuNew = self.filemenu.Append(wx.ID_ANY, "&New Database","Create New Database")
		menuOpen= self.filemenu.Append(wx.ID_ANY, "&Open Database","Open Existing Database")

		menuBar = wx.MenuBar()
		menuBar.Append(self.filemenu,"&File")
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.createDatabase, menuNew)
		self.Bind(wx.EVT_MENU, self.openDatabase, menuOpen)

		self.Show(True)

	def openDatabase(self, e):
		with wx.FileDialog(self, "Open Current Database", wildcard="db files (*.db)|*.db", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return

			pathname = fileDialog.GetPath()
		self.connection = createconnection(pathname)
		self.Close()
		MainWindow(None, "Pathfinder 2.1", self.connection)

	def createDatabase(self, e):

		with wx.FileDialog(self, "Create Database", wildcard="db files (*.db)|*.db", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return     # the user changed their mind
			pathname = fileDialog.GetPath()
		self.connection = createconnection(pathname)
		self.Close()
		MainWindow(None, "Pathfinder 2.1", self.connection)


class LeftPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.tree = MyTree(self, 0, wx.DefaultPosition, (-1, -1), wx.TR_HAS_BUTTONS)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.SetSize((500, 500))   

class RightPanel(wx.Panel):
    def __init__(self, parent):
    	wx.Panel.__init__(self, parent=parent)

    	sizer = wx.BoxSizer(wx.VERTICAL)

    	self.browser = wx.html2.WebView.New(self)
    	sizer.Add(self.browser, 1, wx.EXPAND, 10)
    	self.SetSizer(sizer) 
    	self.SetSize((500, 500))

class MainWindow(wx.Frame):
	def __init__(self, parent, title, connection):
		wx.Frame.__init__(self, parent, title = title)

		
		self.connection = connection
		self.c = self.connection.cursor()
		splitter = wx.SplitterWindow(self)
		self.leftP = LeftPanel(splitter)
		self.rightP = RightPanel(splitter)

		

		splitter.SplitVertically(self.leftP, self.rightP)
		splitter.SetMinimumPaneSize(200)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(splitter, 1, wx.EXPAND)
		self.SetSizer(sizer)

		self.tree = self.leftP.tree

		self.root = self.tree.AddRoot('Pathfinder')

		self.CreateStatusBar()

		self.popupmenu = wx.Menu()
		popupcopy = self.popupmenu.Append(wx.ID_ANY, "Copy")

		self.filemenu = wx.Menu()
		
		menuAbout = self.filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
		self.filemenu.AppendSeparator()
		menuExit = self.filemenu.Append(wx.ID_EXIT,"E&xit","Terminate the program")

		self.datamenu = wx.Menu()
		menuGPS = self.datamenu.Append(wx.ID_ANY,"&Acquire GPS Data","Acquires GPS Data from Photos")
		treeDisp= self.datamenu.Append(wx.ID_ANY,"&Display Data","Displays Current Coordinate Data in Left Panel")
		

		self.mapmenu = wx.Menu()
		openMap = self.mapmenu.Append(wx.ID_OPEN, "&Open Map", "Opens a map file")
		createMap = self.mapmenu.Append(wx.ID_ANY, "&Create Map", "Creates a map from Coordinates")

		self.browsermenu = wx.Menu()
		reloadPage = self.browsermenu.Append(wx.ID_ANY, "&Reload Page", "Reloads Page")
		printPage = self.browsermenu.Append(wx.ID_ANY, "&Print Page", "Opens printing options")
		


		self.filtermenu = wx.Menu()
		self.dateFilter = self.filtermenu.AppendCheckItem(wx.ID_ANY, "&By Date", "Filter Results by Date")

		menuBar = wx.MenuBar()
		menuBar.Append(self.filemenu,"&File") # Adding the "filemenu" to the MenuBar
		menuBar.Append(self.datamenu,"&Data")
		menuBar.Append(self.mapmenu, "&Map")
		menuBar.Append(self.filtermenu, "&Filter")
		menuBar.Append(self.browsermenu, "&Browser")
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.


		#Sets Events
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Bind(wx.EVT_MENU, self.checkFilter, createMap)
		self.Bind(wx.EVT_MENU, self.openHTMLMap, openMap)
		self.Bind(wx.EVT_MENU, self.dataExtract, menuGPS)
		self.Bind(wx.EVT_MENU, self.displayTree, treeDisp)
		self.Bind(wx.EVT_MENU, self.OnPopupCopy, popupcopy)
		self.Bind(wx.EVT_MENU, self.reloadBrowser, reloadPage)
		self.Bind(wx.EVT_MENU, self.printBrowser, printPage)
		self.Bind(wx.EVT_MENU, self.setFilter, self.dateFilter)#self.dateFilter is by itself because other functions need to check if its checked; Required.
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)


		self.Show(True)
		

	def OnAbout(self, e):
		dlg = wx.MessageDialog(self, "Welcome to Pathfinder! This is a GPS Analysis Tool to help you \
			with gathering EXIF data from images acquired from electronic devices. To begin, go \
			to the Data tab at the top of the menu and click Acquire GPS Data", "A GPS Analysis Add-on Tool",  wx.OK)
		dlg.ShowModal()
		dlg.Destroy()

	def OnShowPopup(self, event):
		pos = event.GetPosition()
		pos = self.leftP.ScreenToClient(pos)
		self.leftP.PopupMenu(self.popupmenu, pos)

	def OnPopupCopy(self, e):
		item = self.tree.GetSelection()
		text = self.tree.GetItemText(item)
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(wx.TextDataObject(text))
			wx.TheClipboard.Close()
		dlg = wx.MessageDialog(self, "Copied to Clipboard", "Pathfinder", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		e.Skip()

	def OnExit(self, e):
		self.Close(True)

		"""
		Creates the Map. To comply with map usage, a custom tile link has been provided with associated license display requests.
		DO NOT CHANGE THESE. The author is/will not be responsible for any legal action taken against the user of this application.
		This will also be stated in the github page at: 
		"""
	def createMapFile(self, Latitude, Longitude, ImgName, ImgDate):
		dlg = wx.DirDialog(self, "Select Photo Directory:")
		if dlg.ShowModal() == wx.ID_CANCEL:
			return     # the user changed their mind
		pathname = dlg.GetPath()

		coordsPopup = []
		coordsSearch = []
		points = []
		draw = Draw()
		mymap = folium.Map(location=[38.0, -97.0],zoom_start=5, attr=__attrStringMain)
		resolution, width, height = 75, 7, 3
		for j in range(0, len(Latitude)):
			coordsPopuptemp = [Latitude[j][0], Longitude[j][0]]
			coordsSearchtemp = [Longitude[j][0], Latitude[j][0]]
			coordsPopup.append(coordsPopuptemp)
			coordsSearch.append(coordsSearchtemp)

		for x in range(0, len(coordsSearch)):
			point = Point(coordsSearch[x])
			my_feature = Feature(geometry=point, properties={"name": ImgName[x][0]})
			points.append(my_feature)

		feature_collection = FeatureCollection(points)
		folium.plugins.Search(feature_collection, search_zoom=20).add_to(mymap)
		
		for x in range(0, len(coordsPopup)):
			filename = os.path.join((pathname + '/' + "Thumbnails"), ("T_" + ImgName[x][0]))
			encoded = base64.b64encode(open(filename, 'rb').read()).decode()
			htmlstr = '<div style="font-size: 10pt">{}</div><div style="font-size: 10pt">{}</div><div style="font-size: 10pt">{}</div>, <img src="data:image/jpeg;base64,{}", \
    		width="128px" height="128px">'.format(ImgName[x][0],ImgDate[x][0],str(coordsPopup[x]),encoded)
			html = folium.Html(htmlstr, script=True)
			iframe = folium.IFrame(html, width=(width*resolution)+20, height=(height*resolution)+20)
			popup = folium.Popup(html= html, parse_html=True, max_width=600)
			folium.Marker(location=coordsPopup[x], popup=popup).add_to(mymap)	

			#folium.PolyLine(coords, color="red", weight=2.5, opacity=100).add_to(mymap)
		#mymap.add_child(folium.LatLngPopup())
		rm.RoutingMachine().add_to(mymap)
		folium.TileLayer(tiles='Mapbox Bright', attr=__attrStringGeneral).add_to(mymap)
		folium.TileLayer(tiles='Mapbox Control Room', attr=__attrStringGeneral).add_to(mymap)

		#folium.TileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}{r}.png', attr='© OpenStreetMap contributors').add_to(mymap)
		#folium.TileLayer('CartoDB').add_to(my_map)
		
		folium.LayerControl().add_to(mymap)
		draw.add_to(mymap)
		
		try:
			mymap.save(self.OnSaveAs())
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, "Map Not Saved Correctly!", "Error!", wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

	def openHTMLMap(self, e):
		with wx.FileDialog(self, "Open HTML file", wildcard="html files (*.html)|*.html", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return     # the user changed their mind

			pathname = fileDialog.GetPath()
		self.rightP.browser.LoadURL(pathname)
		#self.rightP.browser.EnableContextMenu()

	#Calls function to extract data from photos
	def dataExtract(self, e):
		get_exif_data(self, self.connection)

	def thread_start(self, event):
		th = threading.Thread(target=openHTMLMap ,args=(e))
		th.start()

	def reloadBrowser(self, e):
		self.rightP.browser.Reload()

	def printBrowser(self, e):
		self.rightP.browser.Print()		
		
	def OnSaveAs(self):
		with wx.FileDialog(self, "Save html file", wildcard="html files (*.html)|*.html", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return     # the user changed their mind
			pathname = fileDialog.GetPath()
			return pathname

	def tree_item_exists(self, tree, match, root):
		item, cookie = tree.GetFirstChild(root)
		while item.IsOk():
			if tree.GetItemText(item) == match:
				return True
			item, cookie = tree.GetNextChild(root, cookie)

		return False


	def displayTree(self, e):

		coords = []

		if self.dateFilter.IsChecked():
			#startDate = simpledialog.askstring("Enter Start Date", "Enter Start Date(YYYY/MM/DD hh/mm/ss): ")
			#endDate = simpledialog.askstring("Enter End Date", "Enter End Date(YYYY/MM/DD hh/mm/ss): ")
			#filterinfo = c.execute("""SELECT * from exifData WHERE date_time BETWEEN {} AND {}""".format(convstart, convend))
			self.c.execute(("SELECT Latitude from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
			Latitude = self.c.fetchall()
			self.c.execute(("SELECT Longitude from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
			Longitude = self.c.fetchall()
			self.c.execute(("SELECT name from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
			ImgName = self.c.fetchall()
			self.c.execute(("SELECT date_time from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
			ImgDate = self.c.fetchall()
			self.c.execute(("SELECT Address from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
			Address = self.c.fetchall()

			for j in range(0, len(Latitude)):
				coordsTemp = [Latitude[j][0], Longitude[j][0]]
				coords.append(coordsTemp)

			for k in range(0, len(ImgName)):
				if self.tree_item_exists(self.tree, ImgName[k][0], self.root):
					return
				else:
					iname = self.tree.AppendItem(self.root, str(ImgName[k][0]))
					coordTreeMenu = self.tree.AppendItem(iname, "Coordinates")
					treecoords = self.tree.AppendItem(coordTreeMenu, str(coords[k]))
					coordDateMenu = self.tree.AppendItem(iname, "Date/Time Taken")
					treedate = self.tree.AppendItem(coordDateMenu, str(ImgDate[k][0]))
					coordAddressMenu = self.tree.AppendItem(iname, "Address")
					treeaddress = self.tree.AppendItem(coordAddressMenu, Address[k][0])
				
		else:
			self.c.execute("""SELECT Latitude from exifdata""")
			Latitude = self.c.fetchall()
			self.c.execute("""SELECT Longitude from exifdata""")
			Longitude = self.c.fetchall()
			self.c.execute("""SELECT name from exifdata""")
			ImgName = self.c.fetchall()
			self.c.execute("""SELECT date_time from exifdata""")
			ImgDate = self.c.fetchall()
			self.c.execute("""SELECT Address from exifdata""")
			Address = self.c.fetchall()

			for j in range(0, len(Latitude)):
				coordsTemp = [Latitude[j][0], Longitude[j][0]]
				coords.append(coordsTemp)

			for k in range(0, len(ImgName)):
				if self.tree_item_exists(self.tree, ImgName[k][0], self.root):
					return
				else:
					iname = self.tree.AppendItem(self.root, str(ImgName[k][0]))
					coordTreeMenu = self.tree.AppendItem(iname, "Coordinates")
					treecoords = self.tree.AppendItem(coordTreeMenu, str(coords[k]))
					coordDateMenu = self.tree.AppendItem(iname, "Date/Time Taken")
					treedate = self.tree.AppendItem(coordDateMenu, str(ImgDate[k][0]))
					coordAddressMenu = self.tree.AppendItem(iname, "Address")
					treeaddress = self.tree.AppendItem(coordAddressMenu, Address[k][0])

	def setFilter(self, e):
		frame = wx.Frame(None, -1, 'win.py')
		frame.SetDimensions(0,0,200,50)
		dlgStartDate = wx.TextEntryDialog(frame, "Enter Start Date", "Enter Start Date(YYYY/MM/DD hh/mm/ss): ")
		dlgStartDate.ShowModal()
		self.startDate = dlgStartDate.GetValue()
		dlgStartDate.Destroy()
		dlgEndDate = wx.TextEntryDialog(frame, "Enter End Date", "Enter End Date(YYYY/MM/DD hh/mm/ss): ")
		dlgEndDate.ShowModal()
		self.endDate = dlgEndDate.GetValue()
		dlgEndDate.Destroy()

	def checkFilter(self, e):

		if self.dateFilter.IsChecked():
			#frame = wx.Frame(None, -1, 'win.py')
			#frame.SetDimensions(0,0,200,50)
			#dlgStartDate = wx.TextEntryDialog(frame, "Enter Start Date", "Enter Start Date(YYYY/MM/DD hh/mm/ss): ")
			#dlgStartDate.ShowModal()
			#startDate = dlgStartDate.GetValue()
			#dlgStartDate.Destroy()
			#dlgEndDate = wx.TextEntryDialog(frame, "Enter End Date", "Enter End Date(YYYY/MM/DD hh/mm/ss): ")
			#dlgEndDate.ShowModal()
			#endDate = dlgEndDate.GetValue()
			#dlgEndDate.Destroy()
			#startDate = simpledialog.askstring("Enter Start Date", "Enter Start Date(YYYY/MM/DD hh/mm/ss): ")
			#endDate = simpledialog.askstring("Enter End Date", "Enter End Date(YYYY/MM/DD hh/mm/ss): ")


			if self.startDate == '' or self.endDate == '':
				dlg = wx.MessageDialog(self, "You must enter a date!", "Error!", wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				return		
			else:
				try:
					self.convstart = time.mktime(time.strptime(startDate, '%Y/%m/%d %H/%M/%S'))
					self.convend = time.mktime(time.strptime(endDate, '%Y/%m/%d %H/%M/%S'))
				except ValueError:
					dlg = wx.MessageDialog(self, "Date needs to be in correct format!", "Error!", wx.OK | wx.ICON_ERROR)
					dlg.ShowModal()
					dlg.Destroy()
					return
				#filterinfo = c.execute("""SELECT * from exifData WHERE date_time BETWEEN {} AND {}""".format(convstart, convend))
				self.c.execute(("SELECT Latitude from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
				Latitude = self.c.fetchall()
				self.c.execute(("SELECT Longitude from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
				Longitude = self.c.fetchall()
				self.c.execute(("SELECT name from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
				ImgName = self.c.fetchall()
				self.c.execute(("SELECT date_time from exifdata WHERE date_unixtimestamp BETWEEN {} AND {}").format(self.convstart, self.convend))
				ImgDate = self.c.fetchall()
				self.createMapFile(Latitude, Longitude, ImgName, ImgDate)
		else:
			self.c.execute("""SELECT Latitude from exifdata""")
			Latitude = self.c.fetchall()
			self.c.execute("""SELECT Longitude from exifdata""")
			Longitude = self.c.fetchall()
			self.c.execute("""SELECT name from exifdata""")
			ImgName = self.c.fetchall()
			self.c.execute("""SELECT date_time from exifdata""")
			ImgDate = self.c.fetchall()
			self.createMapFile(Latitude, Longitude, ImgName, ImgDate)


if __name__ == "__main__":
	app = wx.App(False)
	Init(None, "Database Selection")
	app.MainLoop()