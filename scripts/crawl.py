#!/usr/bin/env python

import lxml
import argparse
from lxml.html import fromstring
import json
from utils import download, write
import re

parser = argparse.ArgumentParser(description='')

ROOT = "http://boston-iframe.r.mikatiming.de/2013/"
BASE_URL = "http://boston-iframe.r.mikatiming.de/2013/?page=%d&event=R&pid=search&search[club]=&search[age_class]=&search[sex]=&search[nation]=&search[state]=&search_sort=name"
all_runners = []

#get the links to each page
def crawl():
    for n in range(1075):
        print BASE_URL % n
        this_page = []
        page = fromstring(download(BASE_URL % n, "%d.html" % n))
        table = page.xpath("//table[@class='list-table']/tbody")[0]
        for runner in table.xpath("tr"):
            name = runner.xpath("td/a/text()")[0]
            info = [x.strip().encode("ascii") for x in runner.xpath("td/text()")[4:8]]
            data = {
                "name": name,
                "bib": info[0],
                "half": info[1],
                "finish_net": info[2],
                "finish_gun": info[3],
                "url": runner.xpath("td/a/@href")[0]
            }
            this_page.append(data)
            all_runners.append(data)
        write(json.dumps(this_page, indent=2), "search/data-%d.json" % n)
    write(json.dumps(all_runners, indent=2), "all_runners.json")

#visit each runner's page and download it
def times(start=0, end=27000):
    runners = json.load(open("data/all_runners.json", "r"))
    c = start
    for runner in runners[start:end]:
        url = ROOT + runner['url']
        pid = re.findall("idp=(.*?)&", url)[0]
        info = download(url, "runners/%s.html" % pid)
        c += 1
        if c % 25 == 0:
            print c, pid

def main():
    parser.add_argument("command", metavar="STR", type=str, default="crawl",
            help="'crawl' for collecting names, 'times' for crawling individual runners")
    parser.add_argument("-n", "--start", metavar="INTEGER", dest="start", type=int, default=0)
    parser.add_argument("-m", "--end", metavar="INTEGER", dest="end", type=int, default=27000)
                        
    args = parser.parse_args()    
    
    if (args.command == "crawl"):
        crawl()
    elif (args.command == "times"):
        times(args.start, args.end)

if __name__ == "__main__":
    main()