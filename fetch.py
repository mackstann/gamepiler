import gamepiler, time

config = gamepiler.Config('scrape-parameters.conf')
cache = gamepiler.Cache()

for game in config.game_ids():
    print
    print game
    print

    urls = config.urls_for_game(game)

    pages = []
    for url in urls:
        print url
        try:
            pages.append(gamepiler.fetch(url))
        except gamepiler.FetchFailure, ex:
            print ex
        time.sleep(5)

    cache.put(game, pages)

