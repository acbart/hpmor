#!/usr/bin/python
import sys, time, os, random, re, urllib
import argparse
import requests
import subprocess
from bs4 import BeautifulSoup
def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--volumes", help="A comma separated list of the chapters to break on (e.g. 1,6,10,42).")
parser.add_argument("-c", "--cached", help="If present, we will use the locally available files only.", action="store_true")
parser.add_argument("-o", "--output", help="If present, this is where the pdf files will be placed.")
args = parser.parse_args()

if args.output:
    destination = args.output + "/"
else:
    destination = ""

roman_numerals = { 1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII",
                   8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII"}

def get_latest_chapter():
    hpmor_content = requests.get("http://www.hpmor.com").content
    hpmor_content_cleaned = removeNonAscii(hpmor_content).encode('ascii', 'ignore')
    hpmor = BeautifulSoup(hpmor_content_cleaned)
    latest_chapter_url = hpmor.find(id = "latest-chapter").find("a")["href"]
    return int(re.search("(\d+)", latest_chapter_url).group(0))

def get_chapter_content(chapter):
    hpmor_content = requests.get("http://www.hpmor.com/chapter/"+str(chapter)).content
    hpmor = BeautifulSoup(hpmor_content)
    return hpmor

def cache_file(id, raw):
    with open("cache/{}.html".format(id), 'w') as file:
        file.write(raw.prettify().encode('utf8'))
        
def load_file(path):
    file = open(path, 'r')
    raw = file.read().decode('utf8')
    file.close()
    return raw
    
def load_cached_file(id):
    return load_file("cache/{}.html".format(id))
    
sequence_breaks = ("$", "*", "%", ">", "`")
hr_block = """<hr noshade="noshade" size="1"/>"""
def parse_chapter(raw, id):
    """
    consumes raw html of page
    returns title, body
    """
    raw = BeautifulSoup(raw)
    title = raw.find(id = "chapter-title").text.strip().replace("\n", " ")
    title = re.findall(r"Chapter (\d+): (.*)", title)[0][1]
    body = raw.find(id = "storycontent").contents
    body =  BeautifulSoup(unicode("").join([unicode(x) for x in body])).prettify()
    # 22 needs its first THREE sections chomped
    if id in (33, 58, 64, 85, 88, 96) or (1 <= id <= 30):
        body = chomp_start(body)
    while hr_block in body: # because who cares about quadratic runtime, amirite?
        body = body.replace(hr_block,  """<p class="sequence-break">{}</p>""".format(random.choice(sequence_breaks)), 1)
    return title, body
    
first_chapter = 1
last_chapter = get_latest_chapter()

if args.volumes is None:
    books = [(first_chapter, last_chapter)]
else:
    chapters = [int(chapter.strip()) for chapter in args.volumes.split(",")]
    books = [(start, finish-1) for start, finish in zip(chapters, chapters[1:]+[1+last_chapter])]

if not args.cached:
    print "Downloading",
    for chapter_id in xrange(first_chapter, 1+last_chapter):
        cache_file(chapter_id, get_chapter_content(chapter_id))
        
header = load_file("hpmor-header.html")
footer = load_file("hpmor-footer.html")
chapter_pattern = unicode("""<div class="chapter"><h2 id="{0}">Chapter {0}</h2><h3>{1}</h3>
{2}
</div>""")

hr_pattern = re.compile("(.*?<hr noshade=\"noshade\" size=\"1\"/>)", re.DOTALL)
def chomp_start(text):
    return hr_pattern.sub("", text, 1)
        
for volume, (start, finish) in enumerate(books, 1):
    print "Generating volume", volume
    html_filename = "hpmor-{}-{}.html".format(start, finish)
    pdf_filename = "hpmor-{}-{}.pdf".format(start, finish)
    with open(html_filename, "w") as file:
        contents = header % {"volume": roman_numerals[volume],
                             "start": start, "finish": finish}
        for id in xrange(start, finish+1):
            title, body = parse_chapter(load_cached_file(id), id)
            contents += chapter_pattern.format(id, title, body)
        contents += footer
        file.write(contents.encode('utf8'))
    subprocess.call(["prince",html_filename,destination+pdf_filename, "--javascript"]);
    