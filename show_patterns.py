import json
import pprint
import re
from HTMLParser import HTMLParser
from utils import utils
import threading


with open('patterns.txt', 'r') as f:
    patterns = json.load(f)

pprint.pprint(patterns, indent=4)

test_strings = [
    "[tag:cv-pls-too-broad-offsite-resource-unclear-whatever] http://stackoverflow.com/questions/25959443/how-do-i-create-a-hierarchical-state-machine-using-c-sharp",
    "[tag:cv-pls-offsite-resource] http://stackoverflow.com/questions/25953631/list-of-resources-to-learn-hierarchical-state-machine",
    "[tag:cv-plz-2048](http://stackoverflow.com/questions/25957854/optimal-algorithm-to-lose-game-2048)",
    "[tag:cv-plz] http://stackoverflow.com/questions/3272285/dns-issue-www-example-not-working-but-example-com-does (very old question, off-topic) ",
    "naa - http://stackoverflow.com/a/25905260/2982225 ",
    "naa finished @DroidDev ",
    "[tag:cv-pls] no-repro http://stackoverflow.com/q/18114801/3622940 see op answer ",
    "\[[Blaze](https://github.com/Charcoal-SE/Blaze)] answer flagged by Undo: http://stackoverflow.com/a/26389222 ",
    "[tag:cv-pls]: http://meta.stackexchange.com/questions/242741/i-have-two-emacs-buffers-in-a-frame-a-cc-b-cc",
    "cv-pls last recommendation for a bit http://stackoverflow.com/q/26357391/189134",
    "[tag:cv-pls] too broad: http://stackoverflow.com/questions/26734497/convert-bytes-array-to-video",
    "[tag:cv-pls] not an MCVE: http://stackoverflow.com/q/26734489/1234256",
    "[tag:cv-pls] non-eng http://stackoverflow.com/q/26736764/656243",
    "cv-pls recommendation http://stackoverflow.com/q/2168701/189134 ",
    "**Spam** **Q** (100%): [AVG Tech Support Toll Free Number 1-855-205-0915 USA](http://travel.stackexchange.com/questions/38253), by [Jessica Florence](http://travel.stackexchange.com/users/22302), on `travel.stackexchange.com`.",
    "**Spam** **A** (27.3%): [You can use ssh -v flag to get more output f...](http://superuser.com/a/835804), by [user2986553](http://superuser.com/users/386641), on `superuser.com`. ",
    "[tag:nuke-pls] *shudder* http://stackoverflow.com/questions/1543107",
    "[tag:cv-pls] *shudder* http://stackoverflow.com/questions/1543107",
    "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in title: [1 866 978 6819 gmail account recovery contact number 1 866 978 6819 gmail account recovery phone number](http://stackoverflow.com/questions/27363275/1-866-978-6819-gmail-account-recovery-contact-number-1-866-978-6819-gmail-accoun) by [ab cl](http://stackoverflow.com/users/4338254/ab-cl) on `stackoverflow.com` ",
    "[tag:Cv-pls] [tag:wtf] http://stackoverflow.com/questions/27381564/how-to-write-an-screen-driver-in-nasm ",
    "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in title, Phone number detected: [support for yahoo mail 18669786819 @call for helpline number](http://stackoverflow.com/questions/27385010/support-for-yahoo-mail-18669786819-call-for-helpline-number) by [jas rat](http://stackoverflow.com/users/4330380/jas-rat) on `stackoverflow.com` ",
    "[tag:cv-pls] [tag:toolrecommendation] cv-pls http://stackoverflow.com/q/27385198/1234256 ",
    "[tag:cv-pls] [tag:too-broad] http://stackoverflow.com/q/27385313/1234256 It's [tag:too-broad] ",
    "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in title, Bad keyword in username, Phone number detected: [Inter Caste +917689070805 @ LoVe marriagE SpEcialiSt baba Ji](http://askubuntu.com/questions/560666/inter-caste-917689070805-love-marriage-specialist-baba-ji) by [babaji](http://askubuntu.com/users/358135/babaji) on `askubuntu.com` ",
    "**Spam** **A** (100%): [send me a letter to pochtaname@gmail.ru](http://mathoverflow.net/a/190649), by [Sergei](http://mathoverflow.net/users/49208/sergei), on `mathoverflow.net`. ",
    "[tag:cv-plz] http://stackoverflow.com/questions/27669972/folder-structure-of-a-smacss-project-where-to-put-class (opinionated)",
    "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Blacklisted website: [The product hydrates the skin](http://meta.stackexchange.com/questions/250231/the-product-hydrates-the-skin) by [victor frith](http://meta.stackexchange.com/users/284891/victor-frith) on `meta.stackexchange.com` ",
    "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in body, Blacklisted website: [However take that same aesthetic and put](http://drupal.stackexchange.com/questions/152240/however-take-that-same-aesthetic-and-put) by [olivianewton](http://drupal.stackexchange.com/users/45453/olivianewton) on `drupal.stackexchange.com` ",
    "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in body: [It provides high level of skin moisture?](http://askubuntu.com/questions/616676/it-provides-high-level-of-skin-moisture) by [tkeikaw Ixji](http://askubuntu.com/users/403751/tkeikaw-ixji) on `askubuntu.com` ",
    "[tag:cv-pls] http://stackoverflow.com/questions/30244930/how-to-implement-material-design-in-android-studio ",
    """**Spam** **Q** ([`TPA`'d by Sam](http://chat.meta.stackexchange.com/transcript/message/3442749)): [More aerodynamic router designs need](http://drupal.stackexchange.com/questions/158348 "Score: 0"), by [?](http://chat.meta.stackexchange.com/transcript/message/2998326) [john](http://drupal.stackexchange.com/users/47340 "Rep: 1"), on `drupal.stackexchange.com`.""",
    """[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Manually reported question: [Your Mind Cans Reinforce](//superuser.com/questions/944613) by [Carmen M Snyder](//superuser.com/users/472807/carmen-m-snyder) on `superuser.com` """,
    """[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in body, bad keyword in title: [Boost Your Brain Power Quickly](//superuser.com/questions/944622) by [david cohen](//superuser.com/users/472811/david-cohen) on `superuser.com` """,
    """[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Manually reported answer: [TOR browser delete history securely](//askubuntu.com/a/652043) by [Roger Stellon](//askubuntu.com/users/432716/roger-stellon) on `askubuntu.com` """,
    """[tag:cv-pls] too broad [How to get Jordan Moore's Top Drawer to work with plain JavaScript instead of jquery?](http://stackoverflow.com/q/32030230/4639281) - [nick_burns](http://stackoverflow.com/users/5231242/nick-burns) 1 min ago """
]

room_base_message = "from [%s](http://chat.%s/rooms/%s/)" % ('TESTING!', "TESTING.NONE", 89)
REASON_CLEAN_REGEX = '^[tag:][.!,;:\-()]'


for content in test_strings:
    for p in patterns:
        try:
            matches = re.compile(p['regex'], re.IGNORECASE).match(content)
        except:
            print "ERROR!", p['regex']
        if matches:
            message = u"**%s** for %s" % (p['translation'], matches.group(4))
            reason_msg = ""
            if matches.group(2) or matches.group(3):
                if matches.group(3):
                    if matches.group(3).strip() not in ("(","-",":"):
                        reason_msg += u" %s " % (re.sub(REASON_CLEAN_REGEX,"",matches.group(3)))
                if matches.group(2):
                    reason_msg += u" %s " % (re.sub(REASON_CLEAN_REGEX,"",matches.group(2)))
            if reason_msg:
                message += u" Reason: {}".format(reason_msg)
            print message
#            thr = threading.Thread(target=utils.save_post, args=(matches.group(4), 'meta.stackexchange.com', 89, p['translation']))
#            thr.start()
