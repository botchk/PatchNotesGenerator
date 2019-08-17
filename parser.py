"Parses League of Legends patch websites and stores the results in json"

import os
import codecs
import json
import requests
from bs4 import BeautifulSoup

from patch import Patch
from patch import Champion
from patch import serialize as patch_serialize


#relative data directory for storing parsed patches
DATA_DIR = "data"


def print_text(text, indentation):
    print((" " * indentation) + text)


#print with bullet point in front
def print_bullet_point(text, indentation):
    print_text("* " + text, indentation)


# removes all whitespaces and replaces them with single spaces
# also replace different kind of apostrophs for easier handling
def cleanup_text(text):
    clean_text = " ".join(text.split())
    clean_text = clean_text.replace("’", "'")
    return clean_text.replace("‘", "'")


def parse_patch(number, url, patch_format):
    patch = None

    if patch_format == "2":
        request = requests.get(url)

        if request.status_code == requests.codes.ok:
            soup = BeautifulSoup(request.text, "html.parser")
            container = soup.find("div", {"id": "patch-notes-container"})

            if container is None:
                print_bullet_point("ERROR: Could not find patch-notes-container", 4)
            else:
                patch_summary = parse_summary(container)
                patch = Patch(number, patch_summary)
                patch.champions = parse_champions(container)
        else:
            print_bullet_point("ERROR: status_code " + str(request.status_code), 4)
    else:
        print_bullet_point("Unknown patch format {}".format(patch_format), 4)

    return patch


def parse_summary(container):
    summary = container.find_next("blockquote", {"class": "blockquote context"})

    if summary is None:
        print_bullet_point("No summary found", 4)
        return ''

    print_bullet_point("Summary", 4)
    return cleanup_text(summary.text)


def parse_champions(container):
    champions = []
    champions_header = container.find("h2", {"id": "patch-champions"}).parent
    champion_block = champions_header.next_sibling

    while not is_header(champion_block):
        if not is_champion(champion_block):
            print_bullet_point("Not a champion block", 6)
        else:
            name_block = champion_block.find("h3", {"class": "change-title"})
            champion = Champion(cleanup_text(name_block.text))
            print_bullet_point(champion.name, 6)

            short_summary_block = champion_block.find("p", {"class": "summary"})
            if short_summary_block is not None:
                champion.short_summary = cleanup_text(short_summary_block.text)

            summary_block = champion_block.find("blockquote", {"class": "blockquote context"})
            if summary_block is not None:
                champion.summary = cleanup_text(summary_block.text)

            champions.append(champion)

        #there can be a newline inbetween tags, skip it
        champion_block = champion_block.next_sibling
        if champion_block == "\n":
            champion_block = champion_block.next_sibling

    return champions


def is_header(content):
    return content.name == "header"


def is_champion(content):
    block = content.find("div", {"class": "patch-change-block"})
    return block is not None


def main():

    patches = {}

    with open("parser_config", "r") as config:
        for line in config.read().splitlines():
            patch_format, major, minor_range, url = line.split(";")

            # minor can be either a single number or a range (e.g. 1-4)
            minor_min = minor_max = int(minor_range.split("-")[0])
            if "-" in minor_range:
                minor_min, minor_max = [int(x) for x in minor_range.split("-")]

            for minor in range(minor_min, minor_max + 1):
                number = str(major) + str(minor)
                formatted_url = url.format(number)
                print_bullet_point("Patch {}.{} (Format: {}) - {}".format(major, minor, patch_format, formatted_url), 2)
                patch = parse_patch(number, formatted_url, patch_format)
                if patch:
                    patches[patch.number] = patch
                print()

    with codecs.open(os.path.join(DATA_DIR, "patches"), "w", "utf-8") as file:
        json.dump(patches, file, default=patch_serialize, indent=4)


if __name__ == "__main__":
    main()
