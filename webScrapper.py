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
import networkx as nx

url = "https://www.NBA.com" 
headers = {
    'user-agent': 'my-app/0.0.1'
    }

r = requests.head(url, allow_redirects=True) #
r = requests.options("https://www.NBA.com/robots.txt")
r.headers.get('content-type') 

soup = BeautifulSoup(r.text, 'lxml')

# print(soup.get_text()) # TODO: Store this 

# for link in soup.find_all('a'): # TODO: Store this
 #   print(link.get('href'))


# print(r.status_code) FOR DEBUG


client_error = ["400","401","403","404","429"] # most common is going to be 403: forbidden
lines = soup.prettify().splitlines()

client_errors = [400, 401, 403, 404, 429]
server_errors = [500, 502, 503, 504]


if r.status_code in client_errors :
    print("Client Error has been found:",r.status_code)  # web crawler stops, should redirect or kill process.
if r.status_code in server_errors :
    print("Server Error has been found:",r.status_code)



'''
When crawling, you need to collect multiple things. 
1. First, the raw text of the page.  This means you don’t want the entire HTML file, but rather, just the important bits of text. 
2. Second, the URL of the page you got the URL from. You will need the URL to make sure you don’t crawl the same page twice. You will also need the URL to ensure you can retrieve the original page again. 
3. Finally, when crawling, keep an adjacency matrix so you know which pages link to others. This will be directed, as a page might point to another, but not visa versa.
'''

'''
# 8/27/26 notes: 
We are able to ping a domain and recieve a status code. I have set flags to come back for when we get stopped,
but I need to wrap this around redirection / stop logic so when the crawler gets stopped it doesn't crash.

The start of requirements #1 and #2 are there, but I need to figure out how to use pandas to store that into a dictionary.

'''







