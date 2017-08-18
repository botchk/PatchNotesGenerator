import os
import markovify
import requests
import argparse

from reddit.account import Account
from bs4 import BeautifulSoup
from config import *

#relative data directory for storing all generated files
data_dir = "data"


def print_text(text, indentation):
    print((" " * indentation) + text)
    
    
#print with bullet point in front
def print_bullet_point(text, indentation):
    print_text("* " + text, indentation)
    
    
# removes all whitespaces and replaces them with single spaces
def format_text(text):
    return " ".join(text.split())

    
def parse_url(url):
    summary = ""
    request = requests.get(url)
    
    if request.status_code == requests.codes.ok:   
        soup = BeautifulSoup(request.text, "html.parser")
        container = soup.find("div", {"id": "patch-notes-container"})
        
        if container == None:
            print("could not find patch-notes-container")
        else:
            summary = get_summary(container)
            changes = get_champ_changes(container)
        
    else:
        print("    ERROR status_code: " + str(request.status_code))
        
    return summary
    
    
def get_summary(container):
    clean_summary = ""
    summary = container.find_next("blockquote", {"class": "blockquote context"})
    
    if summary == None:
        print_bullet_point("No summary found", 4)
    else:
        print_bullet_point("Summary", 4)
        clean_summary = format_text(summary.text)
        
    return clean_summary
    
    
def get_champ_changes(container):
    clean_changes = ''
    champion_header = container.find("h2", {"id": "patch-champions"}).parent
    champion = champion_header.next_sibling
    
    if is_champion_change(champion):
        print_bullet_point("Champions", 4)
    else:
        print_bullet_point("No champions found", 4)
    
    while is_champion_change(champion):
        name = champion.find("h3", {"class": "change-title"})
        print_bullet_point(format_text(name.text), 6)
        #newline is seperate sibling, skip it
        champion = champion.next_sibling.next_sibling
    
        
def is_champion_change(content):
    block = content.find("div", {"class": "patch-change-block"})
    return block != None
  
    
def generate_summary(summaries):
    summary = ''
    welcome_model = markovify.Text(summaries, state_size=2)
    summary = welcome_model.make_sentence_with_start('Welcome')
    
    corpus_model = markovify.Text(summaries, state_size=2)
    for i in range(1,20):
        sentence = corpus_model.make_sentence()
        while sentence == None or "Welcome" in sentence:
            sentence = corpus_model.make_sentence()
            
        summary = summary + '\n' + sentence
    
    return summary
  
    
def parse():
    summaries = ''
    base_url = 'http://euw.leagueoflegends.com/en/news/game-updates/patch/patch-'
    patches = {5:24, 6:24, 7:16}

    for year, max_number in patches.items():
        for number in range(1, max_number + 1):
            url = base_url + str(year) + str(number) + '-notes'
            print_bullet_point(url, 2)
            summaries = summaries + parse_url(url).encode("utf-8") + ' '
            
    with open("summaries", "w") as file:
        file.write(summaries)
    
        
def generate():
    summaries = ''
    with open("summaries", "r") as file:
        summaries = file.read()
        
    summary = generate_summary(summaries)
    
    with open("summary", "w") as file:
        file.write(summary)
    
        
def main(): 
    parser = argparse.ArgumentParser(description='League of Legends patch notes generator')
    parser.add_argument('-p', '--parse', action="store_true", default=False,
                        dest='parse', help='parses the patch notes and generates content files')
    parser.add_argument('-g', '--generate', action="store_true", default=False,
                        dest='generate', help='generates patch notes out of content files')
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    args = parser.parse_args()
    
    if args.parse:
        print("parsing patch notes...")
        parse()
        
    if args.generate:
        print("generating patch notes...")
        generate()
    
    # Check that the config file exists
    #if not os.path.isfile("config.py"):
        #print("config.py not found")
        #print("see config.example.py")
        #exit(1)

    #account = Account(REDDIT_USERNAME, REDDIT_PASSWORD, "PGdevTest 0.1")
    #account.print_stats()

    #account.post_text_submission("test", "this is a test", "text test")
    #submission = account.post_url_submission("test", "this is a test", "http://imgur.com/gallery/eydpv2P")

if __name__ == "__main__":
    main()

