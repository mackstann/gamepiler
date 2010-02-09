import ConfigParser, gamepiler, time

config = ConfigParser.SafeConfigParser()
config.read('scrape-parameters.conf')

cache = gamepiler.Cache()

for section in config.sections():
    print
    print section
    print

    if config.has_option(section, 'url'):
        url = config.get(section, 'url')
        print url
        fetcher = gamepiler.SimpleFetcher(url)

    elif config.has_option(section, 'url_pattern'):
        urlpat = config.get(section, 'url_pattern')
        print urlpat

        if config.has_option(section, 'pattern_values'):
            values = config.get(section, 'pattern_values').split()
        else:
            values = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['0-9']

        fetcher = gamepiler.PatternFetcher(urlpat, values)

    pages = []
    fetch = fetcher.fetch_pages()
    while True:
        try:
            pages.append(fetch.next())
        except gamepiler.FetchFailure, ex:
            print ex
        except StopIteration:
            break
        else:
            print "fetched a page."
        time.sleep(3)

    cache.put(section, pages)

