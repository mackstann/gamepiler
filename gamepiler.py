import os, httplib2

try:
    import cPickle as pickle
except ImportError:
    import pickle

class FetchFailure(Exception):
    pass

class Fetcher(object):
    def __init__(self, urls):
        self.urls = urls

    def fetch_pages(self):
        http = httplib2.Http(cache='http-cache')
        for url in self.urls:
            response, content = http.request(url, headers={'User-Agent': 'gamepiler/1.0'})
            if response.status >= 400:
                raise FetchFailure("HTTP %d" % response.status)
            yield content

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

