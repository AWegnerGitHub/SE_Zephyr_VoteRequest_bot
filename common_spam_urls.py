from HTMLParser import HTMLParser
from collections import Counter
from urlparse import urlparse
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import utils.db_model as db_model
from utils import utils
import datetime

TODAY = datetime.date.today()
FIRST_OF_MONTH = datetime.date(TODAY.year, TODAY.month, 1)


class URLParser(HTMLParser):
    """ Extract URLs from a string """

    def __init__(self, output_list=None):
        HTMLParser.__init__(self)
        if output_list is None:
            self.output_list = []
        else:
            self.output_list = output_list

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.output_list.append(dict(attrs).get('href'))

def print_spam_statistics():

    urls = URLParser()
    domains = []

    s = utils.connect_to_db("sqlite:///zephyr_vote_requests.db")
    now = datetime.datetime.now()
    spam_posts = s.query(db_model.Post).filter(
        db_model.Post.request_type_id == 9,  # Spam Type
        db_model.Post.request_time >= FIRST_OF_MONTH
    ).all()

    for spam in spam_posts:
        urls.feed(spam.body)

    for url in urls.output_list:
        parsed_uri = urlparse(url)
        domains.append('{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri))

    unique_urls = list(set(urls.output_list))
    unique_domains = list(set(domains))
    count_urls = Counter(urls.output_list)
    count_domains = Counter(domains)

    message = "     \n"
    message += "    Spam URLs seen by Zephyr in {}\n".format(TODAY.strftime("%B %Y"))
    message += "    Total URLs: {}\n".format(len(urls.output_list))
    message += "    Total Domains: {}\n".format(len(domains))
    message += "    Total Unique URLs: {}\n".format(len(unique_urls))
    message += "    Total Unique domains: {}\n".format(len(unique_domains))
    message += "    \n"
    message += "    20 Most Common (Domains):\n"
    message += "    " + ("-" * 20) + "\n"
    for url, count in count_domains.most_common(20):
        message += "      {count}  {url}\n".format(count=count, url=url)
    message += "    \n"
    message += "    20 Most Common (Full Path):\n"
    message += "    " + ("-" * 20) + "\n"
    for url, count in count_urls.most_common(20):
        message += "      {count}  {url}\n".format(count=count, url=url)
    return message