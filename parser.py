import os
import markovify
import requests
import argparse
import codecs
import json

from champion import Champion
from champion import serialize
from bs4 import BeautifulSoup

url_start = 'http://euw.leagueoflegends.com/en/news/game-updates/patch/patch-'
url_end = '-notes'

#year:highest_patch
patches = {5:24}
# patches = {5:24, 6:24, 7:24, 8:24, 9:4}

#relative data directory for storing parsed patches
data_dir = "data"


def print_text(text, indentation):
    print((" " * indentation) + text)
    
    
#print with bullet point in front
def print_bullet_point(text, indentation):
    print_text("* " + text, indentation)
    
    
# removes all whitespaces and replaces them with single spaces
def format_text(text):
    return " ".join(text.split())

    
def parse_patch(url):
    summary = ""
    champions = []
    request = requests.get(url)
    
    if request.status_code == requests.codes.ok:   
        soup = BeautifulSoup(request.text, "html.parser")
        container = soup.find("div", {"id": "patch-notes-container"})
        
        if container == None:
            print("Could not find patch-notes-container")
        else:
            summary = parse_summary(container)
            champions = parse_champions(container)
    else:
        print_text("ERROR status_code " + str(request.status_code), 4)

    return summary, champions
    
    
def parse_summary(container):
    summary = container.find_next("blockquote", {"class": "blockquote context"})
    
    if summary == None:
        print_bullet_point("No summary found", 4)
        return ''
    else:
        print_bullet_point("Summary", 4)
        return format_text(summary.text)

    
def parse_champions(container):
    champions = []
    champions_header = container.find("h2", {"id": "patch-champions"}).parent
    champion_block = champions_header.next_sibling
    
    while not is_header(champion_block):
        if not is_champion(champion_block):
            print_bullet_point("Not a champion", 6)
        else:
            name = champion_block.find("h3", {"class": "change-title"})
            champion_name = format_text(name.text)
            print_bullet_point(champion_name, 6)
            champion = Champion(champion_name)
            champion.add_description("test")
            champion.add_summary("test2")
            champions.append(champion)
            
        #there can be a newline inbetween tags, skip it
        champion_block = champion_block.next_sibling
        if champion_block == "\n":
            champion_block = champion_block.next_sibling
            
    return champions


def is_header(content):
    return content.name == "header"

            
#def is_champion_header(content):
#    header = content.find("h2", {"id": "patch-champions"})
#    return header != None
    
        
def is_champion(content):
    block = content.find("div", {"class": "patch-change-block"})
    return block != None
  

def clean_dir(dir):
    for file in os.listdir(dir):
        os.unlink(os.path.join(dir, file))        


def main(): 
    print("Cleaning data directory...")
    clean_dir(data_dir)
    
    champions_merged = {}
    summaries = ""
            
    for year, max_number in patches.items():
        for number in range(1, max_number + 1):
            url = url_start + str(year) + str(number) + url_end
            print_bullet_point(url, 2)
            summary, champions = parse_patch(url)
            summaries += summary + " "
            for champion in champions:
                if champion.name in champions_merged:
                    # merge champion into existing champion
                    print_bullet_point("Merge " + champion.name, 2)
                else:
                    # create first champion in dict
                    print_bullet_point("Create " + champion.name, 2)
                    champions_merged[champion.name] = champion
            print()
            
    with codecs.open(os.path.join(data_dir, "summaries"), "w", "utf-8") as file:
        file.write(summaries)
        
    with codecs.open(os.path.join(data_dir, "champions"), "w", "utf-8") as file:
        json.dump(champions_merged, file, default=serialize)
    

if __name__ == "__main__":
    main()

