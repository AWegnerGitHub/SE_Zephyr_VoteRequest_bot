from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import utils.db_model
import json
import os.path

DB_NAME = "zephyr_vote_requests.db"

Base = declarative_base()
engine = create_engine('sqlite:///{}'.format(DB_NAME), convert_unicode=True, echo=False)
session = sessionmaker()
session.configure(bind=engine)

if not os.path.exists(DB_NAME):
    print "Creating tables"
    utils.db_model.create_all_tables(engine)

s = session()

with open('patterns.txt', 'r') as f:
    patterns = json.load(f)

for p in patterns:
    try:
        s.add(utils.db_model.RequestType(name=p['translation']))
        s.commit()
    except IntegrityError:
        s.rollback()


s.add(utils.db_model.PostType(id=1, name='question'))
s.add(utils.db_model.PostType(id=2, name='answer'))
try:
    s.commit()
except IntegrityError:
        s.rollback()
