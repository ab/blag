#!/usr/bin/env python

"""Reset the database of the blag app."""

import sys
import db

def reset():
    db.clear_posts(0)
    db.clear_comments(0)

def hard_reset():
    db.drop_tables(verbose=True)
    db.create_dbs()
    db.add_author('dude', 'dude')
    db.add_author('guy', 'guy')
    db.add_post(1, 'Hello!', 'The quick brown fox jumps over the lazy dog.')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'hard':
            hard_reset()
        else:
            print 'reset.py [hard]'
    else:
        print 'Clearing all posts and comments.'
        reset()

