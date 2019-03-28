# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

from branca.element import CssLink, Element, Figure, JavascriptLink, MacroElement

from jinja2 import Template

#Note the Routing Services are using OSRMv1 demo server. This is not meant to be used for production purposes
# It is used for this program as a demo and not a live version, please see https://github.com/Project-OSRM/osrm-backend/wiki/Api-usage-policy for more details
class RoutingMachine(MacroElement):
   
    _template = Template("""
            {% macro script(this, kwargs) %}

            function button(label, container) {
                var btn = L.DomUtil.create('button', '', container);
                btn.setAttribute('type', 'button');
                btn.innerHTML = label;
                return btn;
            }
               var control= L.Routing.control({
                    waypoints: [],
                    routeWhileDragging: true,
                    position: 'bottomright',
                    geocoder: new L.Control.Geocoder.Nominatim(),
                    addWaypoints: true,
                    reverseWaypoints: true,

                }).addTo({{this._parent.get_name()}});



                {{this._parent.get_name()}}.on('click', function (e) {
                var container = L.DomUtil.create('div'),
                    startBtn = button('Start from this location', container),
                    destBtn = button('Go to this location', container);

                L.DomEvent.on(startBtn, 'click', function () {
                    control.spliceWaypoints(0, 1, e.latlng);
                    {{this._parent.get_name()}}.closePopup();
                });

                L.DomEvent.on(destBtn, 'click', function () {
                    control.spliceWaypoints(control.getWaypoints().length - 1, 1, e.latlng);
                    {{this._parent.get_name()}}.closePopup();
                });

                L.popup().setContent(container).setLatLng(e.latlng).openOn({{this._parent.get_name()}});
            });

                

                L.Routing.errorControl(control).addTo({{this._parent.get_name()}});

            {% endmacro %}
        """)  # noqa

    def __init__(self):
        super(RoutingMachine, self).__init__()

    def render(self, **kwargs):
        super(RoutingMachine, self).render()

        figure = self.get_root()
        assert isinstance(figure, Figure), ('You cannot render this Element '
                                            'if it is not in a Figure.')

        figure.header.add_child(
            JavascriptLink('https://cdn.jsdelivr.net/gh/dsh011/WxPathfinder/leaflet-routing-machine-3.2.12/leaflet-routing-machine.js'))  # noqa

        figure.header.add_child(
            JavascriptLink('https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js'))

        figure.header.add_child(
            CssLink('https://cdn.jsdelivr.net/gh/dsh011/WxPathfinder/leaflet-routing-machine-3.2.12/leaflet-routing-machine.css'))  # noqa