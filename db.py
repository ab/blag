#!/usr/bin/env python

"""
HCS Blag

Database interaction code.
"""

import MySQLdb
import MySQLdb.cursors
import random

DEBUG = True

DB_HOST = 'localhost'
DB_USER = 'hcs_blag'
DB_PASS = 'SVBUm8Px3CGn8c29'
DB_DB = 'hcs_blag'
db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_DB)
c = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

class DoesNotExist(Exception):
    pass

def get_cursor():
    return db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

def gen_token(length):
     s = ''.join(chr(random.randrange(32,126)) for x in range(length))
     s = s.replace("'", '_')
     s = s.replace("\\", '_')
     return s

def create_dbs():
    q = """ CREATE TABLE IF NOT EXISTS `posts` (
        `id` INT NOT NULL AUTO_INCREMENT ,
        `author_id` INT NOT NULL ,
        `date` DATETIME NOT NULL ,
        `title` VARCHAR( 255 ) NOT NULL ,
        `body` TEXT NOT NULL ,
        PRIMARY KEY ( `id` ) ,
        INDEX ( `author_id` , `date` )
    ) ENGINE = MYISAM """
    c.execute(q)

    q = """ CREATE TABLE IF NOT EXISTS `comments` (
        `id` INT NOT NULL AUTO_INCREMENT ,
        `post_id` INT NOT NULL ,
        `name` VARCHAR( 255 ) NOT NULL ,
        `date` DATETIME NOT NULL ,
        `title` VARCHAR( 255 ) NOT NULL ,
        `body` TEXT NOT NULL ,
        PRIMARY KEY ( `id` ) ,
        INDEX ( `post_id` , `date` )
    ) ENGINE = MYISAM """
    c.execute(q)

    q = """ CREATE TABLE IF NOT EXISTS `authors` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `name` VARCHAR(255) NOT NULL,
        `pass` CHAR(40) CHARACTER SET ascii COLLATE ascii_general_ci NOT NULL,
        `updated` DATETIME NOT NULL ,
        `session` CHAR(20) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
        PRIMARY KEY ( `id` ),
        UNIQUE ( `name`)
    ) ENGINE = MYISAM """
    c.execute(q)

    return True

def drop_tables(verbose=False):
    for table in ['posts', 'comments', 'authors']:
        if verbose:  print "DROP TABLE IF EXISTS %s;" % table
        c.execute("DROP TABLE IF EXISTS %s" % table)

def add_post(author_id, title, body):
    q = """insert into posts (`author_id`, `title`, `body`, `date`)
                VALUES ('%s', '%s', '%s', UTC_TIMESTAMP())"""
    c.execute(q % (author_id, title, body))
    if DEBUG:
        print "New Post(%r, %r, %r)" % (author_id, title, body)
    return c.lastrowid

def get_posts(author_id=None):
    if author_id is not None:
        q = "select * from posts where `id`='%s'"
        c.execute(q % author_id)
    else:
        q = "select * from posts"
        c.execute(q)
    return c.fetchall()

def get_post(post_id):
    rows = c.execute("select * from posts where `id`=%s" % post_id)
    if not rows:
        raise DoesNotExist
    return c.fetchone()

def add_author(name, passwd):
    q = """insert into authors (`name`, `pass`, `updated`, `session`)
              VALUES ('%s', SHA1('%s'), UTC_TIMESTAMP(), '%s')"""
    token = gen_token(20)
    if DEBUG:
        print "New Author(%r)" % name
    c.execute(q % (name, passwd, token))

def get_author(user):
    """Get a single author record by name or id."""
    if isinstance(user, (int, long)):
        user_id = int(user)
        by_name = False
    else:
        by_name = True

    if by_name:
        c.execute("select * from `authors` where `name`='%s'" % user)
    else:
        c.execute("select * from `authors` where `id`=%s" % user_id)

    return c.fetchone()

def add_comment(post_id, name, title, body):
    q = """insert into `comments` (`post_id`, `name`, `title`, `body`, `date`)
                VALUES ('%s', '%s', '%s', '%s', UTC_TIMESTAMP())"""
    if DEBUG:
        print "New Comment(%r, %r, %r, %r)" % (post_id, name, title, body)
    c.execute(q % (post_id, name, title, body))

def del_comment(comment_id):
    return c.execute("delete from `comments` where `id`=%s" % comment_id)

def get_comments(post_id):
    q = "select * from `comments` where `post_id`='%s'"
    c.execute(q % post_id)
    return c.fetchall()

def get_comment(comment_id):
    rows = c.execute("select * from `comments` where `id`=%s" % comment_id)
    if not rows:
        raise DoesNotExist
    return c.fetchone()

def login(user, password):
    """Check user password against database. Return session token on success."""

    q = """select * from `authors` where `name`='%s' and `pass`=SHA1('%s')"""
    rows = c.execute(q % (user, password))
    if rows > 1:
        raise "Error: query returned more than one row!"

    if rows == 0:
        return False

    token = gen_token(20)
    q = "update `authors` set `session`='%s' where `name`='%s'"
    c.execute(q % (token, user))
    return token

def check_session(user_id, token):
    """Check that token represents a valid session for specified user."""

    q = "select * from `authors` where `id`=%s and `session`='%s'"
    rows = c.execute(q % (user_id, token))
    if rows != 1:
        return None
    return c.fetchone()

def clear_posts(min_index):
    q = "delete from `posts` where `id` >= %s"
    rows = c.execute(q % min_index)
    return not not rows

def clear_comments(min_index):
    q = "delete from `posts` where `id` >= %s"
    rows = c.execute(q % min_index)
    return not not rows

