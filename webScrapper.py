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

from bs4 import beautifulSoup


def webScrapper ():
    return 



