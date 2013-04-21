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

#extract split times from HTML for one runner's page
def analyze(pid):
    runner = {}
    page = fromstring(open("cache/runners/%s" % pid, "r").read())
    tables = page.xpath("//table[@class='list-table names']/tbody")    
    for table in tables:
        data = table.xpath("tr")
        for datum in data:
            info = datum.xpath("td/text()")
            if len(info) == 1:
                runner[info[0]] = None
            else:
                runner[info[0]] = info[1:]

    if "5K" not in runner or runner["5K"][0] == "-":
        return None

    first_marker = runner["5K"]

    for item in runner:
        if runner[item]:
            runner[item] = runner[item][0]

    t = [int(x) for x in re.findall("\d+", first_marker[1])]

    for post in posts:
        if post not in runner:
            runner[post] = None
        else:
            runner[post] = (runner[post], timestamp_to_mins(runner[post]))

    runner["time total (gun)"] = (runner["time total (gun)"], timestamp_to_mins(runner["time total (gun)"]))
    runner["time total (net)"] = (runner["time total (net)"], timestamp_to_mins(runner["time total (net)"]))

    #try to impute start time
    #elif runner["10K"][1] and runner["5K"][1]:
    runner["0K"] = ["", runner["5K"][1] - t[1]]
    runner["0K"][0] = mins_to_timestamp(runner["0K"][1])
    #print t, runner["bib number"], runner["0K"]
            
    write(json.dumps(runner, indent=2, sort_keys=True), "times/%s.json" % pid)
    return runner    

#combine into one (large) files
def align():
    every = []
    c = 0
    for pid in os.listdir("cache/runners/"):
        if pid[0] == ".":
            continue
        inf = analyze(pid)
        if inf:
            every.append(inf)
            c += 1
        if c % 100 == 0:
            print c, pid
    write(json.dumps(every), "times/all.json")

def combine():
    roster = defaultdict(list)    
    total = [defaultdict(int) for x in range(segments)]
    starts = {}
    data = json.load(open("data/times/all.json", "r"))
    duds = 0
    co = 0
    for runner in data:
        #print runner["bib number"], runner["5K"]
        #see if he/she showed up
        if "5K" not in runner or not runner["5K"][1]:
            duds += 1
            continue
        co += 1
        if co % 100 == 0:
            print co
        #placement will represent which marker he/she was closest to at each interval
        placement = ["0" for x in range(segments)]
        #stamps is the timestamps scraped from BAA.org
        stamps = [runner[x][1] for x in posts]
        marker = 0

        #fill in placement with most recent split time (intervals of 5K + half and finish)
        for c in range(segments):
            if c > 0:
                placement[c] = placement[c - 1]
            if marker < len(posts) and stamps[marker] and stamps[marker] < c * INTERVAL:
                placement[c] = posts[marker]
                marker += 1

        placement = [int(x.replace("K", "").replace("Finish Net", "42").replace("HALF", "21")) for x in placement]
        #print placement
        #print runner["bib number"]
        
        #calculate interpolations between kilometer marks

        #start at appropriate place for offset in starting point
        c = int(round(runner["0K"] / INTERVAL))
        while c < len(placement):
            if placement[c] == placement[-1] or c >= len(placement) - 2:
                break
            t = 1
            while c+t < len(placement) and placement[c + t] == placement[c]:
                t += 1
            #print c, t, placement[c+t], placement[c]
            step = float(placement[c+t]-placement[c]) / t
            for i in range(1, t):
                placement[c + i] = int(math.floor(placement[c + i] + i * step))
            c += t

        #print placement
        key = "_".join([str(x) for x in placement])
        roster[key].append(runner["bib number"])

        for c in range(segments):
            total[c][placement[c]] += 1
        

    write(json.dumps(roster, indent=2), "times/condensed.json")
    write(json.dumps(total, indent=2), "times/condensed_time.json")
    
def test():
    data = json.load(open("data/times/all.json", "r"))
    last = defaultdict(int)
    roster = defaultdict(list)
    for runner in data:
        for c in range(len(posts) - 1, -1, -1):
            if runner[posts[c]][1]:
                last[posts[c]] += 1
                roster[posts[c]].append(runner["bib number"])
                break

    print last
    write(json.dumps(roster, indent=2), "times/test.json")

#align()
test()
#combine()
