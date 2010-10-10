#!/usr/bin/env python

"""
index.py

Handle web requests to the blag and display blog posts and comments.
"""

import functools
import optparse
from os import path

import cherrypy
from mako import lookup

import db

TEMPLATE_PATH = path.abspath("./templates/")
DEFAULT_LOOKUP = lookup.TemplateLookup(directories=[TEMPLATE_PATH],
                                       module_directory=path.abspath('.'))

class ErrorMessageException(Exception):
    def __init__(self, msg):
        super(Exception,self).__init__()
        self.msg = msg

def error(s):
    raise ErrorMessageException(s)

def render_with(template_name):
    if '.' not in template_name:
        template_name += ".html"
    def render_with_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                tmpl_kwargs = fn(*args, **kwargs)
            except ErrorMessageException, exn:
                t = DEFAULT_LOOKUP.get_template("error.html")
                return t.render(msg=exn.msg, page_title="Error")
            t = DEFAULT_LOOKUP.get_template(template_name)
            return t.render(**tmpl_kwargs)
        return wrapper
    return render_with_decorator

class BlagController(object):
    def __init_(self):
        pass
    @cherrypy.expose
    @render_with("index")
    def index(self):
        posts = [dereference_author(p) for p in db.get_posts()]
        return {"posts":posts, "page_title": "Home"}
    @cherrypy.expose
    @render_with("entry")
    def entry(self, postid):
        post = dereference_author(db.get_post(postid))
        return {"page_title": post["title"], "post": post}
    @cherrypy.expose
    @render_with("add_post")
    def add_post(self, body=None, title=None, submit=None):
        author = get_author()
        if author is None:
            error("You are not logged in.")
        if cherrypy.request.method.lower() == "get":
            return {"page_title":"Create Post"}
        post_id = int(db.add_post(author["id"], title, body))
        raise cherrypy.HTTPRedirect("/entry/%d" % post_id)
    @cherrypy.expose
    @render_with("login")
    def login(self, author_name=None, password=None, submit=None):
        failed = False
        if cherrypy.request.method.lower() == "post":
            author = login_author(author_name, password)
            if author:
                raise cherrypy.HTTPRedirect("/")
            else:
                failed = True
        return {"page_title":"Login", "failed":failed}        
        

def dereference_author(post):
    d = dict(post)
    d["author"] = db.get_author(post["author_id"])
    return d
        
def get_author():
    cookie = cherrypy.request.cookie
    session_token = cookie.get("session_token")
    author_id = cookie.get("author_id")
    if session_token is None or author_id is None:
        return None
    print "aid,tok:",int(author_id.value), session_token.value
    author = db.check_session(int(author_id.value),session_token.value)
    if author is not None:
        return author
    return None

def login_author(author_name,pwd):
    token = db.login(author_name,pwd)
    if token is not False:
        author = db.get_author(author_name)
        cherrypy.response.cookie["session_token"] = token
        cherrypy.response.cookie["author_id"] = author["id"]
        return author
    return False


def get_dummy_posts():
    return ({"title":"Why HCS is amazing.", "date":"now", "author": {"name":"jhoon"},
             "id":"1", "body": "We are the <b>best</b>!"},
            {"title":"Windows sucks.", "date":"Since the 90's", "author": {"name":"linus"},
             "id":"2", "body": "And what's more, it smells."},)

def main(argv):
    parser = optparse.OptionParser()
    parser.add_option("-H", "--hostname", dest="hostname", default="alberge.org",
                      help="Hostname on which cherrypy will listen.")
    parser.add_option("-p", "--port", dest="port", default=8000,
                      help="Port on which cherrypy will listen.")
    opts,args = parser.parse_args(argv)
    conf = {"/": {"tools.staticdir.root": path.abspath(".")},
            "/static": {"tools.staticdir.on": True,
                        "tools.staticdir.dir": "static",},}
    cherrypy.config.update({"server.socket_host": opts.hostname,
                            "server.socket_port": opts.port,})
    cherrypy.quickstart(BlagController(), config=conf)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
