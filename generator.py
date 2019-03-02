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
  
    
def generate_patch_summary(summaries):
    summary = ''
    welcome_model = markovify.Text(summaries, state_size=2)
    summary = welcome_model.make_sentence_with_start('Welcome')
    
    corpus_model = markovify.Text(summaries, state_size=2)
    for _ in range(1,20):
        sentence = corpus_model.make_sentence()
        while sentence == None or "Welcome" in sentence:
            sentence = corpus_model.make_sentence()
            
        summary = summary + ' ' + sentence
    
    return summary


def generate_sentence(input, attempts, state_size):
    sentence = ''
    model = markovify.Text(input, state_size=state_size)
    while not sentence and attempts > 0:
        sentence = model.make_sentence()
        attempts -= 1
    return sentence

        
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
                merged_champions[champion['name']].short_summary += ' ' + champion['short_summary']
                merged_champions[champion['name']].summary += ' ' + champion['summary']
            else:
                merged_champions[champion['name']] = Champion(champion['name'])
                merged_champions[champion['name']].short_summary = champion['short_summary']
                merged_champions[champion['name']].summary = champion['summary']

    summary = generate_patch_summary(summaries)

    for champion in merged_champions.values():
        champion.short_summary = generate_sentence(champion.short_summary, 20, 1)
        champion.summary = generate_sentence(champion.summary, 15, 2)

    generated_patch = Patch('generated', summary)
    generated_patch.champions = merged_champions

    with codecs.open(os.path.join(out_dir, "patch"), "w", "utf-8") as file:
        json.dump(generated_patch, file, default=patch_serialize, indent=4)
    

if __name__ == "__main__":
    main()

