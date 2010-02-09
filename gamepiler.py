import os, httplib2, ConfigParser

try:
    import cPickle as pickle
except ImportError:
    import pickle

class ConfigError(Exception):
    pass

class Config(object):
    def __init__(self, filename):
        self.filename = filename
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(filename)

    def game_ids(self):
        return self.config.sections()

    def urls_for_game(self, game_id):
        config = self.config

        if config.has_option(game_id, 'url'):
            return [config.get(game_id, 'url')]

        if config.has_option(game_id, 'url_pattern'):
            urlpat = config.get(game_id, 'url_pattern')

            if config.has_option(game_id, 'pattern_values'):
                values = config.get(game_id, 'pattern_values').split()
            else:
                values = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['0-9']

            return [ urlpat.replace('$', val) for val in values ]

        raise ConfigError("section needs either a 'url' or 'url_pattern' setting")

class FetchFailure(Exception):
    pass

def fetch(url):
    http = httplib2.Http(cache='http-cache')
    response, content = http.request(url, headers={'User-Agent': 'gamepiler/1.0'})
    if response.status >= 400:
        raise FetchFailure("HTTP %d" % response.status)
    return content

class Cache(object):
    """
    A cache that stores a list of files, with each file being possibly broken
    up into named chunks.
    """
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        try:
            os.mkdir(cache_dir)
        except OSError:
            pass

    def construct_path(self, name):
        return os.path.join(self.cache_dir, name)

    def put(self, name, chunks):
        f = open(self.construct_path(name), 'w')
        pickle.dump(chunks, f)
        f.close()

    def get(self, name):
        f = open(self.construct_path(name), 'r')
        chunks = pickle.load(f)
        f.close()
        return chunks

