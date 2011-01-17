#!/usr/bin/env python

"""Reset the database of the blag app."""

import sys
import db

fixtures = """
INSERT INTO `authors` VALUES (NULL, 'dude', SHA1('dude'), UTC_TIMESTAMP(), '');
INSERT INTO `authors` VALUES (NULL, 'guy', SHA1('guy'), UTC_TIMESTAMP(), '');
"""


def reset():
    db.clear_posts(0)
    db.clear_comments(0)

def hard_reset():
    db.drop_tables(verbose=True)
    db.create_dbs()
    for line in fixtures.split('\n'):
        if not line:
            continue
        print line
        db.c.execute(line)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'hard':
            hard_reset()
        else:
            print 'reset.py [hard]'
    else:
        print 'Clearing all posts and comments.'
        reset()

