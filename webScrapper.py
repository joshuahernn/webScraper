""" **Structure:** 
- User-agent [^1]
	- 2 places where we'll look at this term
		1. HTTP User-Agent: When our scraper makes an HTTP request, it can send a user-agent header identifying itself. 
		2. Robots.txt: Our scraper will end up reading the domains robots.txt, if has our certain crawler and a disallow rule, we'll have to follow it. 

- Disallow [^2]
	1.  If a disallow shows: Disallow /admin/, this means that all crawlers should avoid URLS under /admin/, but other URLs would be accessible.
	2. If it shows just a '/', it means that we cannot crawl anywhere on the site, whereas if we have nothing there, we can crawl anywhere on the site.
	
- Uses only blank lines to separate different user-agent
	1. We can have multiple disallows, and each line would be another path the crawler should avoid.

- One directory per line.
	1. Each directory would be separated with a disallow.

- Once you have collected the data, it must be stored in a directory

""" 

import requests # requests import is able to take care of the TCP connection and do HTTP get, the server sends us an HTTP responses, and the body of that response contains HTML. 
from bs4 import BeautifulSoup

url = "https://www.NBA.com" 
headers = {
    'user-agent': 'my-app/0.0.1'
    }

r = requests.get(url, headers=headers)

r = requests.options("https://www.NBA.com")

r.headers.get('content-type')

print(r.headers)

# Currently, this is able to return the headers of the domain that we select. The header is returned in raw HTML, so our next step would be to use BS4 to process this the HTML
# TODO: 1. Check for status codes, check for roboot.txt, What to do when we get back JSON, check for what body of text you recieved.

# 8/27/26: Read over more documentiaion

 







'''
def webScrapper ():
    return 

'''




