import ConfigParser, gamepiler, time

config = ConfigParser.SafeConfigParser()
config.read('scrape-parameters.conf')

cache = gamepiler.Cache()

for section in config.sections():
    print
    print section
    print

    if config.has_option(section, 'url'):
        urls = [config.get(section, 'url')]

    elif config.has_option(section, 'url_pattern'):
        urlpat = config.get(section, 'url_pattern')

        if config.has_option(section, 'pattern_values'):
            values = config.get(section, 'pattern_values').split()
        else:
            values = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + ['0-9']

        urls = [ urlpat.replace('$', val) for val in values ]

    fetcher = gamepiler.Fetcher(urls)

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

