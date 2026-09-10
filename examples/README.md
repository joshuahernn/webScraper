# Reproduce the demo

From the repository root, with the dependencies installed:

```bash
python examples/run_demo.py
```

This runs the real crawler against the three HTML files and `robots.txt` in [`site/`](site/). The HTTPS URLs use the reserved `demo.example` domain; a fixture adapter supplies responses in memory. **No network requests are made.** This is a functional example, not a live-site benchmark.

The run verifies:

- Three pages produce the expected text, each fetched once.
- Four directed links appear in the exported matrix.
- The `/private/` path is blocked before a page request.
- A link back to Home does not restart the crawl.
- The site's robots rules are fetched once and reused.

## Generated artifacts

| File | What it shows |
| --- | --- |
| [`sample-output/output.csv`](sample-output/output.csv) | Actual text exported by the crawler |
| [`sample-output/adjacency.csv`](sample-output/adjacency.csv) | Actual exported adjacency matrix |
| [`sample-output/terminal.txt`](sample-output/terminal.txt) | Captured console output from the run |
| [`sample-output/link-graph.svg`](sample-output/link-graph.svg) | Graph and matrix rendered from the exported CSV by the demo script |

The renderer is a presentation helper for this three-page fixture, not a general graph-rendering feature of the crawler. The demo writes crawl results in a temporary directory, then replaces its own generated files in `examples/sample-output/`. It leaves any root-level crawl exports alone.

The HTML and text are included demo content. To inspect live-site behavior separately, run `python webScraper.py`; the [README](../README.md#crawl-a-website) explains current operating limits.
