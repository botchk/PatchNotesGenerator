import praw

class Account:

    def __init__(self, username, password, user_agent):
        self.username = username
        self.password = password
        self.user_agent = user_agent

    @property
    def session(self):
        if not hasattr(self, "_session"):
            self._session = praw.Reddit(self.user_agent)
            self._session.login(self.username, self.password, disable_warning=True)
        return self._session

    def print_stats(self):
        print('Username: ' + self.username)
        print('Comment karma: ', self.session.user.comment_karma)
        print('Link karma: ', self.session.user.link_karma)

    def post_text_submission(self, subreddit, title, text):
        """Posts a selftext submission on the given subreddit with the given title and text.
        Returns the submission made."""
        subreddit = self.session.get_subreddit(subreddit)
        return subreddit.submit(title, text=text, raise_captcha_exception=True)

    def post_url_submission(self, subreddit, title, url):
        """Posts a url submission on the given subreddit with the given title and url.
        Returns the submission made."""
        subreddit = self.session.get_subreddit(subreddit)
        return subreddit.submit(title, url=url, raise_captcha_exception=True)


