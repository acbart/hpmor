#!/usr/bin/python
import sys, time, os, random, re, urllib
import argparse
import requests
from bs4 import BeautifulSoup
def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--volumes", help="A comma separated list of the chapters to break on (e.g. 1,6,10,42).")
parser.add_argument("-c", "--cached", help="If present, we will use the locally available files only.", action="store_true")
args = parser.parse_args()

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
    
def parse_chapter(raw):
    """
    consumes raw html of page
    returns title, body
    """
    return raw.find(id = "chapter-title"), raw.find(id = "storycontent")
    
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
        print chapter_id,
        cache_file(chapter_id, *get_chapter_content(chapter_id))
        
header = load_file("hpmor-header.html")
footer = load_file("hpmor-footer.html")
        
for start, finish in books:
    with open("", "w") as file:
        
    
sys.exit()

f = open('hpmor'+suffix+'.html', 'w')
header = open('hpmor-header.html', 'r')
f.write(header.read())

titlere = re.compile('<div id="chapter-title">Chapter \\d+: (.*?)<', re.DOTALL);
contentre = re.compile("<div style='' class='storycontent' id='storycontent'>(.*?)</div>\n<div id=\"nav-bottom\"", re.DOTALL);
garbagequotestr = chr(226)+chr(128)+chr(175)

i = start
while end == 0 or i <= end:
	url = 'http://hpmor.com/chapter/'+str(i)
	print url
	response = urllib.urlopen(url)
	if response.getcode() == '404':
		break
	html = response.read()
	title = titlere.search(html).group(1)
	content = contentre.search(html).group(1)
	content = content.replace(garbagequotestr, '')
	
	f.write('<div class="chapter">')
	f.write('<h2 id="'+str(i)+'">Chapter '+str(i)+'</h2>')
	f.write('<h3>'+title+'</h3>')
	f.write(content)
	f.write('</div>')
	i += 1
	time.sleep(1+3*random.random())

footer = open('hpmor-footer.html', 'r')
f.write(footer.read())

print 'done'


#import subprocess

#subprocess.call(["prince","foo.xml","bar.pdf"]);