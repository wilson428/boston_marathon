import re
import json
import lxml
from lxml.html import fromstring
from utils import write
import os
import time
import math
from collections import defaultdict
import datetime

#list of indeces for splits
posts = ["%dK" % (5 * x) for x in range(1, 9)]
posts.insert(4, "HALF")
posts.append("Finish Net")

#interval for animations
INTERVAL = 5.0
ticks = 60 / INTERVAL
segments = int(ticks * 6 + 1)

def timestamp_to_mins(s):
    if not s:
        return None
    t = [int(x) for x in re.findall("\d+", s)]
    if not len(t):
        return None
    if t[0] < 10:
        t[0] += 12
    return 60 * (t[0] - 10) + t[1]    


def timestamp_to_secs(s):
    if not s:
        return None
    t = [int(x) for x in re.findall("\d+", s)]
    if not len(t):
        return None
    if t[0] < 10:
        t[0] += 12
    return 3600 * (t[0] - 10) + 60 * t[1] + t[2]

def mins_to_timestamp(s):
    if not s:
        return None

    merid = "AM"
    hours = 10 + floor(s / 60)
    mins = s % 60
    if hours >= 12:
        merid = "PM"
    if hours > 12:
        merid -= 12
    
    return hours + ":" + mins + " " + merid;   

def search(place, t):
    target = timestamp_to_secs(t)
    matches = []
    print target
    c = 0
    data = json.load(open("data/times/all.json", "r"))
    for runner in data:
        mytime = timestamp_to_secs(runner[place][0])        
        if mytime:
            diff = mytime - target
            if diff > 0 and diff < 60:
                c += 1
                matches.append({
                    "name": runner["Name"],
                    "finish": runner[place][0],
                    "bib": runner["bib number"]
                })

    print c, "matches"
    write(json.dumps(matches, indent=2), "matches.json")

#align()
search("Finish Net", "2:37:40 PM")
#combine()
