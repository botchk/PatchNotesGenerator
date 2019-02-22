import os
import markovify
import requests
import argparse
import pickle as pickle
import codecs

from champion import Champion
from bs4 import BeautifulSoup

url_start = 'http://euw.leagueoflegends.com/en/news/game-updates/patch/patch-'
url_end = '-notes'

#year:highest_patch
patches = {5:24}
# patches = {5:24, 6:24, 7:24, 8:24, 9:4}

#relative data directory for storing parsed patches
data_dir = "data"

#relative out directory for storing generated patches
out_dir = "out"

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
    print("cleaning data directory...")
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
            
    with codecs.open(os.path.join(data_dir, "summaries"), "w", "utf-8") as file:
        file.write(summaries)
        
    with codecs.open(os.path.join(data_dir, "champions"), "wb") as file:
        pickle.dump(champions_merged, file)
    
        
def generate():
    summaries = ''
    champions = {}
    with codecs.open(os.path.join(data_dir, "summaries"), "r", "utf-8") as file:
        summaries = file.read()
        
    with open(os.path.join(data_dir, "champions"), "rb") as file:
        champions = pickle.load(file)
        
    for key, champion in champions.items():
        print(champion.name)
        print(champion.summaries)
        
    summary = generate_summary(summaries)
    
    with codecs.open(os.path.join(out_dir, "summary"), "w", "utf-8") as file:
        file.write(summary)

        
def clean():
    print_bullet_point("data", 2)
    clean_dir(data_dir)
    print_bullet_point("out", 2)
    clean_dir(out_dir)
    
    
#delete all files in given dir
def clean_dir(dir):
    for file in os.listdir(dir):
        os.unlink(os.path.join(dir, file))
        
        
#creates directory if it does not exist already
def make_dir(dir):
    if not os.path.exists(dir):
        print("create directory " + dir)
        os.makedirs(dir) 
        
        
def main(): 
    parser = argparse.ArgumentParser(description='League of Legends patch notes generator')
    parser.add_argument('-c', '--clean', action="store_true", default=False,
                        dest='clean', help='cleanes data and out directories')
    parser.add_argument('-p', '--parse', action="store_true", default=False,
                        dest='parse', help='parses the patch notes and generates content files')
    parser.add_argument('-g', '--generate', action="store_true", default=False,
                        dest='generate', help='generates patch notes out of content files')
    
    make_dir(data_dir)
    make_dir(out_dir)
    
    args = parser.parse_args()
    
    if args.clean:
        print("cleaning directories...")
        clean()
    
    if args.parse:
        print("parsing patch notes...")
        parse()
        
    if args.generate:
        print("generating patch notes...")
        generate()
    

if __name__ == "__main__":
    main()

