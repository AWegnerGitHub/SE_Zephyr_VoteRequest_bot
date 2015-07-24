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
from SEAPI import SEAPI
import re
import logging
import user_settings
import traceback
from textstat.textstat import textstat
from bs4 import BeautifulSoup
from textblob import TextBlob
from collections import Counter
import re, htmlentitydefs
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

commands = {
    'spamreport': {'restricted': True,
                   'restricted_users': [66258,      # Andy
                                        186281,     # Andy
                                        ],
                   'command': 'print_spam_statistics',
                   'description': 'Show statistics on spam Zephyr has seen this month',
                   'usage': None
                   },
    'analyzepost': {'restricted': True,
                   'restricted_users': [66258,      # Andy
                                        186281,     # Andy
                                        ],
                   'command': 'print_post_analysis',
                   'description': 'Show text features of a post, passed by a URL to post (This command eats an API call)',
                   'usage': 'analyzepost <url>'
                   },
    'zephyrhelp': {'restricted': False,
                   'restricted_users': [],
                   'command': 'print_help',
                   'description': 'Show commands accessible by Zephyr',
                   'usage': None
                   },

}

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


class TextFeature(object):
    """
    A single feature, and related attributes, of a piece of text

    :param name: The name of this feature

    Other attributes:
        value: The value associated with this feature; Can be any object
        group_by: An id used to associated this feature with other features
    """
    def __init__(self, name, value = None, group_by = None):
        self.name = name
        self.value = value
        self.group_by = group_by

    def __repr__(self):
        return "TextFeature(name = '{}', value = {}, group_by = {})".format(
            self.name,
            self.value,
            self.group_by
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.value == other.value:
                return True
            else:
                return False

    def __ne__(self, other):
        return not self.__eq__(other)


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

    url_regex = r"((?:https?:)?//(.*)\.(?:com|net)/((?:q(?:uestions)?|a(?:nswer)?))/(\d+)(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#(\d+))?)"
    endpoint_dict = {  # A quick look up dict to utilize for determining appropriate end point
                       "q": "questions",
                       "questions": "questions",
                       "a": "answers",
                       "answers": "answers",
    }

    matches = re.compile(url_regex, re.IGNORECASE).match(url)
    try:
        site_parameter = matches.group(2).split(".")[0]  # Not all sites are top level, some are site.stackexchange.com
        if site_parameter in ['ru', 'pt']:
            site_parameter += ".stackoverflow"
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
    except ValueError:
        logging.critical("API Error occurred.")
        logging.critical("   Invalid Site name provided: {}".format(site_parameter))
        return

    post = SITE.fetch("{}/{}".format(endpoint, post_id), filter=filter)

    try:
        data = post['items'][0]
    except IndexError:
        logging.info("   No 'items' for {}/{}:".format(endpoint, post_id))
        data = None

    return data, endpoint

def save_post(url=None, room_site=None, room_num=None, reason=None):
    '''Save a post's information by utilizing the StackExchange API'''
    if not CAN_USE_API:
        return

    try:
        post, endpoint = retrieve_post(url)
    except TypeError:
        post = None
    if post:
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

    # See if post is already reported
    existing = s.query(db_model.Post).filter_by(question_id=data.setdefault(u'question_id', None), answer_id=data.setdefault(u'answer_id', None), link=data.setdefault(u'link', None)).first()
    if not existing:
        request_type_id = db_model.RequestType.by_type(s, reason)
        post_type_id = 1 if endpoint == "questions" else 2

        # Save the user fields to the database
        try:
            save_user(s, data[u'owner'])
        except KeyError:                    # Post has already been removed, we can't do anything with it
            logging.info("   No owner of post.")
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
    else:
        logging.debug("   Post already reported.")

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


def unescape(text):
    """
    Converts HTML entities to friendly strings

    http://effbot.org/zone/re-sub.htm#unescape-html
    :param text: HTML/XML text
    :return: string
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def print_spam_statistics(content=None):
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


def process_text(text):
    """
    Processes the text passed and prints results
    :param text: Text string to process
    :return: dict: Results of various tests
    """
    no_code_text, num_code_blocks = _strip_code_blocks(text)

    results = []
    group_by = 'Basic Text Statistics'
    results.append(TextFeature('Number of Code Blocks', num_code_blocks, group_by))
    results.extend(_get_base_textstats(no_code_text))
    results.extend(_get_detailed_stats(no_code_text))
    results.extend(_get_reading_stats(no_code_text))
    return results


def format_results(results, url, title):
    """
    Prints a report from the passed results
    :param results: list: Containing the resultset
    :param url: string: URL that was checked
    :param title: string: Title of post
    :return: None
    """
    message = "     \n"
    message += "    Report for {}\n".format(unescape(title))
    message += "       {}\n".format(url)
    current_group = None
    for r in results:
        if r.group_by != current_group:
            current_group = r.group_by
            message += "    \n"
            message += "       {}\n".format(r.group_by)
        message += "    {}: {}\n".format(r.name, r.value)
    return message


def _count_code_blocks(no_code_soup):
    """
    Counts the number of code blocks in the soup passed
    :param no_code_soup: Soup to check for code blocks
    :return: int: Number of code blocks
    """
    num_code_blocks = 0
    for pre_tag in no_code_soup.find_all('pre'):
        if pre_tag.find('code'):
            num_code_blocks += 1
            no_code_soup.pre.decompose()
    return num_code_blocks

def _get_base_textstats(no_code_text):
    """
    Find basic text statistics
    :param no_code_text: Text we are analyzing
    :return: list: List of results
    """
    results = []
    group_by = 'Basic Text Statistics'
    num_chars = len(no_code_text)
    num_lower = sum(1 for c in no_code_text if c.islower())
    num_upper = sum(1 for c in no_code_text if c.isupper())
    num_letters = sum(1 for c in no_code_text if c.isalpha())
    num_numbers = sum(1 for c in no_code_text if c.isdigit())
    num_alphanum = sum(1 for c in no_code_text if c.isalnum())
    num_otherchars = num_chars - num_alphanum
    results.append(TextFeature('Number of characters', num_chars, group_by))
    results.append(TextFeature('Number of letters', num_letters, group_by))
    results.append(TextFeature('Number of numbers', num_numbers, group_by))
    results.append(TextFeature('Number of other characters', num_otherchars, group_by))
    character_counts = Counter(no_code_text.lower())
    for c in sorted(character_counts.items()):
        try:
            results.append(TextFeature('Character count for "{}"'.format(c[0].encode('unicode_escape')), c[1], group_by))
        except AttributeError:
            results.append(TextFeature('Character count for "{}"'.format(c[0]), c[1], group_by))

    results.append(TextFeature('Number of syllables', textstat.syllable_count(no_code_text), group_by))
    results.append(TextFeature('Lexicon Count (without punctuation)', textstat.lexicon_count(no_code_text, True), group_by))
    results.append(TextFeature('Lexicon Count (with punctuation)', textstat.lexicon_count(no_code_text, False), group_by))
    results.append(TextFeature('Number of lower case characters', num_lower, group_by))
    results.append(TextFeature('Number of upper case characters', num_upper, group_by))
    return results


def _get_detailed_stats(no_code_text):
    """
    Returns detailed stats on text
    :param no_code_text: String to analyse
    :return: list of details
    """
    results = []
    group_by = 'Detailed Text Statistics'
    tb = TextBlob(no_code_text)
    # Spell check here...it's very slow
    results.append(TextFeature('Number of sentences', textstat.sentence_count(no_code_text), group_by))
    results.append(TextFeature('Number of sentences (again)', len(tb.sentences), group_by))
    results.append(TextFeature('Number of words', len(tb.words), group_by))
    results.append(TextFeature('Sentiment Polarity', tb.sentiment.polarity, group_by))
    results.append(TextFeature('Sentiment Subjectivity', tb.sentiment.subjectivity, group_by))
    results.append(TextFeature('Detected Language', tb.detect_language(), group_by))
    results.append(TextFeature('Number of important phrases', len(tb.noun_phrases), group_by))
    results.append(TextFeature('Number of word bi-grams', len(tb.ngrams(2)), group_by))
    results.append(TextFeature('Number of word tri-grams', len(tb.ngrams(3)), group_by))
    results.append(TextFeature('Number of word 4-grams', len(tb.ngrams(4)), group_by))
    return results


def _get_reading_stats(no_code_text):
    """
    Returns reading level information
    :param no_code_text: String to analyse
    :return: list of details
    """
    group_by = 'Reading Level Analysis '
    results = []
    results.append(TextFeature('Flesch Reading Ease', textstat.flesch_reading_ease(no_code_text), group_by))        # higher is better, scale 0 to 100
    results.append(TextFeature('Flesch-Kincaid Grade Level', textstat.flesch_kincaid_grade(no_code_text), group_by))
    try:
        results.append(TextFeature('The Fog Scale (Gunning FOG formula)', textstat.gunning_fog(no_code_text), group_by))
    except IndexError:  # Not sure why, but this test throws this error sometimes
        results.append(TextFeature('The Fog Scale (Gunning FOG formula)', "Undetermined", group_by))
    try:
        results.append(TextFeature('The SMOG Index', textstat.smog_index(no_code_text), group_by))
    except IndexError:  # Not sure why, but this test throws this error sometimes
        results.append(TextFeature('The SMOG Index', "Undetermined", group_by))
    results.append(TextFeature('Automated Readability Index', textstat.automated_readability_index(no_code_text), group_by))
    results.append(TextFeature('The Coleman-Liau Index', textstat.coleman_liau_index(no_code_text), group_by))
    try:
        results.append(TextFeature('Linsear Write Formula', textstat.linsear_write_formula(no_code_text), group_by))
    except IndexError:
        results.append(TextFeature('Linsear Write Formula', "Undetermined", group_by))
    try:
        results.append(TextFeature('Dale Chall Readability Score', textstat.dale_chall_readability_score(no_code_text), group_by))
    except IndexError:  # Not sure why, but this test throws this error sometimes
        results.append(TextFeature('Dale Chall Readability Score', "Undetermined", group_by))

    try:
        results.append(TextFeature('Readability Consensus', textstat.readability_consensus(no_code_text), group_by))
    except (TypeError, IndexError):
        results.append(TextFeature('Readability Consensus', "Undetermined; One of the tests above failed.", group_by))
    return results


def _strip_code_blocks(text):
    """
    Strips the code blocks from text
    :param text: Text that we want code blocks removed from
    :return: string: text without code blocks
             int: number of code blocks removed
    """

    no_code_soup = BeautifulSoup(text)
    num_code_blocks = _count_code_blocks(no_code_soup)
    no_code_text = no_code_soup.get_text()
    return no_code_text, num_code_blocks

def print_post_analysis(content=None):
    """
    Returns the analysis of post
    :param content: Message received from chat
    :return: string: message to post
    """
    post_to_check = content.split(" ")[1]
    data, endpoint = retrieve_post(post_to_check)
    body = data.setdefault(u'body', None)
    title = data.setdefault(u'title',None)
    return format_results(process_text(body), post_to_check, title)

def print_help(content=None):
    """
    Returns Zephyr's help contents
    :param content:
    :return:
    """
    message = "    \n"
    for c in sorted(commands.keys()):
        message += "    "
        if commands[c]['usage']:
            message += "{}: {} (exampe: '{}')".format(c, commands[c]['description'], commands[c]['usage'])
        else:
            message += "{}: {}".format(c, commands[c]['description'])
        if commands[c]['restricted']:
            message += " **Restricted Command** "
        message += "\n"
    return message