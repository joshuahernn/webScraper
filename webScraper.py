import requests # requests import is able to take care of the TCP connection and do HTTP get, the server sends us an HTTP responses, and the body of that response contains HTML. 
from bs4 import BeautifulSoup
import pandas as pd
from collections import deque
from urllib.parse import urljoin, urlparse
import os 

def check_robots(base_url, path, robots_cache):

    robots_url = base_url + "/robots.txt" 

    if base_url in robots_cache:  # if we have already gotten the domain's robot.txt
        lines = robots_cache[base_url]  # use the rules already saved

    else:

        try:
            response = requests.get(robots_url, timeout=5)

        # catch errors to prevent crashes
        except requests.exceptions.Timeout:
            print("robots.txt timed out:", robots_url)
            return False

        except requests.exceptions.ConnectionError:
            print("Could not connect to robots.txt:", robots_url)
            return False

        except requests.exceptions.InvalidURL:
            print("Invalid robots.txt URL:", robots_url)
            return False

        if response.status_code != 200:
            print("Could not read robots.txt")
            return False

        lines = response.text.splitlines() 

        robots_cache[base_url] = lines # store robot.txt into cache


    reading_rules = False

    for line in lines:

        line = line.strip()

        if line.lower() == "user-agent: *": # all web crawlers
            reading_rules = True

        elif line.lower().startswith("user-agent:"):
            reading_rules = False

        elif reading_rules and line.lower().startswith("disallow:"):

            disallowed_path = line.split(":", 1)[1].strip() # take each disallowed paths

            if disallowed_path and path.startswith(disallowed_path): # check path for disallowed paths
                return False

    return True


def get_url(robots_cache): # function only runs once, the redirect logic takes over after user input

	entered_url = input("Please enter the full URL of the site you would like to scrape in the HTTPS format: ") 
	print("Trying to access: ", entered_url)

	while not (entered_url.lower().startswith("https://www.") or entered_url.lower().startswith("https://")): # user input logic 
		entered_url = input("Error: Please enter the full URL with the HTTPS format: ")
		
		
	headers = {
		'user-agent': 'Mozilla/5.0'
		}

	client_sucess = [200]
	client_errors = [400, 401, 403, 404, 429]
	server_errors = [500, 502, 503, 504] # server errors included in case of crashes.

	if not check_robots(entered_url, "/", robots_cache):
		print("robots.txt does not allow this site to be crawled.")
		return None
			 

	try:
		r = requests.get(entered_url, headers=headers, timeout = 5) #timeout will error out, but we need to save the csv before we crash

	except requests.exceptions.Timeout: 
		print("This URL has timed out, resetting queue")

    #todo: put other errors here just in case. reprompt user to restart is easier though.

	if r.status_code in client_sucess:
		# print(soup.get_text()) 
		# print(r.status_code) 
		print("Connection established: Scraping HTML and URL")
		return r

	# if any error is returned / forbidden, prompt the user again 
	if r.status_code in client_errors or r.status_code in server_errors:
		input("You cannot access this site, please try another: ")

    
def save_text(r): # 

    soup = BeautifulSoup(r.text, 'lxml')

    main = soup.find("main") # main body of html

    if main:
        readable_html = main.get_text(" ", strip=True)
    else:
        readable_html = soup.body.get_text(" ", strip=True) # if there is no main body, just pull all text

    readable_url = r.url

    return readable_url, readable_html, soup


def create_adj_table(visited, connections):

	url_index = {}

	for i in range(len(visited)): # row and column belong for each URL
		url_index[visited[i]] = i

	matrix = [] # create an empty adjacency matrix filled with zeros

	for i in range(len(visited)):

		row = []

		for j in range(len(visited)):
			row.append(0) # set 0 for every url

		matrix.append(row)


	for connection in connections:  # go through each connection between pages

		current_url = connection[0] 
		new_url = connection[1] 

		if current_url in url_index and new_url in url_index:  # only record connections between visited pages

			current_index = url_index[current_url]
			new_index = url_index[new_url]

			matrix[current_index][new_index] = 1 # if there is a path from the page of that origin, 1

	return matrix

      
def fill_table(url, text): # export url and text to csv

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

def save_adj_table(visited_urls, matrix): # export adjancent matrix to csv

    collected_rows = []

    for i in range(len(visited_urls)):

        row = {
            "URL": visited_urls[i]
        }

        for j in range(len(visited_urls)):
            row[str(j)] = matrix[i][j]

        collected_rows.append(row)

    df = pd.DataFrame(collected_rows)

    df.to_csv("adjacency.csv", index=False)


def redirect_urls(soup, url, robots_cache):

    queue = deque()

    max_pages = 5000
    pages_checked = 0

    visited = set()
    visited_urls = []
    connections = []

    visited.add(url)
    visited_urls.append(url)

    # grab links from first page
    for link in soup.find_all("a"):

        href = link.get("href")

        if href is not None:
            full_url = urljoin(url, href)

            if full_url.startswith("http://") or full_url.startswith("https://"):

                connections.append((url, full_url))

                if full_url not in visited and full_url not in queue:
                    queue.append(full_url)

    # go through the queue, check robots.txt, and stop at the page limit
    while queue and pages_checked < max_pages:

        next_url = queue.popleft()

        if next_url in visited:
            continue

        parsed_url = urlparse(next_url)

        base_url = parsed_url.scheme + "://" + parsed_url.netloc
        path = parsed_url.path

        if not check_robots(base_url, path, robots_cache):
            print("robots.txt does not allow:", next_url)
            continue

        visited.add(next_url)
        visited_urls.append(next_url) 

        print("Redirecting to:", next_url)

        # grab the page, get the text, and fill the table
        try:
            r = requests.get(next_url, timeout=5)

            if r.status_code == 200:

                print("Successfully connected to:", r.url)

                new_soup = BeautifulSoup(r.text, 'lxml')

                main = new_soup.find("main")

                if main:
                    text = main.get_text(" ", strip=True)

                elif new_soup.body:
                    text = new_soup.body.get_text(" ", strip=True)

                else:
                    print("No readable body found:", r.url)
                    continue
                
                fill_table(r.url, text)

                pages_checked += 1

                # grab links from this new page, add new ones to queue
                for link in new_soup.find_all("a"):

                    href = link.get("href")

                    if href is not None:

                        new_url = urljoin(r.url, href)

                        if new_url.startswith("https://") or new_url.startswith("http://"):

                            connections.append((r.url, new_url))

                            if new_url not in visited and new_url not in queue:
                                queue.append(new_url)

        # error checks so we don't crash
        except requests.exceptions.Timeout:
            print("URL timed out:", next_url)

        except requests.exceptions.ConnectionError:
            print("Connection failed:", next_url)   

        except requests.exceptions.InvalidURL:
            print("Invalid URL:", next_url)

    # create the matrix and save it to the csv
    matrix = create_adj_table(visited_urls, connections) 
    save_adj_table(visited_urls, matrix)

    return matrix

def main():

	robots_cache = {}

	r = get_url(robots_cache)
	
	if r is not None: 
		url, text, soup = save_text(r)
		fill_table(url, text)
		redirect_urls(soup, url, robots_cache)



if __name__ == "__main__":
    main()

'''
When crawling, you need to collect multiple things. 
1. First, the raw text of the page.  This means you don’t want the entire HTML file, but rather, just the important bits of text. 
2. Second, the URL of the page you got the URL from. You will need the URL to make sure you don’t crawl the same page twice. You will also need the URL to ensure you can retrieve the original page again. 
3. Finally, when crawling, keep an adjacency matrix so you know which pages link to others. This will be directed, as a page might point to another, but not visa versa.
'''

