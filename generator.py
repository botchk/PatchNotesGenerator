from reddit.account import Account
import os
from config import *

# Check that the file that contains our username exists
if not os.path.isfile("config.py"):
    print "You must create a config file with your username and password."
    print "Please see config.example.py"
    exit(1)

account = Account(REDDIT_USERNAME, REDDIT_PASSWORD, "PGdevTest 0.1")
account.print_stats()
#account.post_text_submission("test", "this is a test", "text test")
submission = account.post_url_submission("test", "this is a test", "http://imgur.com/gallery/eydpv2P")
print(submission)
