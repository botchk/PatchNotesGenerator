class Patch():
    
    def __init__(self, number, summary):
        self.number = number
        self.summary = summary
        self.champions = {}
        
    def add_champion(self, champion):
        self.champions[champion.name] = champion


class Champion():
    
    def __init__(self, name):
        self.name = name
        self.short_summary = ""
        self.summary = ""


def serialize(obj):
    if isinstance(obj, Patch) or isinstance(obj, Champion):
        return obj.__dict__
    else:
        raise TypeError ("Type not serializable")