# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

from branca.element import CssLink, Element, Figure, JavascriptLink, MacroElement

from jinja2 import Template


class RoutingMachine(MacroElement):
    """
    Vector drawing and editing plugin for Leaflet.

    Parameters
    ----------
    export : bool, default False
        Add a small button that exports the drawn shapes as a geojson file.

    Examples
    --------
    >>> m = folium.Map()
    >>> Draw(export=True).add_to(m)

    For more info please check
    https://leaflet.github.io/Leaflet.draw/docs/leaflet-draw-latest.html

    """
    _template = Template("""
        {% macro script(this,kwargs) %}
            var {{this.get_name()}} = {
                base_layers : { {% for key,val in this.base_layers.items() %}"{{key}}" : {{val}},{% endfor %} },
                overlays : { {% for key,val in this.overlays.items() %}"{{key}}" : {{val}},{% endfor %} }
                };
            L.Routing.control(
                var {{this.get_name()}} = new L.Routng.control({})
        {% endmacro %}
        """)  # noqa

    def __init__(self, export=False):
        super(RoutingMachine, self).__init__()
        self._name = 'RouteControl'
        self.export = export

    def render(self, **kwargs):
        super(RouteControl, self).render()

        figure = self.get_root()
        assert isinstance(figure, Figure), ('You cannot render this Element '
                                            'if it is not in a Figure.')

        figure.header.add_child(
            JavascriptLink('https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.js'))  # noqa

        figure.header.add_child(
            CssLink('https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.css'))  # noqa