# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import logging
import logging.handlers
import re
import threading
import time
import traceback
import requests
import sys
import ChatExchange.chatexchange.client
import ChatExchange.chatexchange.events
import json
from Queue import Queue
import logging
from utils import utils
import os
import threading
import string

logging = utils.setup_logging("zephyr_monitor", file_level=logging.INFO, console_level=logging.INFO,
                              requests_level=logging.CRITICAL, chatexchange_level=logging.CRITICAL)

# Import our user settings
try:
    import user_settings
except ImportError, e:
    if e.message != 'No module named user_settings':
        logging.critical("No module found: {}".format(e.message))
        raise
    import getpass
   
try:
    email = user_settings.email
    password = user_settings.password
except NameError:
    email = raw_input('Email Address: ')
    password = getpass.getpass('Password: ')

bots = []
message_queue = Queue()
REASON_CLEAN_REGEX = '^[tag:][.!,;:\-()]'

commands = {
    'spamreport': {'restricted': True,
                   'restricted_users': [66258,      # Andy
                                        186281,     # Andy
                                        ],
                   'command': 'print_spam_statistics'}

}


class ChatMonitorBot(threading.Thread):
    def __init__(self, queue, room_num, room_site=None,
                 monitor_room=False, post_requests=False, monitor_patterns=None):
        """Set up a bot to connect to a specific room.

        :param room_num: The room number the bot will join
        :param room_site: The site the room is hosted on:
            stackoverflow.com, meta.stackexchange.com, stackexchange.com
        :param monitor_room: Boolean value used to determine if this room is monitored for matching patterns
        :param post_requests: Boolean value used to deteramin if vote requests are posted to this room
        :param monitor_patterns: Patterns that the bot is watching for
        """
        super(ChatMonitorBot, self).__init__()
        self.room_number = room_num
        self.site = room_site
        self.monitor_room = monitor_room
        self.post_requests = post_requests
        self.client = ChatExchange.chatexchange.client.Client(self.site)
        self.client.login(email, password)
        self.room = self.client.get_room(self.room_number)
        self.enabled = True
        self.running = True
        self.daemon = True
        self.queue = queue
        self.room_base_message = None
        self.patterns = monitor_patterns

    def run(self):
        """Join/monitor room"""
        self.room.join()
        if not self.monitor_room:
            self.patterns = []
        self.room.watch_socket(self.on_event)
        self.update_room_information()

        logging.info("Starting bot in {} => {}".format(filter(lambda x: x in string.printable, self.room.name.strip()), self.room_number))

        while self.running:
            time.sleep(0.25)

    def update_room_information(self):
        self.room.scrape_info()
        room_name = (filter(lambda x: x in string.printable, self.room.name.strip())).replace("[","\[").replace("]","\]")
        self.room_base_message = "from [%s](http://chat.%s/rooms/%s/)" % (room_name, self.site, self.room_number)

    def on_event(self, event, client):
        should_return = False
        if not self.enabled:
            should_return = True
        if not self.running:
            should_return = True
        if not isinstance(event, ChatExchange.chatexchange.events.MessagePosted) and not isinstance(event, ChatExchange.chatexchange.events.UserMentioned):
            should_return = True
        if should_return:
            return

        message = event.message

        if event.user.id == self.client.get_me().id:
            return

        # This prints the bot was messaged in multiple rooms
        # if isinstance(event, ChatExchange.chatexchange.events.UserMentioned):
        #     print "     Mentioned in %s by %s" % (self.room.name, self.client.get_user(event.user.id).name)

        h = HTMLParser()
        should_check_message = False
        try:
            content = h.unescape(message.content_source).strip()
            should_check_message = True
        except requests.exceptions.HTTPError, e:
            logging.debug("   404 Raised. Ignoring message.")
            logging.debug("   Occurred in %s by user %s" % (self.room_base_message, self.client.get_user(event.user.id).name))
            logging.debug("   Error %s" % (e))
            logging.debug(traceback.format_exc())
        except requests.exceptions.ConnectionError, e:
            logging.debug("   Connection Error.")
            logging.debug("   Occurred in %s by user %s" % (self.room_base_message, self.client.get_user(event.user.id).name))
            logging.debug("   Error %s" % (e))
            logging.debug(traceback.format_exc())

        if should_check_message:
            for p in self.patterns:
                matches = re.compile(p['regex'], re.IGNORECASE).match(content)
                if matches:
                    message = u"**%s** for %s by %s %s" % (p['translation'], matches.group(4),
                                                          self.client.get_user(event.user.id).name,
                                                          self.room_base_message)
                    reason_msg = ""
                    if matches.group(2) or matches.group(3):
                        if matches.group(3):
                            if matches.group(3).strip() not in ("(","-",":"):
                                reason_msg += u" %s " % (re.sub(REASON_CLEAN_REGEX,"",matches.group(3)))
                        if matches.group(2):
                            reason_msg += u" %s " % (re.sub(REASON_CLEAN_REGEX,"",matches.group(2)))
                    if reason_msg:
                        message += u" Reason: {}".format(reason_msg)
                    if p['should_post']:
                        message_queue.put(message)
                    if matches.group(4):
                        thr = threading.Thread(target=utils.save_post, args=(matches.group(4), self.site, self.room_number, p['translation']))
                        thr.start()
                    else:
                        logging.critical("   No group 4 matches:")
                        logging.critical("   Content: {}".format(content))
                        logging.critical("   Matches: {}".format(matches.groups()))
            if content in commands:
                if commands[content]['restricted']:
                    if event.user.id in commands[content]['restricted_users']:
                        self.room.send_message(getattr(utils, commands[content]['command'])())



    def post_request_message(self, message):
        logging.info(u"{}".format(message))
        self.room.send_message(message)


if __name__ == '__main__':
    with open('rooms.txt', 'r') as f:
        rooms = json.load(f)

    with open('patterns.txt', 'r') as f:
        patterns = json.load(f)

    for r in rooms:
        bots.append(ChatMonitorBot(message_queue, r['room_num'], r['site'], r['monitor'], r['post_requests'], patterns))

    for b in bots:
        b.start()

    while True:
        val = message_queue.get()
        if val is None:
            break
        else:
            for b in bots:
                if b.post_requests:
                    try:
                        b.post_request_message(val)
                    except requests.exceptions.ConnectionError, e:
                        logging.critical("Error printing to room")
                        logging.critical("Connection error %s" % (e))
        for b in bots:
            if not b.isAlive():
                print b, "is dead!"
