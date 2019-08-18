"Parses League of Legends patch notes and stores the results as json"

import codecs
import json
import argparse
import requests
from bs4 import BeautifulSoup

from patch import Patch
from patch import Champion
from patch import serialize as patch_serialize


def print_text(text, indentation):
    print((" " * indentation) + text)


def print_bullet_point(text, indentation):
    print_text("* " + text, indentation)


def cleanup_text(text):
    """
    Removes all whitespaces and replaces them with single spaces.
    Also replace different kind of apostrophs for easier handling
    """
    clean_text = " ".join(text.split())
    clean_text = clean_text.replace("’", "'")
    return clean_text.replace("‘", "'")


def parse_patch(number, url, patch_format):
    patch = None

    if patch_format in ("2", "3"):
        request = requests.get(url)

        if request.status_code == requests.codes.ok:
            soup = BeautifulSoup(request.text, "html.parser")
            container = soup.find("div", {"id": "patch-notes-container"})

            if container is None:
                print_bullet_point("ERROR: Could not find patch-notes-container", 4)
            else:
                print_bullet_point("Summary", 4)
                patch_summary = parse_summary(container)
                patch = Patch(number, patch_summary)

                print_bullet_point("Champions", 4)
                if patch_format == "3":
                    patch.champions = parse_champions(
                        container.find("h2", {"id": "patch-fighters"}).parent)
                    patch.champions = parse_champions(
                        container.find("h2", {"id": "patch-mages-and-assassins"}).parent)
                    patch.champions = parse_champions(
                        container.find("h2", {"id": "patch-marksmen"}).parent)
                    patch.champions = parse_champions(
                        container.find("h2", {"id": "patch-supports"}).parent)
                else:
                    patch.champions = parse_champions(
                        container.find("h2", {"id": "patch-champions"}).parent)
        else:
            print_bullet_point("ERROR: status_code " + str(request.status_code), 4)
    else:
        print_bullet_point("Unknown patch format {}".format(patch_format), 4)

    return patch


def parse_summary(container):
    summary = container.find_next("blockquote", {"class": "blockquote context"})

    if summary is None:
        print_bullet_point("No summary found", 6)
        return ""

    return cleanup_text(summary.text)


def parse_champions(champions_header):
    champions = []
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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parses League of Legends patch notes and stores the results as json")

    parser.add_argument(
        "config",
        type=str,
        help="Configuration file that specifies the patch URLs")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="patches.json",
        help="Output file, default is 'patches.json'")

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    patches = {}

    with open(args.config, "r") as config:
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

    with codecs.open(args.output, "w", "utf-8") as file:
        json.dump(patches, file, default=patch_serialize, indent=4)


if __name__ == "__main__":
    main()
