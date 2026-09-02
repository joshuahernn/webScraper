import requests # requests import is able to take care of the TCP connection and do HTTP get, the server sends us an HTTP responses, and the body of that response contains HTML. 
from bs4 import BeautifulSoup
import pandas as pd
import networkx as nx # TODO: this is for requirement 3



def get_url ():

	entered_url = input("Please enter the full URL of the site you would like to scrape in the HTTPS format: ")
	print(f"Trying to access: ", entered_url)

	while not entered_url.lower().startswith("https://www."):
		entered_url = input("Error: Please enter the full URL with the HTTPS format: ")
		
		
	headers = {
		'user-agent': 'Mozilla/5.0'
		}


	connection_attempts = 0
	max_attempts = 5
	
	client_sucess = [200]
	client_errors = [400, 401, 403, 404, 429]
	server_errors = [500, 502, 503, 504]

	while connection_attempts < max_attempts: # usually we can't connect off of first try. so just for safety ;p
		
		r = requests.head(entered_url, allow_redirects=True) 
		r = requests.get(entered_url, headers=headers)
		# print(f"Trying to access: ", entered_url)

		connection_attempts += 1
	

	if r.status_code in client_sucess:
		# print(soup.get_text()) 
		# print(r.status_code) # FOR DEBUG
		print("Connection established: Scraping HTML and URL")
		return r

	# if any error is returned / forbidden, prompt the user again 
	if r.status_code in client_errors or r.status_code in server_errors:
		input("You cannot access this site, please try another: ")
	
	# soup = BeautifulSoup(r.text, 'lxml')
	
	
	
def save_text(r):  # we need to save the URL and the body of text here.

	soup = BeautifulSoup(r.text, 'lxml')

	readable_html = soup.get_text()
	readable_url = r.url

	# we need to grab href here for other links / redirects



	# print(r.url)
	# print(readable_html)
	return readable_url, readable_html


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

	collected_rows= []

	collected_rows.append({
        "URL": url,
        "Text": text
    })

	df = pd.DataFrame(collected_rows)
	df.to_csv('output.csv', index=False)


def redirect_urls():
	pass 




def main():
	r = get_url()
	
	if r is not None:
		create_table()
		url, text = save_text(r)
		fill_table(url, text)



if __name__ == "__main__":
    main()



''' 

# 8/31/2026
restructured design and encapsulated all functions. we still need to implement the fill table function as we want to keep the fill 
and create table functions seperately. 

after we do this, 
2. handle redirects logic (href)
3. handle crashes.
4. handle hard limits. 


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







