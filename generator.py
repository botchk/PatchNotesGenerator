import os
import markovify
import requests
import argparse

from reddit.account import Account
from bs4 import BeautifulSoup
from config import *


def parse_url(url):
    summary = ''
    request = requests.get(url)
    
    if request.status_code == requests.codes.ok:   
        soup = BeautifulSoup(request.text, "html.parser")
        container = soup.find("div", {"id": "patch-notes-container"})
        
        if container == None:
            print("could not find patch-notes-container")
        else:
            summary = get_summary(container)
        
    else:
        print("    ERROR status_code: " + str(request.status_code))
        
    return summary
    
    
def get_summary(container):
    clean_summary = ''
    summary = container.find_next("blockquote", {"class": "blockquote context"})
    
    if summary == None:
        print("could not find patch summary")
    else:
        print("summary")
        clean_summary = format_text(summary.text)
        
    return clean_summary
    
# removes all whitespaces except spaces and 
def format_text(text):
    return " ".join(text.split())
  
    
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
            print("  * " + url)
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
    
    args = parser.parse_args()
    
    if args.parse:
        print('parsing patch notes')
        parse()
        
    if args.generate:
        print('generate patch notes')
        generate()
    
    # Check that the config file exists
    if not os.path.isfile("config.py"):
        print("config.py not found")
        print("see config.example.py")
        exit(1)

    #account = Account(REDDIT_USERNAME, REDDIT_PASSWORD, "PGdevTest 0.1")
    #account.print_stats()

    #account.post_text_submission("test", "this is a test", "text test")
    #submission = account.post_url_submission("test", "this is a test", "http://imgur.com/gallery/eydpv2P")

if __name__ == "__main__":
    main()

