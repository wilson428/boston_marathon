from pprint import pprint
import datetime
import errno
import htmlentitydefs
import os
import os.path
import re
import sys

from pytz import timezone

# read in an opt-in config file for changing directories and supplying email settings
# returns None if it's not there, and this should always be handled gracefully

eastern_time_zone = timezone('US/Eastern')


def log(object):
    if isinstance(object, (str, unicode)):
        print object
    else:
        pprint(object)


def format_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return eastern_time_zone.localize(obj.replace(microsecond=0)).isoformat()
    elif isinstance(obj, str):
        return obj
    else:
        return None


def write(content, destination, dir=None):
    if not dir:
        dir = data_dir()
    path = os.path.join(dir, destination)
    mkdir_p(os.path.dirname(path))
    f = open(path, 'w')
    f.write(content)
    f.close()

def read(destination):
    if os.path.exists(destination):
        with open(destination) as f:
            return f.read()

# de-dupe a list, taken from:
# http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def uniq(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


# mkdir -p in python, from:
# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def xpath_regex(doc, element, pattern):
    return doc.xpath(
        "//%s[re:match(text(), '%s')]" % (element, pattern),
        namespaces={"re": "http://exslt.org/regular-expressions"})


# taken from http://effbot.org/zone/re-sub.htm#unescape-html
def unescape(text):

    def remove_unicode_control(str):
        remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
        return remove_re.sub('', str)

    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is

    text = re.sub("&#?\w+;", fixup, text)
    text = remove_unicode_control(text)
    return text


##### Downloading
#the os.getcwd() (current working directory) is for file system access in Cloud9IDE


import scrapelib
scraper = scrapelib.Scraper(requests_per_minute=120, follow_robots=False, retry_attempts=3)


# uses config values if present
def cache_dir():
    return os.getcwd() + "/cache"

# uses config values if present
def data_dir():
    return os.getcwd() + "/data"

# uses config values if present
def log_dir():
    return os.getcwd() + "/log"

def download(url, destination=None, force=False, options=None):
    if not options:
        options = {}
        
    if not destination:
        destination = url.split("//")[1].replace("/", "-")
    cache_path = os.path.join(cache_dir(), destination)

    if not force and os.path.exists(cache_path):
        if options.get('debug', False):
            log("Cached: (%s, %s)" % (cache_path, url))
        with open(cache_path, 'r') as f:
            body = f.read()
    else:
        try:
            if options.get('debug', False):
                log("Downloading: %s" % url)
            response = scraper.urlopen(url)
            body = response.encode('utf-8')
        except scrapelib.HTTPError:
            log("Error downloading %s" % url)
            return None

        # don't allow 0-byte files
        if (not body) or (not body.strip()):
            return None

        # cache content to disk
        write(body, cache_path)

    return body