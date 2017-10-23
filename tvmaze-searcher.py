# -*- coding: utf-8 -*-
import json, urllib.request, sys, re, argparse

# Check if string is an IMDB-id
def is_imdb(string):
    re_imdb = re.compile("^tt\d{1,}")
    return True if re_imdb.search(string) else False

#Check that string is valid year
def valid_year(string):
    if string == None:
        return False
    re_year = re.compile("^[1-2]\d{3}$")
    return True if (re_year.search(string) or string != None) else False

class Show:
    def __init__(self, json_data):
        self.title = json_data['name']
        self.year = json_data['premiered']
        self.imdb_id = json_data["externals"]["imdb"]
        self.imdb_rating = json_data["rating"]["average"]
        self.genre = ""
        for genre in json_data["genres"]:
            self.genre += genre + ", "
        self.genre = self.genre[:-2]
        #self.actors = json_data["Actors"]
        self.runtime = json_data["runtime"]
        self.country = json_data["network"]["country"]["name"]
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
        self.release_date = json_data['airdate']
    def to_string(self):
        print("S" + "%02d" % self.season_number + "E" + \
            "%02d" % self.episode_number + ": " + self.title + \
            " (" + self.release_date + ")")


site = " http://api.tvmaze.com"     #/lookup/shows?imdb=
                                    #/singlesearch/shows?q=

parser = argparse.ArgumentParser(description='TVMaze search')
parser.add_argument('query', type=str, help='Search query')
parser.add_argument('-season', dest='season', help='Season')
parser.add_argument('-episode', dest='episode', help='Episode')
parser.add_argument('-output', dest='output', \
    help='Output: full, full_noep, imdb, title, year, runtime, actors,' \
    'genre, episode_list, episode_count') # -o works'
args = parser.parse_args()

# Build search url
search_string_url = site
if is_imdb(args.query):
    search_string_url += "/lookup/shows?imdb=" + args.query
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
show.to_string()
show.list_episodes()

# Output

#print(json_data[args.output])
