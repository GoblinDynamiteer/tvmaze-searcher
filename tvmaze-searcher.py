# -*- coding: utf-8 -*-
import json, urllib.request, sys, re, argparse
from datetime import datetime

# Check if string is an IMDB-id
def is_imdb(string):
    re_imdb = re.compile("^tt\d{1,}")
    return True if re_imdb.search(string) else False

# Check if string is an IMDB-id
def possible_maze_id(string):
    re_imdb = re.compile("^\d{1,}")
    return True if re_imdb.search(string) else False

# Convert datetime to string date (eg 2012-11-02)
def get_date_as_string(date):
    try:
        return str(date.year) + "-" + \
        str("%02d" % date.month) + "-" + \
        str("%02d" % date.day)
    except:
        return "N/A" # Could not stringify datetime

class Show:
    def __init__(self, json_data):
        self.last_aired_date = "None Aired"
        self.last_aired = "None Aired"
        self.title = json_data['name']
        self.year = json_data['premiered']
        self.status = json_data['status']
        self.imdb_id = json_data["externals"]["imdb"]
        self.imdb_rating = json_data["rating"]["average"]
        self.genre = ""
        for genre in json_data["genres"]:
            self.genre += genre + ", "
        self.genre = self.genre[:-2]
        #self.actors = json_data["Actors"]
        self.runtime = json_data["runtime"]

        try:
            if json_data["network"] != None:
                self.country = json_data["network"]["country"]["name"]
            elif json_data["webChannel"] != None:
                self.country = json_data["webChannel"]["country"]["name"]
        except:
            self.country = "Unknown Country"

        self.tvmaze_url = json_data["_links"]["self"]["href"]
        self.episode_json_data = None

        try:
            response = urllib.request.urlopen( \
                self.tvmaze_url + "/episodes").read().decode("utf-8")
            self.episode_json_data = json.loads(response)
        except:
            print("Error: Could not get episodes!")
            sys.exit
            pass

        self.season_count = self.episode_json_data[-1]['season']
        self.episode_count = len(self.episode_json_data)
        self.episodes = None

        self.__find_episodes()

        #find last aired episode
        for i in range(0, len(self.episodes)):
            if self.episodes[i].has_aired() == 0:
                if i == 0:
                    self.last_aired_date = "None Aired"
                    self.last_aired = "None Aired"
                elif i < len(self.episodes) - 1:
                    self.last_aired_date = self.episodes[i-1].release_date
                    self.last_aired = self.episodes[i-1].to_string_se()
                break
            if i == len(self.episodes) - 1:
                self.last_aired_date = self.episodes[i].release_date
                self.last_aired = self.episodes[i].to_string_se()

    def to_string(self):
        print("Show: " + self.title + \
            (" (" + self.year +")" if self.year != None else ""))
        print(self.country)
        print(str(self.season_count) + " seasons")
        print(self.imdb_id)
        print(self.genre)
        print("Runtime: " + str(self.runtime))
        print("IMDb rating: " + str(self.imdb_rating))
        #print("Actors: " + self.actors)

    def get_episode_info(self, match_season, match_episode, data):
        for episode in self.episodes:
            if episode.episode_number == match_episode \
            and episode.season_number == match_season:
                if(hasattr(episode, data) == False) and data != "full":
                    print("Data not available for episode: " + data)
                    return
                if data == "title":
                    print(episode.title)
                elif data == "release_date":
                    print(get_date_as_string(episode.release_date))
                elif data == "tvmaze_url":
                    print(episode.tvmaze_url)
                elif data == "full":
                    episode.to_string()
                elif data == "has_aired":
                    print(episode.has_aired())
                return
        print("Episode not found")

    def list_episodes(self):
        for episode in self.episodes:
            episode.to_string()

    def get_episode_count(self):
        return self.episode_count

    def __find_episodes(self):
        self.episodes = []
        for episode_json_data in self.episode_json_data:
            self.episodes.append(Episode(episode_json_data))

class Episode:
    def __init__(self, json_data):
        self.title = json_data['name']
        self.episode_number = json_data['number']
        self.season_number = json_data['season']

        try:
            self.release_date = datetime.strptime( \
            json_data['airdate'], "%Y-%m-%d")
        except:
            self.release_date = "N/A"

        self.tvmaze_url = json_data['url']

        if self.release_date != "N/A":
            self.days_since_airdate = (datetime.now() - self.release_date).days
        else:
            self.days_since_airdate = "N/A"

    def to_string(self):
        print(show.title + " - S" + "%02d" % self.season_number + "E" + \
            "%02d" % self.episode_number + ": " + self.title + \
            " (" + get_date_as_string(self.release_date) + ")" +
            " (" + str(self.days_since_airdate) + " days ago)")

    def to_string_se(self):
        return "S" + "%02d" % self.season_number + "E" + \
            "%02d" % self.episode_number

    def has_aired(self):
        if self.days_since_airdate == "N/A":
            return "N/A"

        if self.days_since_airdate < 0:
            return 0
        else:
            return 1

site = " http://api.tvmaze.com"     #/lookup/shows?imdb=
                                    #/singlesearch/shows?q=
                                    #/shows/

parser = argparse.ArgumentParser(description='TVMaze search')
parser.add_argument('query', type = str, help='Search query, Show title'\
    ' or IMDb-id')
parser.add_argument('-season', dest = 'season', type = int, help = 'Season')
parser.add_argument('-episode', dest = 'episode', type = int, help = 'Episode')
parser.add_argument('-output', dest = 'output', \
    help = 'Output: title, release_date, full, tvmaze_url' \
    'imdb, rating, tvmaze_id, episode_count, season_count,' \
    'rating, country, genre, status, last_aired, last_aired_date, ' \
    'has_aired') # -o works'
args = parser.parse_args()

# Build search url
search_string_url = site
if is_imdb(args.query):
    search_string_url += "/lookup/shows?imdb=" + args.query
elif possible_maze_id(args.query):
    search_string_url += "/shows/" + args.query
else:
    search_string_url += "/singlesearch/shows?q=" + \
        re.sub('\s+', '+', args.query)
try:
    response = urllib.request.urlopen(search_string_url).read().decode("utf-8")
    json_data = json.loads(response)

except:
    print("Error searching for " + args.query)
    print("String Generated: " + search_string_url)
    sys.exit()

show = Show(json_data)

# Output
if args.season and args.episode:
    if args.output == None:
        show.get_episode_info(args.season, args.episode, "full")
    else:
        show.get_episode_info(args.season, args.episode, args.output)
elif args.output == "full":
    show.to_string()
    show.list_episodes()
elif args.output == "title":
    print(show.title)
elif args.output == "year":
    print(show.year)
elif args.output == "imdb":
    print(show.imdb_id)
elif args.output == "genre":
    print(show.genre)
elif args.output == "rating":
    print(show.imdb_rating)
elif args.output == "status":
    print(show.status)
elif args.output == "country":
    print(show.country)
elif args.output == "last_aired":
    print(show.last_aired)
elif args.output == "last_aired_date":
    print(get_date_as_string(show.last_aired_date))
elif args.output == "episode_count":
    print(show.episode_count)
elif args.output == "season_count":
    print(show.season_count)
elif args.output == "tvmaze_id":
    print(re.sub("http:\/\/api.tvmaze.com\/shows\/", "", show.tvmaze_url))
elif args.output == "tvmaze_url":
    print(show.tvmaze_url)
else: # Invalid or no output given, show full info w/o episode data
    show.to_string()
