import json
import pprint
import re
from HTMLParser import HTMLParser

with open('patterns.txt', 'r') as f:
    patterns = json.load(f)

pprint.pprint(patterns, indent=4)
print patterns[-1]['regex']

test_strings = [
    "[tag:cv-pls-too-broad-offsite-resource-unclear-whatever] http://stackoverflow.com/questions/25959443/how-do-i-create-a-hierarchical-state-machine-using-c-sharp",
    "[tag:cv-pls-offsite-resource] http://stackoverflow.com/questions/25953631/list-of-resources-to-learn-hierarchical-state-machine",
    "[tag:cv-plz-2048](http://stackoverflow.com/questions/25957854/optimal-algorithm-to-lose-game-2048)",
    "[tag:cv-plz] http://stackoverflow.com/questions/3272285/dns-issue-www-example-not-working-but-example-com-does (very old question, off-topic) ",
    "naa - http://stackoverflow.com/a/25905260/2982225 ",
    "naa finished @DroidDev ",
    "[tag:cv-pls] no-repro http://stackoverflow.com/q/18114801/3622940 see op answer ",
    "\[[Blaze](https://github.com/Charcoal-SE/Blaze)] answer flagged by Undo: http://stackoverflow.com/a/26389222 ",
    "[tag:cv-pls]: http://meta.stackexchange.com/questions/242741/i-have-two-emacs-buffers-in-a-frame-a-cc-b-cc"
]

room_base_message = "from [%s](http://chat.%s/rooms/%s/)" % ('TESTING!', "TESTING.NONE", 89)

for content in test_strings:
    for p in patterns:
        matches = re.compile(p['regex'], re.IGNORECASE).match(content)
        if matches:
            reason_msg = ""
            message = "**%s** for %s by %s %s" % (p['translation'], matches.group(4),
                                                      "TEST_USER", room_base_message)
            if matches.group(2) or matches.group(3):
                if matches.group(3):
                    if matches.group(3).strip() not in ("(","-"):
                        reason_msg += " %s " % (matches.group(3))
                if matches.group(2):
                    reason_msg += " %s " % (matches.group(2).replace("-"," "))
            if reason_msg:
                message += " Reason: {}".format(reason_msg)
            print message
            print

