from distutils.core import setup
import py2exe

setup(windows=['WxPathfinder.py'],
	options= {
		'py2exe': {
			'packages': ['folium','WxPython', 'PIL', 'geocoder', 'geojson']
		}
	})