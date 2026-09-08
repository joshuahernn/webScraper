How to Run

Before running the crawler, make sure all required libraries are installed.

Required imports:

import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import deque
from urllib.parse import urljoin, urlparse
import os

- pip install requests
- pip install beautifulsoup4
- pip install pandas
- pip install lxml

To run the crawler:

python webScrapper.py -- 

Once the program starts, enter a valid HTTPS URL. If the format is incorrect, you will be prompted again.

The first URL is used as the seed page. From there, the crawler collects text, follows discovered links, checks robots.txt, and continues until the queue is empty or the page limit is reached.

CSV's for url + text output and adjacency matrix will be produced in where program is executed.