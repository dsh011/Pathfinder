# Pathfinder
Pathfinder is an Open-Source Photo Mapping Tool designed to extract metadata from Photos and plot them on a leaflet map.

This is a project by me to fulfill the project requirements for the Master's of Science degree in Digital Forensics at Sam Houston State University.

This tool is designed in Python 3.6 version and uses a variety of libraries available through pip install and are also Open-Source.

Libraries included are:
1. Folium (Mapping Library)
2. Leaflet Routing Machine (Designed and developed by Per Liedman)
3. Python Imaging Library (PIL)
4. WxPython (GUI Framework)
5. Geocoder (Geocoding service Library)
6. OpenRouteService (Needed for Routing Machine; Developed by the GIScience Research Group)
7. Variety of Python Native Libraries (OS, Time, Threading, SQLite3, etc.)
8. Cx_Freeze (Packaging Python Code; Developed by Anthony Tuininga)

# Installer.Rar
This archive holds a current Microsoft Installer file to install Pathfinder. Download the archive, unzip it, and the executable is within. The executable only runs on Windows at this time. 

## Extra Setup
After installing the program, there is a slight change that needs to be made. In order to open maps properly, launch regedit and
navigate to **Computer\HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BROWSER_EMULATION**
(might vary depending on your installation). After navigating, right click, hover over new, and select **DWORD**. A new value should
have been created. Right click the new value and changed the value name to without quotes "Pathfinder.exe" and set the **DECIMAL** value 
to **11001**. Once finished, exit regedit and launch Pathfinder.

# Testing Machine

CPU: i7-4790 3.6GHz
RAM: 8GB
OS: Windows 10 64bit



This program is currently licensed under the MIT License. Libraries in the credits have their own licenses. Please review these before 
any changes are made. 

**Note** The Nominatim (Geocoding) service has a usage policy. Please see the link for their usage policy. https://operations.osmfoundation.org/policies/nominatim/
Using this service was just for demonstration purposes and should not be used commercially for bulk requests.

To use your own routing service URL, find the routingmachine.py file and look for the line similar to this and add your URL
service:

```
L.Routing.control({
    waypoints: [
        L.latLng(57.74, 11.94),
        L.latLng(57.6792, 11.949)
    ],
    router: new L.Routing.OSRMv1({
        serviceUrl: url_to_your_service
    })
}).addTo(map);
```


# Credits
1. OpenRouteService: https://github.com/GIScience/openrouteservice
2. Folium: https://github.com/python-visualization/folium
3. PIL: https://pillow.readthedocs.io/en/stable/
4. WxPython: https://wxpython.org/
5. Leaflet Routing Machine: http://www.liedman.net/leaflet-routing-machine/
6. Geocoder: https://geocoder.readthedocs.io/
7. Python: https://www.python.org/
8. Cx_Freeze: https://github.com/anthony-tuininga/cx_Freeze

If I missed your credit, this was not intentional, please inform me and I will add you to the list.
