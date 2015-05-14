import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import db_model
import re
from SEAPI import SEAPI
from datetime import datetime, timedelta
import datetime
import traceback
from HTMLParser import HTMLParser
from collections import Counter
from urlparse import urlparse
import pprint
# Import our user settings
try:
    import user_settings

    CAN_USE_API = True
    if user_settings.DB_HOST and user_settings.DB_PASS \
            and user_settings.DB_USER and user_settings.DB_PORT and user_settings.DATABASE:
        CAN_USE_DATABASE = True
except ImportError, e:
    if e.message != 'No module named user_settings':
        logging.critical("No module found: {}".format(e.message))
        raise
    CAN_USE_API = False
    CAN_USE_DATABASE = False

if not CAN_USE_DATABASE:
    raise ValueError('No database connection information found. Information should be in user_settings.py')

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


def setup_logging(file_name, file_level=logging.INFO, console_level=logging.INFO, requests_level=logging.CRITICAL,
                  chatexchange_level=logging.CRITICAL):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create Console handler
    console_log = logging.StreamHandler()
    console_log.setLevel(console_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(name)-12s - %(message)s')
    console_log.setFormatter(formatter)
    logger.addHandler(console_log)

    # Log file
    file_log = logging.FileHandler('logs/%s.log' % (file_name), 'a', encoding='UTF-8')
    file_log.setLevel(file_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(name)-12s - %(message)s')
    file_log.setFormatter(formatter)
    logger.addHandler(file_log)

    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(requests_level)

    chatexchange_log = logging.getLogger('ChatExchange.chatexchange.client.Client')
    chatexchange_log.setLevel(chatexchange_level)

    chatexchange_log = logging.getLogger('ChatExchange.chatexchange.rooms.Room')
    chatexchange_log.setLevel(chatexchange_level)

    return logger


def retrieve_post(url):
    """
    Retrieves post information
    :param url: URL of post to retreive
    :return:
        dict: The post returned from the API
        string: The endpoint utilized
    """

    url_regex = r"(https?://(.*)\.com/((?:q(?:uestions)?|a(?:nswer)?))/(\d+)(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#(\d+))?)"
    endpoint_dict = {  # A quick look up dict to utilize for determining appropriate end point
                       "q": "questions",
                       "questions": "questions",
                       "a": "answers",
                       "answers": "answers",
    }

    matches = re.compile(url_regex, re.IGNORECASE).match(url)
    try:
        site_parameter = matches.group(2).split(".")[0]  # Not all sites are top level, some are site.stackexchange.com
    except AttributeError:
        logging.critical("URL Error: {}".format(url))
        logging.critical("   Groups: {}".format(matches))
        logging.critical("   Groups: {}".format(matches.groups()))
        return
    if matches.group(5) is None:
        endpoint = endpoint_dict[matches.group(3)]
        post_id = matches.group(4)
    else:
        if matches.group(3) in ['q', 'questions']:
            endpoint = 'answers'
            post_id = matches.group(5)

    if endpoint == "questions":
        filter = user_settings.API_QUESTION_FILTER
    elif endpoint == "answers":
        filter = user_settings.API_ANSWER_FILTER

    try:
        SITE = SEAPI.SEAPI(site_parameter, key=user_settings.API_KEY, access_token=user_settings.ACCESS_TOKEN)
    except SEAPI.SEAPIError as e:
        logging.critical("API Error occurred.")
        logging.critical("   Site Parameter: %s" % (site_parameter))
        logging.critical("   Error URL: %s" % (e.url))
        logging.critical("   Error Number: %s" % (e.error))
        logging.critical("   Error Code: %s" % (e.code))
        logging.critical("   Error Message: %s" % (e.message))
        return

    post = SITE.fetch("{}/{}".format(endpoint, post_id), filter=filter)

    try:
        data = post['items'][0]
    except IndexError:
        logging.critical(traceback.format_exc())
        logging.critical("Post:")
        logging.critical(post)
        raise

    return data, endpoint

def save_post(url=None, room_site=None, room_num=None, reason=None):
    '''Save a post's information by utilizing the StackExchange API'''
    if not CAN_USE_API:
        return

    post, endpoint = retrieve_post(url)
    save_post_to_db(post, endpoint, room_site, room_num, reason)


def save_post_to_db(data, endpoint=None, room_site=None, room_num=None, reason=None):
    '''
    :param data: Post from API stripped down to the `data` key
    :param endpoint: End point utilized
    :param room_site: Site the chatroom is one
    :param room_num: Room number of Chatroom
    :param reason: Reason for flag request
    :return: None
    '''
    s = connect_to_db()
    request_type_id = db_model.RequestType.by_type(s, reason)
    post_type_id = 1 if endpoint == "questions" else 2

    # Save the user fields to the database
    try:
        save_user(s, data[u'owner'])
    except KeyError:                    # Post has already been removed, we can't do anything with it
        logging.critical("No owner of post.")
        return

    try:
        save_user(s, data[u'last_editor'])
    except KeyError:
        pass

    # Dates
    closed_date = data.setdefault(u'closed_date', None)
    closed_date = None if not closed_date else datetime.datetime.fromtimestamp(closed_date)
    creation_date = data.setdefault(u'creation_date', None)
    creation_date = None if not creation_date else datetime.datetime.fromtimestamp(creation_date)
    last_activity_date = data.setdefault(u'last_activity_date', None)
    last_activity_date = None if not last_activity_date else datetime.datetime.fromtimestamp(last_activity_date)
    last_edit_date = data.setdefault(u'last_edit_date', None)
    last_edit_date = None if not last_edit_date else datetime.datetime.fromtimestamp(last_edit_date)
    locked_date = data.setdefault(u'locked_date', None)
    locked_date = None if not locked_date else datetime.datetime.fromtimestamp(locked_date)

    # Deeper values
    last_editor_id = data.setdefault(u'last_editor', None)
    last_editor_id = None if not last_editor_id else last_editor_id[u'user_id']
    owner_id = data.setdefault(u'owner', None)
    owner_id = None if not owner_id else owner_id['user_id']

    # Tags -> List to String
    tags = data.setdefault(u'tags',None)
    tags = None if not tags else ','.join(tags)

    # Save the post information to the database
    s.add(db_model.Post(
        post_type_id=post_type_id,
        answer_id=data.setdefault(u'answer_id', None),
        accepted_answer_id=data.setdefault(u'accepted_answer_id', None),
        body=data.setdefault(u'body', None),
        close_votes=data.setdefault(u'close_vote_count', None),
        closed_date=closed_date,
        closed_reason=data.setdefault(u'closed_reason', None),
        comment_count=data.setdefault(u'comment_count', None),
        creation_date=creation_date,
        delete_vote_count=data.setdefault(u'delete_vote_count', None),
        down_vote_count=data.setdefault(u'down_vote_count', None),
        favorite_count=data.setdefault(u'favorite_count', None),
        is_accepted=data.setdefault(u'is_accepted', None),
        last_activity_date=last_activity_date,
        last_edit_date=last_edit_date,
        last_editor_id=last_editor_id,
        link=data.setdefault(u'link', None),
        locked_date=locked_date,
        owner_id=owner_id,
        question_id=data.setdefault(u'question_id', None),
        reopen_vote_count=data.setdefault(u'reopen_vote_count', None),
        score=data.setdefault(u'score',None),
        tags=tags,
        title=data.setdefault(u'title',None),
        up_vote_count=data.setdefault(u'up_vote_count',None),
        view_count=data.setdefault(u'view_count',None),
        request_from_room_num=room_num,
        request_from_room_site=room_site,
        request_type_id=request_type_id,
        request_time=datetime.datetime.now()
    ))
    try:
        s.commit()
    except IntegrityError:
        s.rollback()


def save_user(s, user):
    '''Saves a user to the database. If user already exists, ignore.'''
    s.add(db_model.User(
        id=user['user_id'],
        name=user['display_name'],
        reputation=user['reputation'],
        link=user['link'],
        type=user['user_type']
    ))
    try:
        s.commit()
    except IntegrityError:
        s.rollback()


#def connect_to_db(db_name):
def connect_to_db():
    '''Connect to SQLite database'''
    logging.debug("Connecting to {}@{}".format(user_settings.DATABASE, user_settings.DB_HOST))
#    engine = create_engine(db_name, convert_unicode=True, echo=False)
    connect_string = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(user_settings.DB_USER, user_settings.DB_PASS,
                                                     user_settings.DB_HOST, user_settings.DB_PORT,
                                                     user_settings.DATABASE)
    engine = create_engine(connect_string, convert_unicode=True, echo=False)
    session = sessionmaker()
    session.configure(bind=engine)
    logging.debug('Connection to database initialized; returning session.')
    return session()


def print_spam_statistics():
    TODAY = datetime.date.today()
    FIRST_OF_MONTH = datetime.date(TODAY.year, TODAY.month, 1)
    urls = URLParser()
    domains = []

    s = connect_to_db()
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