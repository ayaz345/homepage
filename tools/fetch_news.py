#!/usr/bin/env python3

import urllib.request
import re
import os
import html as pyhtml

def fetch_all_news_links():

    result = set()
    visited = set()

    url = "https://manjaro.org/news/"

    while url:

        print(f"Visit {url} ...")
        visited.add(url)
        html = urllib.request.urlopen(url).read().decode("utf-8")

        matches = re.findall("\"https:\\/\\/manjaro.org\\/\\d{4}\\/\\d{2}\\/\\d{2}\\/\\S+\\/\"", html)
        matches_pages = re.findall("\"https:\\/\\/manjaro.org\\/news\\/page\\/\\d+\\/\"", html)

        result |= {m[1:-1] for m in matches}
        matches_pages = {m[1:-1] for m in matches_pages} - visited

        print(f"Found {len(result)} links")

        url = list(matches_pages)[0] if matches_pages else None
    return result

def make_archives():

    news_urls = set()

    with open("news_links.txt", "r") as f:
        for _line in f:
            if line := _line.strip():
                news_urls.add(line)

    if not os.path.exists("news-archive"):
        os.mkdir("news-archive")

    archives = { url.split("/")[4] + "_" + url.split("/")[3] : { "month" : int(url.split("/")[4]), "year" : int(url.split("/")[3]), "name" : url.split("/")[4] + "_" + url.split("/")[3]} for url in news_urls }
    archives = list(sorted(archives.values(), key = lambda x: x["year"] * 12 + x["month"]))
    archive_names = [ x["name"] for x in archives]

    for arch in archives:

        year = arch["year"]
        month = arch["month"]
        name = arch["name"]

        print(name)

        with open(f"news-archive/{name}.md", "w") as f:
            f.write(
                "\n".join(
                    [
                        "+++",
                        "archive = \"" + name + "\"",
                        f"weight = {archive_names.index(name)}",
                        "title = \"" + str(month) + "/" + str(year) + "\"",
                        "type = \"news-archive\"",
                        "+++",
                    ]
                )
            )

def extract_news():

    news_urls = set()

    with open("news_links.txt", "r") as f:
        for _line in f:
            if line := _line.strip():
                news_urls.add(line)

    for url in news_urls:

        print(f"Visit {url}")

        html = urllib.request.urlopen(url).read().decode("utf-8")


        with open("debug.html", "w") as f:
            f.write(html)
        html = html.replace("\r","").replace("\n", "")

        title = pyhtml.unescape(re.split("[><|]", re.findall("<title>.*<\\/title>", html)[0].strip())[2]).strip()
        author = pyhtml.unescape(re.split("[><]", re.findall("\"author\">.*<\\/a>", html)[0].strip())[1]).strip()
        date = pyhtml.unescape(re.split("[><]", re.findall("\"entry-date\">.*<\\/li>", html)[0].strip())[1]).strip()
        content = pyhtml.unescape(re.split("[><]", re.findall("\"text\">.*", html)[0].strip())[1]).strip()

        print(f"{title} by {author} on {date}")
        print(content)

        return


def main():

    if not os.path.exists("news_links.txt"):
        with open("news_links.txt", "w") as f:
            f.write("\n".join(fetch_all_news_links()))
    else:
        print("Skipping extraction of news links")

    make_archives()
    extract_news()

main()
