import os
import markovify
import requests

from reddit.account import Account
from bs4 import BeautifulSoup
from config import *

def get_texts(url):

    text = ''
    request = requests.get(url)
    
    if request.status_code == requests.codes.ok:
        request.raise_for_status()
        
        soup = BeautifulSoup(request.text, "html.parser")
        container = soup.find("div", {"id": "patch-notes-container"})
        summary = container.find_next("blockquote", {"class": "blockquote context"})
        #for context in contexts:
            # .text removes all kind of html tags
        text = text + summary.text.replace("\t", " ").replace("\n", " ") + ' '
    else:
        print("    ERROR status_code: " + str(request.status_code))
    return text
    
def main():
    
    # Check that the config file exists
    if not os.path.isfile("config.py"):
        print("config.py not found")
        print("see config.example.py")
        exit(1)

    #account = Account(REDDIT_USERNAME, REDDIT_PASSWORD, "PGdevTest 0.1")
    #account.print_stats()

    #account.post_text_submission("test", "this is a test", "text test")
    #submission = account.post_url_submission("test", "this is a test", "http://imgur.com/gallery/eydpv2P")
    
    text = ''
    base_url = 'http://euw.leagueoflegends.com/en/news/game-updates/patch/patch-'
    patches = {5:24, 6:24, 7:16}
    
    print("Parsing: ")
    for year, max_number in patches.items():
        for number in range(1, max_number + 1):
            url = base_url + str(year) + str(number) + '-notes'
            print("  * " + url)
            text = text + get_texts(url).encode("utf-8")
    
    model = markovify.Text(text, state_size=2)

    with open("out.txt", "w") as file:
        for i in range(100):
            file.write(str(model.make_sentence()))
            file.write("\n")

if __name__ == "__main__":
    main()

