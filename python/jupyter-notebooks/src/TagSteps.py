# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 10:28:46 2020

@author: Clemens Langer
"""


import requests 
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import sys
import warnings
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)


def get_time_stamp_list(date1,date2):
    '''returns a list dates off all monthly intervalls between to timestamps'''
    start_year = [int(i) for i in date1.split("T")[0].split("-")]
    end_year = [int(i) for i in date2.split("T")[0].split("-")]
    if end_year[0:2:] == start_year[0:2:]:
        return ["{}-{:02d}-01T00:00:00".format(end_year[0],end_year[1])]
    timestamps = []
    for i in range(start_year[0],end_year[0]+1):
        if i == start_year[0]:
             start_month = start_year[1]
        else:
            start_month = 1
        if  i != end_year[0]:
            end_month = 12
        else:
            end_month = end_year[1]
        for o in  range(start_month,end_month+1):
            timestamps.append("{}-{:02d}-01T00:00:00".format(i,o))
    return timestamps


def plot_steps(ax,filter,location,BBOXes,c,len_filter,o,len_location,TIME, STEPS):
    '''plots the steps for a certain filter / locations'''
    URL = "https://api.ohsome.org/v1"
    
    LINE_STYLE = ["-","--","-.",":"]
    COLORS = ["C0","C1","C2","C3"]
    time = TIME.replace("/P1M","").replace("/",",")
    data = {"time":time, "filter":filter, "bboxes":BBOXes[location],"properties":"tags"}  
    with requests.post(URL+"/elementsFullHistory/centroid",data) as response:
         body = response.json()
    df = pd.DataFrame()
    tags = {}
   
    
    if "features" in body:
        for i, feature in enumerate(body["features"]):
            sys.stdout.write("\r finished {} out of {} filter for {} out of  {} locations | {} / {} Objects".format(o, len_filter,c +1,len_location,i,len(body["features"])))
            sys.stdout.flush()
            
            try:
                timestamps = get_time_stamp_list(feature["properties"]['@validFrom'],feature["properties"]["@validTo"])
                for timestamp in timestamps:
                    if timestamp not in tags:
                        tags[timestamp] = [len(feature["properties"])-3]
                    else:
                        tags[timestamp].append(len(feature["properties"])-3)
            except:
                print(feature)
                continue
    else: 
        print(body)
        sys.exit(1)
    max_count = 0
    for ts, values in tags.items():
        max_count = max(max_count, len(values))
    for s ,step in enumerate(STEPS):
       series = pd.Series({timestamp:len([i for i in tag_lens if i >= step])/len(tag_lens) for timestamp, tag_lens in tags.items()})
       df["{}_{}_{}".format(location,filter,step)]= series
       df.set_index(pd.to_datetime(df.index),inplace=True)
       df["{}_{}_{}".format(location,filter,step)].plot(linestyle=LINE_STYLE[s],c=COLORS[c],ax=ax,legend=True,title=filter)

def level3(BBOXes,time):
    ''' plots the facilities for locations '''
    COLORS = ["C0","C1","C2","C3"]
    URL = "https://api.ohsome.org/v1"
    level_3_tags = ["amenity=water_point","amenity=drinking_water","amenity=place_of_whorship","amenity=clinic","amenity=doctors","amenity=dentist","healthcare=*","amenity=school","amenity=college","amenity=university","amenity=kindergarden","amenity=childcare","bridge=*","tunnel=*"]
    filter = " or ".join(level_3_tags)
    fig, axs = plt.subplots(figsize=(15,7))
    for c,(location, bbox) in enumerate(BBOXes.items()):
        data = {"time":time, "filter":filter, "bboxes":bbox} 
        response = requests.post(URL+"/elements/count",data)
        df = pd.DataFrame()
        series = pd.Series({i["timestamp"]:i["value"] for i in response.json()["result"]})
        df[location]= series
        df.set_index(pd.to_datetime(df.index),inplace=True)
        df[location].plot(c=COLORS[c],legend=location,title="Level 3 Count",ax=axs)

def pointsOfIntrest(BBOXes,time):
    ''' plots the facilities for locations '''
    COLORS = ["C0","C1","C2","C3"]
    URL = "https://api.ohsome.org/v1"
    filter = "name=* and amenity=*"
    fig, axs = plt.subplots(figsize=(15,7))
    for c,(location, bbox) in enumerate(BBOXes.items()):
        data = {"time":time, "filter":filter, "bboxes":bbox} 
        response = requests.post(URL+"/elements/count",data)
        df = pd.DataFrame()
        series = pd.Series({i["timestamp"]:i["value"] for i in response.json()["result"]})
        df[location]= series
        df.set_index(pd.to_datetime(df.index),inplace=True)
        df[location].plot(c=COLORS[c],legend=location,title="Points of Intrest Count",ax=axs)  

def geometry(BBOXes,TIME):
    ''' plots the geometrical completeness of roadnetwork / building count for locations '''
    COLORS = ["C0","C1","C2","C3"]
    URL = "https://api.ohsome.org/v1"
    filter = "highway=*"
    fig, axs = plt.subplots(2,figsize=(15,10))
    fig.suptitle("Geometrical development")
    for c,(location, bbox) in enumerate(BBOXes.items()):
        data = {"time":TIME, "filter":filter, "bboxes":bbox} 
        response = requests.post(URL+"/elements/length",data)
        df = pd.DataFrame()
        series = pd.Series({i["timestamp"]:i["value"] for i in response.json()["result"]})
        df[location]= series
        df.set_index(pd.to_datetime(df.index),inplace=True)
        df[location].plot(c=COLORS[c],legend=location,title="Total lenght of Roadnetwork [km]",ax=axs[0])
    filter = "building=*"
    for c,(location, bbox) in enumerate(BBOXes.items()):
        data = {"time":TIME, "filter":filter, "bboxes":bbox} 
        response = requests.post(URL+"/elements/count",data)
        df = pd.DataFrame()
        series = pd.Series({i["timestamp"]:i["value"] for i in response.json()["result"]})
        df[location]= series
        df.set_index(pd.to_datetime(df.index),inplace=True)
        df[location].plot(c=COLORS[c],legend=location,title="Total count of buildings",ax=axs[1])


def plotTagcompletness(BBOXes,FILTER,TIME,STEPS=[0,3,5,10]):
    import sys
    COLORS = ["C0","C1","C2","C3"]
    
    fig, axs = plt.subplots(len(FILTER),figsize=(len(FILTER)*5,15))
    fig.suptitle("Portion of objects containing a minimum number of Tags")
    for c,location in enumerate(BBOXes.keys()):
        for o, filter in enumerate(FILTER):
            
            sys.stdout.write("\r finished {} out of {} filter for {} out of  {} locations |  waiting for response".format(0,len(FILTER),c+1,len(BBOXes)))
            sys.stdout.flush()
            plot_steps(axs[o],filter,location,BBOXes,c,len(FILTER),o,len(BBOXes),TIME,STEPS)
        


