import requests # requests import is able to take care of the TCP connection and do HTTP get, the server sends us an HTTP responses, and the body of that response contains HTML. 
from bs4 import BeautifulSoup
import pandas as pd
import networkx as nx # TODO: this is for requirement 3
from collections import deque
from urllib.parse import urljoin
import os 

def check_robots(base_url, path): # use of ai, we need to simplify this. 

    robots_url = base_url + "/robots.txt"

    response = requests.get(robots_url)

    if response.status_code != 200:
        print("Could not read robots.txt")
        return False

    lines = response.text.splitlines()

    reading_rules = False

    for line in lines:

        line = line.strip()
        print(line)

        if line.lower() == "user-agent: *":
            reading_rules = True
            # print("Found robot.txt")
			 

        elif line.lower().startswith("user-agent:"):
            reading_rules = False

        elif reading_rules and line.lower().startswith("disallow:"):

            disallowed_path = line.split(":", 1)[1].strip()
            print(disallowed_path)

            if disallowed_path and path.startswith(disallowed_path):
                return False

	
    return True


def get_url ():

	entered_url = input("Please enter the full URL of the site you would like to scrape in the HTTPS format: ")
	print(f"Trying to access: ", entered_url)

	while not entered_url.lower().startswith("https://www."):
		entered_url = input("Error: Please enter the full URL with the HTTPS format: ")
		
		
	headers = {
		'user-agent': 'Mozilla/5.0'
		}


	# connection_attempts = 0
	# max_attempts = 5
	
	client_sucess = [200]
	client_errors = [400, 401, 403, 404, 429]
	server_errors = [500, 502, 503, 504]

	'''
	# todo: we need to enforce the robots.txt
		1. get the robot.txt, this is text file,
		2. parse through the file, looking for user-agent *.
		3. check the paths that we cannot travel
		4. store the paths we cannot travel.

		if the robot.txt says that we cannot travel any path '*', prompt the user, kill the process -> start with the beginning. 
	'''


	if not check_robots(entered_url, "/"):
		print("robots.txt does not allow this site to be crawled.")
		return None
	

	# while connection_attempts < max_attempts: # usually we can't connect off of first try. so just for safety ;p
		
	r = requests.head(entered_url, allow_redirects=True) 

	try:
		r = requests.get(entered_url, headers=headers, timeout = 5) #timeout will error out, but we need to save the csv before we crash

	except requests.exceptions.Timeout: 
		print("This URL has timed out, resetting queue")
		#todo: skip this url in the queue. (if its the first, restart the process, if there is a queue, skip the url)

	
		# print(f"Trying to access: ", entered_url)

		# connection_attempts += 1
	

	if r.status_code in client_sucess:
		# print(soup.get_text()) 
		# print(r.status_code) # FOR DEBUG
		print("Connection established: Scraping HTML and URL")
		return r

	# if any error is returned / forbidden, prompt the user again 
	if r.status_code in client_errors or r.status_code in server_errors:
		input("You cannot access this site, please try another: ")
	
	# soup = BeautifulSoup(r.text, 'lxml')
	
	


def save_text(r):

    soup = BeautifulSoup(r.text, 'lxml')

    main = soup.find("main")

    if main:
        readable_html = main.get_text(" ", strip=True)
    else:
        readable_html = soup.body.get_text(" ", strip=True)

    readable_url = r.url

    return readable_url, readable_html, soup




def create_table():

	df = pd.DataFrame(
    {
        "URL": [],
        "Text": []
    })

	df = df.astype({
		'URL': 'string', 
		'Text': 'string'
	})



def fill_table(url, text):

    collected_rows = []

    collected_rows.append({
        "URL": url,
        "Text": text
    })

    df = pd.DataFrame(collected_rows)

    df.to_csv(
        'output.csv',
        mode='a',
        header=not os.path.exists('output.csv'),
        index=False
    )


def redirect_urls(soup, url):

    queue = deque()

    max_pages = 500
    pages_checked = 0

    visited = set()

    # grab links from first page
    for link in soup.find_all("a"):

        href = link.get("href")

        if href is not None:
            full_url = urljoin(url, href)
            queue.append(full_url)


    while queue and pages_checked < max_pages:

        next_url = queue.popleft()

        if next_url in visited:
            continue

        visited.add(next_url)

        print("Redirecting to:", next_url)

        try:
            r = requests.get(next_url, timeout=5)

            if r.status_code == 200:

                print("Successfully connected to:", r.url)

                new_soup = BeautifulSoup(r.text, 'lxml')

                main = new_soup.find("main")

                if main:
                    text = main.get_text(" ", strip=True)
                else:
                    text = new_soup.body.get_text(" ", strip=True)

                fill_table(r.url, text)

                pages_checked += 1


                # NEW PART:
                # grab links from this new page
                for link in new_soup.find_all("a"):

                    href = link.get("href")

                    if href is not None:

                        new_url = urljoin(r.url, href)

                        if new_url not in visited:
                            queue.append(new_url)


        except requests.exceptions.Timeout:
            print("URL timed out:", next_url)



'''
#todo
	0.5. lets try setting a hard limit on the redirects so we know when to stop. this will be hard coded for now.
	1. pull hrefs from the save_text(r)
	2. we need to impelement a fifo queue here.
	3. check with the paths that we cannot travel to from get_urls.
	4. tell user that there is queue, would you like to continue, if not just save the one link, if yes, proceed with the queue.

	4.5 we're eventually going to pull more hrefs from travelling these redirects, store these in the queue, go through them as they go.
'''




def main():
	r = get_url()
	
	if r is not None:
		create_table()
		url, text, soup = save_text(r)
		fill_table(url, text)
		redirect_urls(soup, url)



if __name__ == "__main__":
    main()



''' 

# 8/31/2026
restructured design and encapsulated all functions. we still need to implement the fill table function as we want to keep the fill 
and create table functions seperately. 

after we do this, 
2. handle redirects logic (href)
3. handle crashes. (still need an idea for this)
4. handle hard limits. 


'''



'''
9/4/2026

1. fix logic for incorrectly typed urls

'''















































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







