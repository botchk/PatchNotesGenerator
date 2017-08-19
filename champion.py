# TODO rename summary to short_description or stuff like that
class Champion():
    
    def __init__(self, name):
        self.name = name
        self.summaries = ""
        self.descriptions = ""
        
    def add_summary(self, summary):
        self.summaries += " " + summary
    
    def add_description(self, description):
        self.descriptions += " " + description