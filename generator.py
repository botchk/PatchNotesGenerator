import os
import markovify
import codecs
import json

from patch import Patch
from patch import Champion
from patch import serialize as patch_serialize

#relative data directory for storing parsed patches
data_dir = "data"

#relative out directory for storing generated patches
out_dir = "out"

def print_text(text, indentation):
    print((" " * indentation) + text)
    
    
#print with bullet point in front
def print_bullet_point(text, indentation):
    print_text("* " + text, indentation)
  
    
def generate_summary(summaries):
    summary = ''
    welcome_model = markovify.Text(summaries, state_size=2)
    summary = welcome_model.make_sentence_with_start('Welcome')
    
    corpus_model = markovify.Text(summaries, state_size=2)
    for i in range(1,20):
        sentence = corpus_model.make_sentence()
        while sentence == None or "Welcome" in sentence:
            sentence = corpus_model.make_sentence()
            
        summary = summary + ' ' + sentence
    
    return summary


def generate_sentence(input, attempts, state_size):
    if input:
        sentence = ''
        repeat = 0
        while not sentence and attempts > 0:
            model = markovify.Text(input, state_size=state_size)
            sentence = model.make_sentence()
            attempts-=1
        return sentence
    else:
        return ''

        
def main(): 
    patches = {}
    merged_champions = {}
    
    with codecs.open(os.path.join(data_dir, "patches"), "r", "utf-8") as file:
        patches = json.load(file)
        
    summaries = ""
    for patch in patches.values():
        summaries += patch['summary']
        for champion in patch['champions']:
            if champion['name'] in merged_champions:
                merged_champions[champion['name']].summary += ' ' + champion['summary']
                merged_champions[champion['name']].description += ' ' + champion['description']
            else:
                merged_champions[champion['name']] = Champion(champion['name'])
                merged_champions[champion['name']].summary = champion['summary']
                merged_champions[champion['name']].description = champion['description']

    summary = generate_summary(summaries)

    for champion in merged_champions.values():
        champion.summary = generate_sentence(champion.summary, 20, 1)
        champion.description = generate_sentence(champion.description, 15, 2)

    generated_patch = Patch('generated', summary)
    generated_patch.champions = merged_champions

    with codecs.open(os.path.join(out_dir, "patch"), "w", "utf-8") as file:
        json.dump(generated_patch, file, default=patch_serialize, indent=4)
    

if __name__ == "__main__":
    main()

