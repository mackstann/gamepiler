# -*- coding: utf-8 -*-
import gamepiler, re
from lxml.html import fromstring
from cStringIO import StringIO

config = gamepiler.Config('scrape-parameters.conf')
cache = gamepiler.Cache()

class TreeExaminer(object):
    def __init__(self, tree):
        self.tree = tree
        self.examine_tables()
        self.examine_lists()
        self.examine_headings()

    def examine_headings(self):
        regex = re.compile(r'^\s*(?:0[–-]9|[a-z])\s*$', re.I)
        count = 0
        for heading_type in ('h2', 'h3'):
            for span in self.tree.cssselect("%s span.mw-headline" % heading_type):
                if regex.match(span.text_content()):
                    count += 1
        self.has_alphabetical_headings = count >= 10

    def examine_tables(self):
        sizes = []
        for table in self.tree.cssselect("div#bodyContent table.wikitable"):
            children = [ child for child in table.getchildren() if child.tag == 'tr' ]
            sizes.append(len(children))

        if sizes:
            sizes.sort()
            self.has_decent_sized_table = sizes[-1] >= 10
            self.has_lots_of_tables = len(sizes) >= 10
        else:
            self.has_decent_sized_table = False
            self.has_lots_of_tables = False

        self.one_table_is_clearly_the_biggest = False
        if len(sizes) == 1:
            self.one_table_is_clearly_the_biggest = True
        if len(sizes) >= 2:
            self.one_table_is_clearly_the_biggest = \
                sizes[-2] / float(sizes[-1]) < 0.1

    def examine_lists(self):
        sizes = []
        for table in self.tree.cssselect("div#bodyContent ul"):
            children = [ child for child in table.getchildren() if child.tag == 'li' ]
            sizes.append(len(children))

        if sizes:
            sizes.sort()
            self.has_decent_sized_list = sizes[-1] >= 10
            self.has_lots_of_lists = len(sizes) >= 10
        else:
            self.has_decent_sized_list = False
            self.has_lots_of_lists = False

        self.one_list_is_clearly_the_biggest = False
        if len(sizes) == 1:
            self.one_list_is_clearly_the_biggest = True
        if len(sizes) >= 2:
            self.one_list_is_clearly_the_biggest = \
                sizes[-2] / float(sizes[-1]) < 0.1


for game in config.game_ids():
    pages = cache.get(game)

    for page in pages:
        tree = fromstring(page)

        exam = TreeExaminer(tree)

        # big lists and tables must be carefully selected.  they may appear in
        # a section with a name like "A", "Z", "0-9", "Released games",
        # "Unreleased games", but not "References" or a few others.

        # only examine the first <a> in the <li> or <td>.  if it is
        # an external link, skip that list/table.

        # you can't really associate an <h3>/<h4> with a subsequent table/list,
        # because there may be a bit of other stuff in between them.

        # ignore: See also, External links, References, Sources.
        # ignore: lists with links like <li id="cite_note-24"><b><a href="#cite_ref-24">

        # <th> must start with Title or Game

        print game
        if exam.has_alphabetical_headings and exam.has_lots_of_tables:
            print "alphabetical tables"
        elif exam.has_alphabetical_headings and exam.has_lots_of_lists:
            print "alphabetical lists"
        elif not exam.has_alphabetical_headings and exam.has_decent_sized_table:
            print "big tables"
        elif not exam.has_alphabetical_headings and exam.has_decent_sized_list:
            print "big lists"
        else:
            print "i don't know."
            import pprint
            pprint.pprint([ (k, v) for k, v in vars(exam).items() if (not k.startswith('_') and k != 'tree') ])

