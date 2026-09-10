"""Run the unchanged crawler offline and render its three-page example exports."""

import contextlib
import csv
import importlib.util
import io
import os
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch
from xml.sax.saxutils import escape

import requests

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "examples" / "site"
OUTPUT = ROOT / "examples" / "sample-output"
ORIGIN = "https://demo.example"
PAGES = {
    ORIGIN: "index.html",
    ORIGIN + "/about": "about.html",
    ORIGIN + "/contact": "contact.html",
    ORIGIN + "/robots.txt": "robots.txt",
}


def render_graph(rows):
    """Visualize this fixture's CSV, with edges determined by the matrix values."""
    names = ["Home", "About", "Contact"]
    positions = [(70, 235), (350, 120), (350, 350)]
    paths = {
        (0, 1): "M230 252 C275 252 285 156 344 156",
        (0, 2): "M230 279 C275 279 285 386 344 386",
        (1, 2): "M430 192 L430 344",
        (2, 0): "M350 404 C215 480 80 425 80 313",
    }
    arrowheads = {
        (0, 1): "M334 150 L344 156 L334 162",
        (0, 2): "M334 380 L344 386 L334 392",
        (1, 2): "M424 334 L430 344 L436 334",
        (2, 0): "M74 323 L80 313 L86 323",
    }
    edges = [(i, j) for i, row in enumerate(rows) for j in range(3) if row[str(j)] == "1"]
    elements = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="540" viewBox="0 0 1040 540" role="img" aria-labelledby="title desc">
<title id="title">Three webpages, four directed links</title>
<desc id="desc">Offline fixture results: Home links to About and Contact. About links to Contact. Contact links to Home. The matrix shows the same four links.</desc>
<rect width="1040" height="540" rx="20" fill="#f6f8fb"/>
<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">
<text x="42" y="43" fill="#168071" font-size="13" font-weight="700" letter-spacing="2">WEB CRAWLER / DEMO OUTPUT</text>
<text x="42" y="88" fill="#15283c" font-size="32" font-weight="700">From webpages to a link graph</text>
<line x1="574" y1="130" x2="574" y2="452" stroke="#dce3ea"/>
<text x="625" y="161" fill="#15283c" font-size="19" font-weight="600">The same links, as a matrix</text>
<text x="625" y="188" fill="#526477" font-size="14">Row → column · 1 means a link exists</text>''']
    for edge in edges:
        elements.append(f'<path d="{paths[edge]}" fill="none" stroke="#168b7d" stroke-width="2.5"/>')
        elements.append(f'<path d="{arrowheads[edge]}" fill="none" stroke="#168b7d" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')
    for i, (x, y) in enumerate(positions):
        suffix = ["/", "/about", "/contact"][i]
        elements.append(f'<rect x="{x}" y="{y}" width="160" height="72" rx="12" fill="white" stroke="#cbd6e2"/>')
        elements.append(f'<text x="{x+18}" y="{y+29}" fill="#15283c" font-size="18" font-weight="600">{names[i]}</text>')
        elements.append(f'<text x="{x+18}" y="{y+52}" fill="#607186" font-size="13">{suffix}</text>')
    for j, name in enumerate(names):
        elements.append(f'<text x="{793+j*77}" y="236" fill="#526477" font-size="13" text-anchor="middle">{name}</text>')
    for i, row in enumerate(rows):
        y = 254 + i * 61
        elements.append(f'<text x="625" y="{y+31}" fill="#15283c" font-size="16">{names[i]}</text>')
        for j in range(3):
            value = row[str(j)]
            fill, ink = ("#daf2ec", "#096b5c") if value == "1" else ("#e9eef4", "#627487")
            x = 764+j*77
            elements.append(f'<rect x="{x}" y="{y}" width="58" height="46" rx="8" fill="{fill}"/>')
            elements.append(f'<text x="{x+29}" y="{y+31}" fill="{ink}" font-size="22" font-weight="600" text-anchor="middle">{escape(value)}</text>')
    elements.append(f'<text x="42" y="502" fill="#526477" font-size="14">Offline fixture · {len(rows)} pages · {len(edges)} directed links · rendered from adjacency.csv</text></g></svg>')
    return "\n".join(elements) + "\n"


def main():
    spec = importlib.util.spec_from_file_location("crawler", ROOT / "webScraper.py")
    crawler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(crawler)
    fetched = []

    def fixture_get(url, **kwargs):
        # Unknown URLs fail immediately: the demo cannot fall through to a live request.
        if url not in PAGES:
            raise RuntimeError(f"Unexpected fixture URL: {url}")
        fetched.append(url)
        response = requests.Response()
        response.status_code = 200
        response.url = url
        response.encoding = "utf-8"
        response._content = (SITE / PAGES[url]).read_bytes()
        return response

    transcript = io.StringIO()
    original_directory = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="crawler-demo-") as temporary:
        try:
            os.chdir(temporary)
            with patch.object(crawler.requests, "get", side_effect=fixture_get), patch(
                "builtins.input", return_value=ORIGIN
            ), contextlib.redirect_stdout(transcript):
                print("Offline demo: using included HTML and robots.txt fixtures.")
                crawler.main()
            with open("output.csv", newline="", encoding="utf-8") as stream:
                pages = list(csv.DictReader(stream))
            with open("adjacency.csv", newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            urls = list(PAGES)[:3]
            expected_text = [
                "Crawler demo Three pages, one connected site.",
                "About This fixture demonstrates relative link discovery.",
                "Contact The link home closes the cycle.",
            ]
            expected_matrix = [["0", "1", "1"], ["0", "0", "1"], ["1", "0", "0"]]
            if pages != [dict(URL=url, Text=text) for url, text in zip(urls, expected_text)]:
                raise RuntimeError("Exported page text does not match the fixture.")
            if [row["URL"] for row in rows] != urls or [
                [row[str(j)] for j in range(3)] for row in rows
            ] != expected_matrix:
                raise RuntimeError("Exported links do not match the fixture.")
            if fetched != [ORIGIN + "/robots.txt", *urls]:
                raise RuntimeError("Unexpected request order, duplicate, or robots fetch.")
            print("Verified: 3 pages, 4 directed links, 1 blocked path.", file=transcript)
            print("Each page fetched once; robots.txt fetched once.", file=transcript)
            print("Saved demo artifacts to examples/sample-output/", file=transcript)
            OUTPUT.mkdir(parents=True, exist_ok=True)
            for filename in ("output.csv", "adjacency.csv"):
                shutil.copyfile(filename, OUTPUT / filename)
            (OUTPUT / "link-graph.svg").write_text(render_graph(rows), encoding="utf-8")
            (OUTPUT / "terminal.txt").write_text(transcript.getvalue(), encoding="utf-8")
        finally:
            os.chdir(original_directory)
    print(transcript.getvalue(), end="")


if __name__ == "__main__":
    main()
