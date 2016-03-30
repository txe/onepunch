import tornado.ioloop
import tornado.web
import os
import random
from os import listdir
from os.path import isfile, join, splitext
import re


static_path = os.path.dirname(os.path.abspath(__file__))
topics_path = join(static_path, "topics")

def random_color():
    colors = ['lightgray', 'CCCCFF', '99CCCC', '66CC99'];
    random.shuffle(colors)
    return colors[0];

def get_decks():
    files = [f for f in listdir(topics_path) if isfile(join(topics_path, f)) and splitext(f)[1] == ".txt"]
    files.sort()
    items = []
    for file in files:
        prefix = ''
        prefix_color = 'red'
        name = file[:-4]
        parts = name.split(":")
        if len(parts) == 2:
          prefix = parts[0] + ":"
          name = parts[1]
          if prefix == 'text:':  prefix_color = 'green'
          if prefix == 'waste:': prefix_color = 'black'
          if prefix == 'topic:': prefix_color = 'blue'
        
        items.append({'name' : name, 'url' : 'deck/' + file, 'prefix': prefix, 'prefix_color' : prefix_color})
    return items;

def load_deck(deck_name):
    file_name = os.path.join(topics_path, deck_name)
    with open(file_name, encoding='utf8') as f:
        lines = f.readlines()

    lines = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), lines)))
    if len(lines) > 0 and lines[0] == "[associate]":
        return load_deck_type_2(lines[1:])
    else:
        return load_deck_type_1(lines)

# text with +
def load_deck_type_1(lines):
    content = []
    for line in lines:
        new_line = ""
        parts = line.split("+")
        for i in range(len(parts)):
            if i % 2 == 0:
                new_line += parts[i]
            else:
                huge = 1 if len(parts[i]) > 10 else 0
                new_line += "<input class='card' type='text' rightVal='{0}' autocomplete='off' huge='{1}' />".format(tornado.escape.xhtml_escape(parts[i]), huge)
        content.append(new_line)
    random.shuffle(content)
    return content

def random_answers(answers, others):
    while len(answers) <= 4:
        other = random.choice(others)
        if other not in answers:
            answers.append(other)
    random.shuffle(answers)
    return "".join(map(lambda x: "<span class='label label-danger'>" + x + "</span>", answers))

# text with =
def load_deck_type_2(lines):
    word_value = {}
    for line  in lines:
        parts = line.split("=");
        if (len(parts) != 2) : raise NameError('Wrong amount words')
        word_value[parts[0].strip()] = parts[1].strip()

    content = []
    keys = list(word_value.keys())
    for key, value in word_value.items():
        new_line = ""
        new_line += "<input class='card' type='text' rightVal='{0}' autocomplete='off' huge='{1}' />".format(tornado.escape.xhtml_escape(key), 1)
        new_line += "<span class='label label-info'>" + value + "</span>"
        new_line += random_answers([key], keys)
        content.append(new_line)
    random.shuffle(content)
    return content

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        items = get_decks()
        self.render("index.html", title="Decks", items=items, body_color=random_color())

class DeckHandler(tornado.web.RequestHandler):
    def get(self, deck_id):
        items = load_deck(deck_id)
        self.render("deck.html", title="Deck", items=items, body_color=random_color())

application = tornado.web.Application([
    tornado.web.url(r"/", MainHandler),
    tornado.web.url(r"/deck/(.+)", DeckHandler),
    (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
], debug=True)

if __name__ == "__main__":
    random.seed();
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
