import unittest
import json
import re

# Performing some dynamic test generation inspired by:
# http://stackoverflow.com/a/20870875/189134
# Each item in the "test_strings" variable has this format:
#    [ test name, string to test, expected value ]

with open('patterns.txt', 'r') as f:
    patterns = json.load(f)

test_strings = [
    [
        "tag_with_reason_in_tag",
        """[tag:cv-pls-too-broad-offsite-resource-unclear-whatever] http://stackoverflow.com/questions/25959443/how-do-i-create-a-hierarchical-state-machine-using-c-sharp""",
        """**Close Vote Request** for http://stackoverflow.com/questions/25959443/how-do-i-create-a-hierarchical-state-machine-using-c-sharp Reason:  -too-broad-offsite-resource-unclear-whatever"""
    ],
    [
        "tag_with_reason_ignored",
        """[tag:cv-plz] http://stackoverflow.com/questions/3272285/dns-issue-www-example-not-working-but-example-com-does (very old question, off-topic) """,
        """**Close Vote Request** for http://stackoverflow.com/questions/3272285/dns-issue-www-example-not-working-but-example-com-does"""
    ],
    [
        "not_an_answer",
        "naa - http://stackoverflow.com/a/25905260/2982225 ",
        """**Flag Request -> Not an answer** for http://stackoverflow.com/a/25905260/2982225""",
    ],
    [
        "invalid_format",
        "naa finished @DroidDev ",
        None
    ],
    [
        "with_reason_ignore_end_reason",
        "[tag:cv-pls] no-repro http://stackoverflow.com/q/18114801/3622940 see op answer ",
        """**Close Vote Request** for http://stackoverflow.com/q/18114801/3622940 Reason:  no-repro""",
    ],
    [
        "blaze_format",
        "\[[Blaze](https://github.com/Charcoal-SE/Blaze)] answer flagged by Undo: http://stackoverflow.com/a/26389222",
        """**Flag Request** for http://stackoverflow.com/a/26389222""",
    ],
    [
        "with_colon_after_type",
        "[tag:cv-pls]: http://meta.stackexchange.com/questions/242741/i-have-two-emacs-buffers-in-a-frame-a-cc-b-cc",
        """**Close Vote Request** for http://meta.stackexchange.com/questions/242741/i-have-two-emacs-buffers-in-a-frame-a-cc-b-cc""",
    ],
    [
        "long_reason",
        "cv-pls last recommendation for a bit http://stackoverflow.com/q/26357391/189134",
        """**Close Vote Request** for http://stackoverflow.com/q/26357391/189134 Reason:  last recommendation for a bit""",
    ],
    [
        "colon_in_reason",
        "[tag:cv-pls] too broad: http://stackoverflow.com/questions/26734497/convert-bytes-array-to-video",
        """**Close Vote Request** for http://stackoverflow.com/questions/26734497/convert-bytes-array-to-video Reason:  too broad:""",
    ],
    [
        "close_without_tag_prefix",
        "cv-pls recommendation http://stackoverflow.com/q/2168701/189134 ",
        """**Close Vote Request** for http://stackoverflow.com/q/2168701/189134 Reason:  recommendation""",
    ],
    [
        "asterisk_in_reason",
        "[tag:nuke-pls] *shudder* http://stackoverflow.com/questions/1543107",
        """**Close/Delete Request** for http://stackoverflow.com/questions/1543107 Reason:  *shudder*""",
    ],
    [
        "smoke_detector_format_single_reason",
        "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in title: [1 866 978 6819 gmail account recovery contact number 1 866 978 6819 gmail account recovery phone number](http://stackoverflow.com/questions/27363275/1-866-978-6819-gmail-account-recovery-contact-number-1-866-978-6819-gmail-accoun) by [ab cl](http://stackoverflow.com/users/4338254/ab-cl) on `stackoverflow.com` ",
        """**Spam Flag Request** for http://stackoverflow.com/questions/27363275/1-866-978-6819-gmail-account-recovery-contact-number-1-866-978-6819-gmail-accoun Reason:  Bad keyword in title""",
    ],
    [
        "smoke_detector_format_multiple_reason",
        "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in title, Phone number detected: [support for yahoo mail 18669786819 @call for helpline number](http://stackoverflow.com/questions/27385010/support-for-yahoo-mail-18669786819-call-for-helpline-number) by [jas rat](http://stackoverflow.com/users/4330380/jas-rat) on `stackoverflow.com` ",
        """**Spam Flag Request** for http://stackoverflow.com/questions/27385010/support-for-yahoo-mail-18669786819-call-for-helpline-number Reason:  Bad keyword in title""",
    ],
    [
        "tag_as_reason",
        "[tag:Cv-pls] [tag:wtf] http://stackoverflow.com/questions/27381564/how-to-write-an-screen-driver-in-nasm ",
        """**Close Vote Request** for http://stackoverflow.com/questions/27381564/how-to-write-an-screen-driver-in-nasm Reason:  [tag:wtf]"""
    ],
    [
        "invalid_format_tag_and_reason",
        "[tag:cv-pls] [tag:toolrecommendation] cv-pls http://stackoverflow.com/q/27385198/1234256 ",
        None
    ],
    [
        "reason_at_end_with_tag",
        "[tag:cv-pls] [tag:too-broad] http://stackoverflow.com/q/27385313/1234256 It's [tag:too-broad] ",
        """**Close Vote Request** for http://stackoverflow.com/q/27385313/1234256 Reason:  [tag:too-broad]""",
    ],
    [
        "smoke_detector_multiple_reason_2",
        "[ [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) ] Bad keyword in title, Bad keyword in username, Phone number detected: [Inter Caste +917689070805 @ LoVe marriagE SpEcialiSt baba Ji](http://askubuntu.com/questions/560666/inter-caste-917689070805-love-marriage-specialist-baba-ji) by [babaji](http://askubuntu.com/users/358135/babaji) on `askubuntu.com` ",
        """**Spam Flag Request** for http://askubuntu.com/questions/560666/inter-caste-917689070805-love-marriage-specialist-baba-ji Reason:  Bad keyword in"""
    ],
    [
        "reason_ignored",
        "[tag:cv-plz] http://stackoverflow.com/questions/27669972/folder-structure-of-a-smacss-project-where-to-put-class (opinionated)",
        """**Close Vote Request** for http://stackoverflow.com/questions/27669972/folder-structure-of-a-smacss-project-where-to-put-class""",
    ],
    [
        "cv_pls_user_script",
        """[tag:cv-pls] too broad [How to get Jordan Moore's Top Drawer to work with plain JavaScript instead of jquery?](http://stackoverflow.com/q/32030230/4639281) - [nick_burns](http://stackoverflow.com/users/5231242/nick-burns) 1 min ago """,
        """**Close Vote Request** for http://stackoverflow.com/q/32030230/4639281 Reason:  too broad"""
    ],
    [
        "cv_pls_user_script_markdown_reason",
        """[tag:cv-pls] [duplicate](http://programmers.stackexchange.com/q/59344/88986) [How to get Jordan Moore's Top Drawer to work with plain JavaScript instead of jquery?](http://stackoverflow.com/q/32030230/4639281) - [nick_burns](http://stackoverflow.com/users/5231242/nick-burns) 1 min ago """,
        """**Close Vote Request** for http://stackoverflow.com/q/32030230/4639281"""
    ]

]


def check_string(content):
    REASON_CLEAN_REGEX = '^[tag:][.!,;:\-()]'
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
                    if matches.group(3).strip() not in ("(", "-", ":"):
                        reason_msg += u" %s " % (re.sub(REASON_CLEAN_REGEX, "", matches.group(3)))
                if matches.group(2):
                    reason_msg += u" %s " % (re.sub(REASON_CLEAN_REGEX, "", matches.group(2)))
            if reason_msg:
                message += u" Reason: {}".format(reason_msg)
            return message.strip()


class TestSequenceMeta(type):
    def __new__(mcs, name, bases, dict):
        def gen_test(a, b):
            def test(self):
                self.assertEqual(check_string(a), b)

            return test

        for tname, a, b in test_strings:
            test_name = "test_%s" % tname
            dict[test_name] = gen_test(a, b)
        return type.__new__(mcs, name, bases, dict)


class TestSequence(unittest.TestCase):
    __metaclass__ = TestSequenceMeta


if __name__ == '__main__':
    unittest.main()
