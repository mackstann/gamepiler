import os, ConfigParser, urllib2, time, httplib2

try:
    import cPickle as pickle
except ImportError:
    import pickle

config = ConfigParser.SafeConfigParser()
config.read('scrape-parameters.conf')

class FetchFailure(Exception):
    pass

class SimpleFetcher(object):

    def __init__(self, url):
        self.url = url

    def fetch_pages(self):
        yield self.fetch_url(self.url)

    def fetch_url(self, url):
        http = httplib2.Http(cache='http-cache')
        response, content = http.request(url, headers={'User-Agent': 'gamepiler/1.0'})
        if response.status >= 400:
            raise FetchFailure("HTTP %d" % response.status)
        return content

class PatternFetcher(SimpleFetcher):
    def __init__(self, url_pattern, pattern_values):
        self.url_pattern = url_pattern
        self.pattern_values = pattern_values

    def fetch_pages(self):
        for val in self.pattern_values:
            url = self.url_pattern.replace('$', val)
            yield self.fetch_url(url)

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

cache = Cache()

for section in config.sections():
    print section,

    if config.has_option(section, 'url'):
        print config.get(section, 'url')
        fetcher = SimpleFetcher(config.get(section, 'url'))
    elif config.has_option(section, 'url_pattern'):
        print config.get(section, 'url_pattern')

        if config.has_option(section, 'pattern_values'):
            values = config.get(section, 'pattern_values').split()
        else:
            values = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['0-9']

        fetcher = PatternFetcher(config.get(section, 'url_pattern'), values)

    pages = []
    fetch = fetcher.fetch_pages()
    while True:
        try:
            pages.append(fetch.next())
        except FetchFailure, ex:
            print ex
        except StopIteration:
            break
        time.sleep(3)

    cache.put(section, pages)

