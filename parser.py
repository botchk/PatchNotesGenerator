import os
import markovify
import requests
import argparse
import codecs
import json

from patch import Patch
from patch import Champion
from patch import serialize as patch_serialize
from bs4 import BeautifulSoup

url_start = 'http://euw.leagueoflegends.com/en/news/game-updates/patch/patch-'
url_end = '-notes'

#year:highest_patch
#patch_numbers = {3:2}
patch_numbers = {5:24, 6:24, 7:21, 8:24, 9:4}

#relative data directory for storing parsed patches
data_dir = "data"


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

    
def parse_patch(number):
    patch = None
    url = url_start + number + url_end
    print_bullet_point(url, 2)

    request = requests.get(url)
    
    if request.status_code == requests.codes.ok:   
        soup = BeautifulSoup(request.text, "html.parser")
        container = soup.find("div", {"id": "patch-notes-container"})
        
        if container == None:
            print_bullet_point("ERROR: Could not find patch-notes-container", 4)
        else:
            patch_summary = parse_summary(container)
            patch = Patch(number, patch_summary)
            patch.champions = parse_champions(container)
    else:
        print_bullet_point("ERROR: status_code " + str(request.status_code), 4)

    return patch
    
    
def parse_summary(container):
    summary = container.find_next("blockquote", {"class": "blockquote context"})
    
    if summary == None:
        print_bullet_point("No summary found", 4)
        return ''
    else:
        print_bullet_point("Summary", 4)
        return cleanup_text(summary.text)

    
def parse_champions(container):
    champions = []
    champions_header = container.find("h2", {"id": "patch-champions"}).parent
    champion_block = champions_header.next_sibling
    
    while not is_header(champion_block):
        if not is_champion(champion_block):
            print_bullet_point("Not a champion", 6)
        else:
            name_block = champion_block.find("h3", {"class": "change-title"})
            champion = Champion(cleanup_text(name_block.text))
            print_bullet_point(champion.name, 6)

            summary_block = champion_block.find("p", {"class": "summary"})
            if summary_block != None:
                champion.summary = cleanup_text(summary_block.text)

            description_block = champion_block.find("blockquote", {"class": "blockquote context"})
            if description_block != None:
                champion.description = cleanup_text(description_block.text)

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
    return block != None       


def main():     
    patches = {}
            
    for year, max_number in patch_numbers.items():
        for number in range(1, max_number + 1):
            patch = parse_patch(str(year) + str(number))
            if patch:
                patches[patch.number] = patch
            print()
        
    with codecs.open(os.path.join(data_dir, "patches"), "w", "utf-8") as file:
        json.dump(patches, file, default=patch_serialize, indent=4)
    

if __name__ == "__main__":
    main()

