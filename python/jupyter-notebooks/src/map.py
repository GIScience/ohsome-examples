"""
Created on Fri Nov 13 10:28:46 2020

@author: Clemens Langer
"""


import ipyleaflet
import ipywidgets as widgets
from branca.colormap import linear
import random
import requests
import numpy as np
import datetime


from math import sin, cos, sqrt, atan2, radians
from traitlets import Tuple


def get_distance(lon1, lat1, lon2, lat2):
    '''returns the distance between 2 points in km'''
    import pyproj
    import math
    from pyproj import Transformer
    
    utm_band = str((math.floor((lon1 + 180) / 6 ) % 60) + 1)
    if len(utm_band) == 1:
        utm_band = '0'+utm_band
    if lat1 >= 0:
        epsg_code = '326' + utm_band
    else:
        epsg_code = '327' + utm_band
        
    transformer = Transformer.from_crs("epsg:4326", 'epsg:{0}'.format(epsg_code))

    
    x1, y1 =transformer.transform(lat1, lon1)
    x2, y2 =transformer.transform(lat2, lon2)

    return  np.sqrt((x2-x1)**2 + (y2-y1)**2)/1000


def get_geojson_grid(BBOXes, n):
    '''creates a grid with a given cell edge length in km containing one or multiple BBoxes'''
    max_cells = 0
    steps_dict = {}
    for location, coord_string in BBOXes.items():
        
        coord = [float(i) for i in coord_string.split(",")]
        
        lower_left = coord[0:2]
        upper_right = coord[2:4]
        #calculate the minimum number of cells
        dlat = get_distance(coord[0], coord[1], coord[0], coord[3])
        dlon = get_distance(coord[0], coord[1], coord[2], coord[1])
        flat = (n / dlat) * (int(dlat / n) + 1)
        flon = (n / dlon) * (int(dlon / n) + 1)
    
        lon_steps = np.linspace(
            lower_left[0],
            lower_left[0] + (upper_right[0] - lower_left[0]) * flon,
            int(dlon / n) + 2,
        )
        lat_steps = np.linspace(
            lower_left[1],
            lower_left[1] + (upper_right[1] - lower_left[1]) * flat,
            int(dlat / n) + 2,
        )

        
        steps_dict[location] = {"lat_steps": lat_steps, "lon_steps": lon_steps}
        max_cells = max(len(lat_steps) * len(lon_steps), max_cells)
    
    geo_json = {"type": "FeatureCollection", "features": []}
    for base_id, (location, steps) in enumerate(steps_dict.items()):
        lat_steps = steps["lat_steps"]
        lon_steps = steps["lon_steps"]
        
        lat_stride = lat_steps[1] - lat_steps[0]
        lon_stride = lon_steps[1] - lon_steps[0]

        for lat_id, lat in enumerate(lat_steps[:-1]):
            for long_id, lon in enumerate(lon_steps[:-1]):
                # Define dimensions of box in grid
                upper_left = [lon, lat + lat_stride]
                upper_right = [lon + lon_stride, lat + lat_stride]
                lower_right = [lon + lon_stride, lat]
                lower_left = [lon, lat]
                if dlon > dlat:
                    id = (int(dlon / n) + 2) * long_id + lat_id
                else:
                    id = (int(dlat / n) + 2) * lat_id + long_id
                id = id + max_cells * base_id
                # Define json coordinates for polygon
                coordinates = [
                    upper_left[::],
                    upper_right[::],
                    lower_right[::],
                    lower_left[::],
                    upper_left[::],
                ]
                grid_feature = {
                    "type": "Feature",
                    "id": "{}".format(id),
                    "properties": {
                        "location": location,
                        "lower_left": lower_left,
                        "upper_right": upper_right,
                        "bbox": "{},{},{},{}".format(
                            lower_left[0],
                            lower_left[1],
                            upper_right[0],
                            upper_right[1]),
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coordinates],
                    },
                }

                geo_json["features"].append(grid_feature)
    return geo_json


def get_time_stamp_list(date1, date2):
    '''returns all timestamps between 2 dates'''
    start_year = [int(i) for i in date1.split("T")[0].split("-")]
    end_year = [int(i) for i in date2.split("T")[0].split("-")]
    if end_year[0:2:] == start_year[0:2:]:
        return ["{}-{:02d}-01T00:00:00".format(end_year[0], end_year[1])]
    timestamps = []
    for i in range(start_year[0], end_year[0] + 1):
        if i == start_year[0]:
            start_month = start_year[1]
        else:
            start_month = 1
        if i != end_year[0]:
            end_month = 12
        else:
            end_month = end_year[1]
        for o in range(start_month, end_month + 1):
            timestamps.append("{}-{:02d}-01T00:00:00".format(i, o))
    return timestamps


def create_style_dict(response):
    '''creates a style dict for choropleth map for a given ohsome response'''
    style_dict = {}
    body = response.json()

    for result in body["groupByResult"]:
        values = []
        for i in result["result"]:
            values.append(i["value"])
        grid_id = result["groupByObject"]

        for i in result["result"]:
            timestamp = str(
                datetime.datetime.strptime(
                    i["timestamp"].split("T")[0],
                    "%Y-%m-%d"))
            if timestamp not in style_dict:
                style_dict[timestamp] = {}
            style_dict[timestamp][grid_id] = i["value"]

    return style_dict


def calculate_tag(grid, TIME, FILTER, style_dict):
    '''calculates the average number of tags for a given filters for given geojson'''
    URL = "https://api.ohsome.org/v1"
    endpoint = "/elementsFullHistory/centroid"
    time = TIME.replace("/P1M", "").replace("/", ",")

    for filter in FILTER:
        style_dict["tags_{}".format(filter)] = {}
        for cell in grid["features"]:
            grid_id = cell["id"]
            params = {
                "bboxes": cell["properties"]["bbox"],
                "filter": filter,
                "time": time,
                "properties": "tags",
            }
            with requests.post(URL + endpoint, data=params) as response:
                body = response.json()
            tags = {}
            if "features" in body:
                for feature in body["features"]:
                    timestamps = get_time_stamp_list(
                        feature["properties"]["@validFrom"],
                        feature["properties"]["@validTo"],
                    )
                    for timestamp in timestamps:
                        if timestamp not in tags:
                            tags[timestamp] = [len(feature["properties"]) - 3]
                        else:
                            tags[timestamp].append(
                                len(feature["properties"]) - 3)

            for timestamp in tags.keys():
                if timestamp not in style_dict["tags_{}".format(filter)]:
                    style_dict["tags_{}".format(filter)][timestamp] = {
                        grid_id: sum(tags[timestamp]) / len(tags[timestamp])
                    }
                else:
                    style_dict["tags_{}".format(filter)][timestamp][grid_id] = sum(
                        tags[timestamp]) / len(tags[timestamp])
        grid_ids = [cell["id"] for cell in grid["features"]]
        for timestamp, values in style_dict["tags_{}".format(filter)].items():
            for grid_id in grid_ids:
                if grid_id not in values:
                    values[grid_id] = 0

    return style_dict


def calculate_change(style_dict):
    '''´calulates the diffrence between time intervals'''
    temp_style_dict = {}
    for filter in style_dict.keys():
        dates = sorted([date for date in style_dict[filter].keys()])

        temp_style_dict["delta" + filter] = {}
        for i, timestamp in enumerate(dates):
            temp_style_dict["delta" + filter][timestamp] = {}
            for gridid in style_dict[filter][timestamp]:
                if i == 0:
                    delta = 0
                else:
                    delta = (
                        style_dict[filter][timestamp][gridid]
                        - style_dict[filter][dates[i - 1]][gridid]
                    )
                temp_style_dict["delta" + filter][timestamp][gridid] = delta
    for key, value in temp_style_dict.items():
        style_dict[key] = value
    return style_dict


class ChoroplethMap:
    '''ChoroplethMap class, which handles the query and rendering for a given '''
    def on_click(self, change):
        '''handles changes for the layer selection'''
        filter = change["new"]
        self.layer.choro_data = self.all_style_dict[filter][str(
            self.time_slider.value)]
        self.color_range.max = max(
            self.layer.choro_data.items(),
            key=lambda k: k[1])[1]

    def on_slide(self, change):
        ''' handles changes for the timeslider'''
        self.layer.choro_data = self.all_style_dict[self.dropdown.value][change["new"]]
        self.color_range.max = max(
            self.layer.choro_data.items(),
            key=lambda k: k[1])[1]

    def on_selection(self, change):
        '''handles changes for the color range selection'''
        self.layer.value_min = change["new"][0]
        self.layer.value_max = change["new"][1]

    def zoom_out_to_target_bounds(self, change):
        ''' zooms automaticaly out to minimal zoomlevel containing certain target bounds'''
        # the change owner is the widget triggering the handler, in this case a Map
        # if we're not zoomed all the way out already, and we have a target...
        if self.m.zoom > 1 and self.m.target_bounds:
            b = self.m.target_bounds
            n = change.new
            if (
                n[0][0] < b[0][0]
                and n[0][1] < b[0][1]
                and n[1][0] > b[1][0]
                and n[1][1] > b[1][1]
            ):
                # bounds are already large enough, so remove the target
                self.m.target_bounds = None
            else:
                # zoom out
                self.m.zoom = self.m.zoom - 1

    def zoom_to_location(self, change):
        '''handles changes in location selection'''

        bbox = self.BBOXes[change["new"]]

        coord = [float(i) for i in bbox.split(",")]
        center = [sum(coord[1::2]) / 2, sum(coord[0::2]) / 2]
        self.m.center = center
        self.m.target_bounds = ((coord[1], coord[0]), (coord[3], coord[2]))

    def getTimeChoroplethMap(
            self,
            BBOXes,
            FILTER,
            TIME, 
            delta=True,
            tags=True,
            size=1):
        '''creates and querys all needed data for the choropleth map'''

        URL = "https://api.ohsome.org/v1"
        self.BBOXes = BBOXes
        FILTER = FILTER
        TIME = TIME
        self.all_style_dict = {}

        self.grid = get_geojson_grid(BBOXes, size)
        endpoint = "/elements/count/groupBy/boundary"

        for filter in FILTER:
            params = {
                "bboxes": "|".join(
                    [
                        "{}:{}".format(i["id"], i["properties"]["bbox"])
                        for i in self.grid["features"]
                    ]
                ),
                "filter": filter,
                "time": TIME,
            }
            response = requests.post(URL + endpoint, data=params)
            self.all_style_dict[filter] = create_style_dict(response)

        if delta:
            self.all_style_dict = calculate_change(self.all_style_dict)
        if tags:
            self.all_style_dict = calculate_tag(
                self.grid, TIME, FILTER, self.all_style_dict
            )

    def loadJSON(self, path_style, path_grid, BBOXes):
        import json

        self.BBOXes = BBOXes
        self.all_style_dict = json.load(open(path_style))
        self.grid = json.load(open(path_grid))

    def saveJSON(self, path_style, path_grid):
        import json

        with open(path_style,'w+') as out_style:
            json.dump(self.all_style_dict, out_style)
        with open(path_grid,'w+') as out_grid:
            json.dump(self.grid, out_grid)

    def renderMap(self):
        '''creates ipyleaflet map'''
        self.m = ipyleaflet.Map(
            center=(
                33.66832279243364,
                135.8861750364304),
            zoom=10)
        # self.grid
        options = []
        options.extend(list(self.all_style_dict.keys()))
        option = options[0]

        dates = sorted([date for date in self.all_style_dict[option].keys()])
        

        self.layer = ipyleaflet.Choropleth(
            geo_data=self.grid,
            choro_data=self.all_style_dict[option][str(dates[0])],
            colormap=linear.YlOrRd_04,
            style={"fillOpacity": 0.8, "dashArray": "5, 5"},
        )
        self.m.add_layer(self.layer)

        self.time_slider = widgets.SelectionSlider(
            options=dates,
            value=dates[0],
            description="TimeStamp",
            disabled=False,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
        )
        self.time_slider.observe(self.on_slide, "value")
        widget_control_slider = ipyleaflet.WidgetControl(
            widget=self.time_slider, position="bottomright"
        )

        self.m.add_control(widget_control_slider)
        # widgets.interact(update_map_time, timeStamp = self.time_slider)

        self.dropdown = widgets.Dropdown(
            options=options, value=option, description="Select layer"
        )
        self.dropdown.observe(self.on_click, "value")

        widget_control = ipyleaflet.WidgetControl(
            widget=self.dropdown, position="topright"
        )
        self.m.add_control(widget_control)

        self.color_range = widgets.IntRangeSlider(
            value=[self.layer.value_min, self.layer.value_max],
            min=self.layer.value_min,
            max=self.layer.value_max,
            step=1,
            description="ColorBar:",
            disabled=False,
            continuous_update=False,
            orientation="horizontal",
            readout=True,
            readout_format="d",
        )
        self.zoom_to_location({"new": list(self.BBOXes.keys())[0]})

        self.color_range.observe(self.on_selection, "value")

        widget_control = ipyleaflet.WidgetControl(
            widget=self.color_range, position="bottomright"
        )
        self.m.add_control(widget_control)

        locations = widgets.Dropdown(
            options=self.BBOXes.keys(),
            value=list(self.BBOXes.keys())[0],
            description="Location:",
        )
        locations.observe(self.zoom_to_location, "value")

        widget_control = ipyleaflet.WidgetControl(
            widget=locations, position="topright")
        self.m.add_control(widget_control)

        self.m.observe(self.zoom_out_to_target_bounds, "bounds")

        def compute_style(feature, colormap, choro_data):
            return {
                "fillColor": colormap(choro_data),
                "color": "white",
                "weight": random.randint(1, 3),
            }

        self.layer.style_callback = compute_style

    def getMap(self):
        return self.m
    
    
if __name__ == "__main__":
    
    BBOXes = {
    "Heidelberg" : "8.6581,49.3836,8.7225,49.4363",
    "Pokhara":"83.9142,28.1693,84.0775,28.2687",
    "Kathmandu" : "85.26810609,27.66794937,85.3755574,27.75133958",
    "Manila":"120.94169186,14.55699989, 121.0261672,14.63900265"}
    TIME_MONTHLY = "2009-11-01/2020-06-01/P1M"
    FILTER = ["building=*","highway=*","amenity=* and name=*"]
    path_grid = r"C:\Users\Clemens Langer\Desktop\Blogpost\ohsome-examples\python\jupyter-notebooks\data\map_stored.json"
    path_style = r"C:\Users\Clemens Langer\Desktop\Blogpost\ohsome-examples\python\jupyter-notebooks\data\style_stored.json"
    m = ChoroplethMap()
    m.getTimeChoroplethMap(BBOXes,FILTER,TIME_MONTHLY,size=1, tags=False)
    m.saveJSON(path_style,path_grid)
    