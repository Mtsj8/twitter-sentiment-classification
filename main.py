import sys
import search_tweet

if __name__ == "__main__":
    query = sys.argv[1]
    lang = sys.argv[2]

    full_query = f"\"{query}\" lang:{lang}"
    search_tweet.search(full_query, 'tweets_%s' % (query))
