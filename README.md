# Web Scraper — Python Web Crawler

A Python web scraper and crawler built with **Requests, Beautiful Soup, lxml, and Pandas**. Starting from a user-provided HTTPS seed URL, the program downloads page content, extracts readable text, discovers links, checks `robots.txt`, tracks visited pages, and records page-to-page relationships in an adjacency matrix.

## Overview

This project explores the core pieces of a web crawler without relying on a full crawling framework. The scraper handles HTTP requests with `requests`, parses returned HTML with Beautiful Soup and `lxml`, resolves links with Python's `urllib.parse` tools, and uses a queue to continue crawling newly discovered pages.

Each successfully processed page is stored in `output.csv` with its URL and extracted text. At the same time, the crawler tracks links between pages and writes those relationships to `adjacency.csv`, allowing the crawl to be viewed as a directed graph.

## Features

| Feature | Implementation |
| --- | --- |
| HTTPS seed URL | Prompts the user for a full `https://` URL before beginning the crawl |
| HTTP requests | Uses `requests` to send GET requests and retrieve webpage content |
| HTML parsing | Uses Beautiful Soup with the `lxml` parser |
| Text extraction | Collects readable text from successfully retrieved HTML pages |
| Link discovery | Finds links from anchor tags and resolves relative URLs |
| URL normalization | Uses `urljoin` and `urlparse` to work with complete URLs |
| Crawl queue | Uses `collections.deque` to process discovered URLs in order |
| Duplicate prevention | Tracks visited URLs so pages are not repeatedly crawled |
| `robots.txt` support | Reads site rules before following paths that may be disallowed |
| Redirect handling | Processes URLs returned or discovered while moving between pages |
| CSV storage | Uses Pandas to save scraped URL and text data |
| Adjacency matrix | Records directed connections between crawled webpages |
| Crawl limit | Stops once the configured page limit is reached or no URLs remain |

## Run locally

**Requirements:** Python 3 and an internet connection.

Clone the repository:

```bash
git clone https://github.com/joshuahernn/webScraper.git
cd webScraper
```

Install the required packages:

```bash
pip install requests
```

```bash
pip install beautifulsoup4
```

```bash
pip install pandas
```

```bash
pip install lxml
```

Run the scraper:

```bash
python webScrapper.py
```

On systems where `python` does not point to Python 3, use:

```bash
python3 webScrapper.py
```

## Using the crawler

When the program starts, it asks for the full HTTPS URL of the website you want to scrape.

```text
Please enter the full URL of the site you would like to scrape in the HTTPS format:
```

For example:

```text
https://www.example.com
```

The URL must use the `https://` format. If the input does not match the expected format, the program asks for another URL.

The first valid URL becomes the **seed URL**. The crawler begins with that page and uses links discovered during the crawl to find additional pages.

## Crawl process

At a high level, the crawler follows this flow:

```text
User enters HTTPS URL
        |
        v
   Seed URL added
    to crawl queue
        |
        v
Check robots.txt rules
        |
        v
 Send HTTP GET request
        |
        v
 Parse returned HTML
 with BeautifulSoup/lxml
        |
        v
 Extract page text
        |
        +--------------------+
        |                    |
        v                    v
 Store URL + text       Find page links
 in output.csv               |
                             v
                      Resolve relative URLs
                             |
                             v
                      Track page connection
                             |
                             v
                     Add new URLs to queue
                             |
                             v
                     Continue crawl process
```

The crawler continues until there are no more URLs waiting in the queue or the configured page limit has been reached.

## URL discovery

Webpages often contain both absolute and relative links.

An absolute link already contains the complete location:

```text
https://example.com/about
```

A relative link may only contain a path:

```text
/about
```

The crawler uses `urljoin()` to combine relative links with the current page's URL so they can be treated as complete URLs.

For example:

```text
Current page:  https://example.com
Found link:    /about
Resolved URL:  https://example.com/about
```

`urlparse()` is also used when URL components such as domains and paths need to be separated or inspected.

## `robots.txt`

Before crawling paths on a website, the program checks the site's `robots.txt` file.

For a site such as:

```text
https://example.com
```

the crawler checks:

```text
https://example.com/robots.txt
```

The program reads rules associated with:

```text
User-agent: *
```

and checks discovered paths against `Disallow` entries.

For example:

```text
User-agent: *
Disallow: /private/
```

A URL whose path begins with `/private/` should not be crawled by the program.

The implementation is intentionally lightweight and focuses on the basic `User-agent` and `Disallow` behavior needed for this project rather than attempting to implement the complete Robots Exclusion Protocol.

## HTML parsing

After a successful GET request, the returned HTML is passed to Beautiful Soup:

```python
BeautifulSoup(response.text, "lxml")
```

Beautiful Soup provides the interface used to search the page, extract text, and locate links. `lxml` performs the underlying HTML parsing.

Compared with Python's built-in `html.parser`, `lxml` is generally faster and is also tolerant of imperfect HTML. Since a crawler may repeatedly parse many documents during one run, using `lxml` helps reduce parsing overhead.

The crawler works with the HTML returned by the server. Content created only after JavaScript executes in a browser may therefore not appear in the scraped output.

## Queue and visited URLs

The crawler uses a `deque` as its URL queue.

Conceptually:

```text
Queue:
[page A, page B, page C]
   ^
 next page processed
```

When a URL is discovered, the program can add it to the queue. Before processing it, the crawler tracks whether the page has already been visited.

This prevents a common crawling problem:

```text
Page A -> Page B
Page B -> Page A
```

Without visited-page tracking, the crawler could continuously move between the same pages. Keeping a visited collection allows each intended page to be processed without repeatedly starting the same crawl path again.

## Output files

The scraper produces its CSV files in the directory where the program is executed.

### `output.csv`

`output.csv` contains the primary scraped data.

| URL | Text |
| --- | --- |
| `https://example.com` | Text extracted from the seed page... |
| `https://example.com/about` | Text extracted from the about page... |
| `https://example.com/contact` | Text extracted from the contact page... |

Each row represents a webpage processed by the crawler.

The **URL** column identifies the source page, while the **Text** column contains the readable text extracted from that page.

Because page text can be large, some CSV files produced by larger crawls may also become large.

### `adjacency.csv`

`adjacency.csv` contains the adjacency matrix generated from the links found during the crawl.

An adjacency matrix represents a graph by comparing every recorded webpage with every other recorded webpage.

For example, suppose the crawler finds these links:

```text
Page A -> Page B
Page A -> Page C
Page B -> Page C
Page C -> Page A
```

The corresponding matrix is:

|  | Page A | Page B | Page C |
| --- | ---: | ---: | ---: |
| **Page A** | 0 | 1 | 1 |
| **Page B** | 0 | 0 | 1 |
| **Page C** | 1 | 0 | 0 |

A `1` means the page represented by the row contains a recorded connection to the page represented by the column.

A `0` means that connection was not recorded.

Because webpage links have direction, the matrix does not have to be symmetrical. Page A can link to Page B even if Page B never links back to Page A.

## Adjacency matrix model

The crawler can be viewed as building a directed graph:

```text
        +--------+
        | Page A |
        +--------+
          |    \
          |     \
          v      v
      +--------+  +--------+
      | Page B |->| Page C |
      +--------+  +--------+
                      |
                      |
                      v
                   Page A
```

In graph terminology:

- Each URL is a **vertex**.
- Each discovered page-to-page link is a directed **edge**.
- The adjacency matrix stores those edges numerically.

This makes the output useful for understanding not only the content of the pages but also how the pages discovered during the crawl are connected.

## Code guide

| File | Purpose |
| --- | --- |
| [`webScrapper.py`](webScrapper.py) | Main crawler logic, URL input, requests, parsing, link discovery, `robots.txt` handling, storage, and crawl control |
| `output.csv` | Generated URL and scraped-text dataset |
| `adjacency.csv` | Generated adjacency matrix showing links between crawled pages |

The main program can be understood as several stages:

```text
Input
  ->
Request
  ->
Parse
  ->
Extract
  ->
Discover Links
  ->
Queue New URLs
  ->
Store Results
  ->
Generate Adjacency Matrix
```

When reading the code, following those stages makes it easier to understand how the crawler moves from one page to the next.

## Libraries used

| Library / Module | Purpose |
| --- | --- |
| `requests` | Sends HTTP requests and receives webpage responses |
| `bs4.BeautifulSoup` | Searches and extracts information from parsed HTML |
| `lxml` | Parser used by Beautiful Soup |
| `pandas` | Creates and writes CSV-based data |
| `collections.deque` | Maintains the crawl queue |
| `urllib.parse.urljoin` | Converts relative links into absolute URLs |
| `urllib.parse.urlparse` | Separates and inspects URL components |
| `os` | Handles operating-system and file-related operations |

## Technical notes and tradeoffs

- **Requests instead of a browser:** the crawler communicates directly with web servers using `requests`. This keeps the program lightweight, but JavaScript-rendered content may not be available because no browser executes the page scripts.
- **`lxml` parsing:** using `lxml` provides efficient HTML parsing and is useful when repeatedly processing webpages. Beautiful Soup remains the higher-level interface for finding elements and extracting text.
- **Queue-based crawling:** a `deque` provides an efficient structure for URLs waiting to be processed and keeps the crawl logic easier to follow.
- **Visited-page tracking:** URLs are tracked separately so discovered links do not cause the crawler to endlessly revisit the same pages.
- **Adjacency matrix storage:** a matrix makes page relationships easy to inspect and export to CSV, although the matrix becomes increasingly large as the number of unique URLs grows.
- **Basic `robots.txt` parsing:** the crawler checks common `User-agent: *` and `Disallow` rules. It is designed for the scope of this project rather than as a complete implementation of every possible robots directive.
- **Static HTML focus:** the program extracts data present in the HTTP response. Sites that rely heavily on JavaScript may return incomplete visible content compared with what appears in a browser.
- **Website differences:** real websites use different HTML structures, redirects, link formats, access controls, and server behavior, so results can vary between domains.

## Why the adjacency matrix can become large

An adjacency matrix requires one row and one column for every recorded URL.

If a crawl contains `n` URLs, the matrix contains approximately:

```text
n x n
```

entries.

For example:

| URLs | Matrix entries |
| ---: | ---: |
| 10 | 100 |
| 100 | 10,000 |
| 1,000 | 1,000,000 |
| 10,000 | 100,000,000 |

This makes an adjacency matrix simple to understand and useful for smaller crawls, but potentially expensive in memory and file size for very large crawls.

A larger production crawler would often store only the edges that actually exist instead of every possible URL-to-URL combination.

## Limitations

This project is an educational web crawler and is not intended to replace production crawling frameworks.

Current limitations include:

- JavaScript-generated content is not rendered.
- Some websites may block automated requests.
- Some servers may return redirects, errors, or non-HTML content.
- HTML structure varies significantly between websites.
- The `robots.txt` implementation covers the rules needed by this project rather than the complete specification.
- Large crawls can create large CSV files.
- Adjacency matrices scale poorly when the number of discovered URLs becomes very large.
- The program does not currently use multithreading or asynchronous requests.

## Possible improvements

Potential extensions to the project include:

- Multithreaded or asynchronous HTTP requests
- Request timeouts and retry policies
- More complete `robots.txt` handling
- Crawl-delay support
- Domain-specific crawl restrictions
- Additional URL normalization
- Saving and loading crawl state
- More compact graph storage for large crawls
- JSON or database output
- Better handling of non-HTML responses
- Command-line arguments for crawl settings
- Logging instead of console debug output

## Responsible crawling

Web crawling should be performed responsibly.

Before crawling a site:

- Review its `robots.txt` rules.
- Respect its terms of service.
- Avoid sending requests at an excessive rate.
- Do not attempt to access private or restricted content.
- Keep crawl sizes reasonable.
- Only collect data you are permitted to access and use.

The `robots.txt` check in this project is one part of responsible crawling, but it does not replace the need to follow a website's applicable policies.

## Project purpose

This project was built to practice and better understand:

- HTTP GET requests
- Web scraping
- Web crawling
- HTML parsing
- Relative and absolute URLs
- URL queues
- Duplicate URL prevention
- `robots.txt`
- CSV data storage
- Pandas
- Graph relationships
- Adjacency matrices

Rather than relying on an existing crawler framework, the project implements these pieces directly so the individual parts of the crawling process can be seen and understood.
