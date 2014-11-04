import json

patterns = [
    {
        'regex': "^((?:\[)?cv-pl[sz].*?(?:\])?|\[tag:cv-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Close Vote Request"
    },
    {
        'regex': "^((?:\[)?close-pl[sz].*?(?:\])?|\[tag:close-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Close Vote Request"
    },
    {
        'regex': "^((?:\[)?dv-pl[sz].*?(?:\])?|\[tag:dv-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Delete Vote Request"
    },
    {
        'regex': "^((?:\[)?delv-pl[sz].*?(?:\])?|\[tag:delv-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Delete Vote Request"
    },
    {
        'regex': "^((?:\[)?undelv-pl[sz].*?(?:\])?|\[tag:undelv-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Undelete Vote Request"
    },
    {
        'regex': "^((?:\[)?undv-pl[sz].*?(?:\])?|\[tag:undv-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Undelete Vote Request"
    },
    {
        'regex': "^((?:\[)?ro-pl[sz].*?(?:\])?|\[tag:ro-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Reopen Vote Request"
    },
    {
        'regex': "^((?:\[)?rov-pl[sz].*?(?:\])?|\[tag:rov-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Reopen Vote Request"
    },
    {
        'regex': "^((?:\[)?reopen-pl[sz].*?(?:\])?|\[tag:reopen-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Reopen Vote Request"
    },
    {
        'regex': "^((?:\[)?reject-pl[sz].*?(?:\])?|\[tag:reject-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Review Reject Request"
    },
    {
        'regex': "^((?:\[)?review-pl[sz].*?(?:\])?|\[tag:review-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Review Request"
    },
    {
        'regex': "^((?:\[)?rv-pl[sz].*?(?:\])?|\[tag:rv-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Review Request"
    },
    {
        'regex': "^((?:\[)?nuke-pl[sz].*?(?:\])?|\[tag:nuke-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Close/Delete Request"
    },
    {
        'regex': "^((?:\[)?flag-pl[sz].*?(?:\])?|\[tag:flag-pl[sz](-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Flag Request"
    },
    {
        'regex': "^((?:\[)?spam.*?(?:\])?|\[tag:spam(-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Spam Flag Request"
    },
    {
        'regex': "^((?:\[)?flag-naa.*?(?:\])?|\[tag:flag-naa(-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Flag Request -> Not an answer"
    },
    {
        'regex': "^((?:\[)?link-only.*?(?:\])?|\[tag:link-only(-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Flag Request -> Link Only"
    },
    {
        'regex': "^((?:\[)?naa.*?(?:\])?|\[tag:naa(-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Flag Request -> Not an answer"
    },
    {
        'regex': "^((?:\[)?vlq.*?(?:\])?|\[tag:vlq(-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Flag Request -> Very Low Quality"
    },
    {
        'regex': r"^(\\\[\[Blaze\]\(https://github\.com/Charcoal-SE/Blaze\)\]) (?:q(?:uestion)?|a(?:nswer)?)()() flagged by \w+: (https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Flag Request"
    },
    {
        'regex': "^((?:\[)?offensive.*?(?:\])?|\[tag:offensive(-.*)?])(?: )?((?:\[tag\:*)?[\w :\-\(\)]+(?:\])?)?(?: )?(https?://.*\.com/(?:q(?:uestions)?|a(?:nswer)?)/\d+(?:/)?(?:\d+|(?:\w|-)+)?(?:/\d+)?(?:#\d+)?)",
        'translation': "Offensive Flag Request"
    },
]

rooms = [
    {
        'site': "meta.stackexchange.com",
        'room_num': 89,
        'monitor': True,
        'post_requests': False
    },
    {
        'site': "stackoverflow.com",
        'room_num': 5,
        'monitor': True,
        'post_requests': False
    },
    {
        'site': "stackoverflow.com",
        'room_num': 11,
        'monitor': True,
        'post_requests': False
    },
    {
        'site': "stackoverflow.com",
        'room_num': 29074,
        'monitor': True,
        'post_requests': False
    },
    {
        'site': "stackoverflow.com",
        'room_num': 17,
        'monitor': True,
        'post_requests': False
    },
    {
        'site': "stackoverflow.com",
        'room_num': 6,
        'monitor': True,
        'post_requests': False
    },
	{
        'site': "stackoverflow.com",
        'room_num': 41570,
        'monitor': True,
        'post_requests': False
    },
    {
        'site': "stackexchange.com",
        'room_num': 11540,
        'monitor': True,
        'post_requests': False
    },
    {
        'site': "meta.stackexchange.com",
        'room_num': 773,
        'monitor': False,
        'post_requests': True
    },
]


with open('patterns.txt', 'w') as fout:
    json.dump(patterns, fout, indent=4)

with open('rooms.txt', 'w') as fout:
    json.dump(rooms, fout, indent=4)

room_read = []
patterns_read = []

with open('patterns.txt', 'r') as f:
    patterns_read = json.load(f)

with open('rooms.txt', 'r') as f:
    rooms_read = json.load(f)

assert(patterns == patterns_read)
assert(rooms == rooms_read)
