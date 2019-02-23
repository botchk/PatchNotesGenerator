import os
import markovify
import pickle as pickle
import codecs

from champion import Champion

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
            
        summary = summary + '\n' + sentence
    
    return summary

        
def main(): 
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
    

if __name__ == "__main__":
    main()

