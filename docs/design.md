# How the crawler works

The implementation lives in [`webScraper.py`](../webScraper.py). This guide describes the current code, including its boundaries.

## From seed URL to CSV

1. `get_url()` prompts for an HTTPS seed, checks basic robots rules, and requests the page.
2. `save_text()` parses the seed response with Beautiful Soup and lxml. It prefers the `<main>` element and otherwise uses `<body>`.
3. `fill_table()` appends the page URL and text to `output.csv`.
4. `redirect_urls()` resolves discovered links with `urljoin()`, adds unseen HTTP(S) URLs to a `deque`, and processes them in discovery order.
5. Before each queued request, `check_robots()` checks the domain's cached rules. Allowed URLs are added to the visited set and ordered URL list. Successful readable responses are exported, and their links extend the queue.
6. `create_adj_table()` builds a directed adjacency matrix; `save_adj_table()` writes it to `adjacency.csv`.

## Engineering decisions

| Decision | Benefit | Tradeoff |
| --- | --- | --- |
| Requests + Beautiful Soup/lxml | Keeps fetching and HTML extraction explicit and easy to inspect | Does not execute JavaScript |
| FIFO `deque` + visited set | Processes links breadth-first and prevents revisiting identical URL strings | Checking queue membership is linear; equivalent URLs are not fully canonicalized |
| Per-domain robots cache | Reuses successfully fetched rules across pages | The parser only handles basic wildcard-agent `Disallow` prefixes |
| Append page text as each page finishes | Preserves text already written if a later request fails | Repeated runs append to the same file; graph export happens only at the end |
| Dense adjacency matrix | Makes small link graphs easy to inspect in a spreadsheet | Uses O(n²) entries; a sparse edge list would scale better |

These describe the implementation's tradeoffs, rather than measured performance claims.

## A cycle and a blocked path

The [offline demo](../examples/README.md) includes `Home → Contact → Home`. Tracking visited URLs prevents that cycle from causing repeated requests. Both Home and About link to Contact, which is fetched once. A fourth discovered path, `/private/`, is disallowed by the included `robots.txt` and is never fetched.

The demo runs the actual `main()` function. Only user input and HTTP responses are substituted with local fixtures. It verifies the expected page texts, four directed edges, one robots fetch, no repeated page fetches, and the absence of requests to the disallowed path. It does not test live networking, redirects, or failure recovery.

## Reading the exports

- **`output.csv`:** `URL,Text`; text is written for successfully parsed pages. Link text outside `<main>` is excluded when a `<main>` element exists.
- **`adjacency.csv`:** `URL,0,1,...`; row `i` identifies the URL represented by column `i`. A `1` at row `i`, column `j` records a link from URL `i` to URL `j`.

The matrix includes URLs marked visited before their requests finish, so a failed page can appear in the matrix without a corresponding text row. Edges are retained only when both endpoints occur in the ordered visited list. Redirected URLs can differ from queued URLs, which can affect recorded connections.

## Current boundaries

- Seed input must start with HTTPS. Use a site's origin, such as `https://host.example`, because seed robots lookup appends `/robots.txt` directly to the supplied value.
- Discovered links may use HTTP or HTTPS and may leave the seed domain.
- Five-second request timeouts are present. Seed error recovery is incomplete, and some network or parsing failures can still stop the program.
- The basic robots parser skips an origin when its robots file is unavailable or returns a non-200 status. It does not implement the complete protocol or check each automatic redirect target.
- The code has no request delay, retry policy, concurrency, or command-line crawl configuration.
- `max_pages = 5000` limits successfully extracted queued pages, excluding the initial seed. It does not bound all requests or all discovered URLs.
- The graph is written at normal crawl completion. An interrupted run may leave text output without a new graph export.

## Next steps

1. Expose page limits, domain scope, and request delay as command-line options.
2. Improve seed failures, robots handling, redirect handling, and URL canonicalization.
3. Offer an edge-list export for larger crawls.
