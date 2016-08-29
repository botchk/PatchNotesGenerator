import os
import markovify
import requests

from reddit.account import Account
from bs4 import BeautifulSoup
from config import *

def get_texts(url):

    text = ''
    request = requests.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    changes = soup.findAll("div", {"class": "patch-change-block"})
    for change in changes:
        contexts = change.findAll("blockquote", {"class": "blockquote context"})
        for context in contexts:
            # .text removes all kind of html tags
            text = text + context.text.replace("\t", " ").replace("\n", " ") + ' '

    return text
    
def main():
    
    # Check that the config file exists
    if not os.path.isfile("config.py"):
        print("You must create a config file")
        print("Please see config.example.py")
        exit(1)

    #account = Account(REDDIT_USERNAME, REDDIT_PASSWORD, "PGdevTest 0.1")
    #account.print_stats()

    #account.post_text_submission("test", "this is a test", "text test")
    #submission = account.post_url_submission("test", "this is a test", "http://imgur.com/gallery/eydpv2P")
    
    text = ''
    for i in range(1, 18):
        text = text + get_texts('http://euw.leagueoflegends.com/en/news/game-updates/patch/patch-6' + str(i) + '-notes')
    
    model = markovify.Text(text, state_size=2)

    for i in range(100):
      print(model.make_sentence())

if __name__ == "__main__":
    main()

