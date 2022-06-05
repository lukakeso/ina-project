
from collections import defaultdict
from tqdm import tqdm
import json
# import nltk
# nltk.download('stopwords')
from nltk.corpus import stopwords

custom_communites = ["christmas", "religious", "children", "romance", "study", "country", "hiphop", \
                    "ambient", "rap", "latin", "workout", "jazz", "relaxing", "electronic", "rock", \
                    "instrumental", "pop"]
stop_en = set(stopwords.words('english'))
stop_es = set(stopwords.words('spanish'))
stop_de = set(stopwords.words('german'))
stop_fr = set(stopwords.words('french'))
stop_it = set(stopwords.words('italian'))
stop_pr = set(stopwords.words('portuguese'))

stop_list = [stop_en, stop_es, stop_de, stop_fr, stop_it, stop_pr]
stop_words = set().union(*stop_list)
common_words = ["best", "top", "song", "songs", "essential", "hot", "hottest", "hotest", \
                "track", "tracks", "playlist", "playlists", "music", "hit", "hits", "mix"]

with open("dataset/custom_communities.json", "r", encoding="utf-8") as f:
    custom_communities = json.load(f)

with open("dataset/collections.json", "r", encoding="utf-8") as f:
    collections = json.load(f)

for community in custom_communites:
    with open("dataset/word_cloud_{}.txt".format(community), "w", encoding="utf-8") as f:
        for info in tqdm([info for playlist_id, info in collections.items()\
                            if playlist_id in custom_communities["collections"][community]]):

            if "<a href=:" in info["description"]:
                decription = []
                for i in info["description"].split(", "):
                    decription += i.lower().split(">")[1].split("</a")[0].split()
            else:
                decription = info["description"].lower()\
                            .replace("(","").replace(")","").replace("{","").replace("}","")\
                            .replace("[","").replace("]","").replace("!","").replace("?","")\
                            .replace("(","").replace(")","").replace(",","").replace(".","")\
                            .replace("-","").replace("–","").replace(";","").replace(":","")\
                            .replace("&","").replace("%","").replace("/","").replace("\\","")\
                            .replace("$","").replace("|","").replace("#","").split()

            name = info["name"].lower()\
                            .replace("(","").replace(")","").replace("{","").replace("}","")\
                            .replace("[","").replace("]","").replace("!","").replace("?","")\
                            .replace("(","").replace(")","").replace(",","").replace(".","")\
                            .replace("-","").replace("–","").replace(";","").replace(":","")\
                            .replace("&","").replace("%","").replace("/","").replace("\\","")\
                            .replace("$","").replace("|","").replace("#","").split()
            
            
            # for word in [word for word in name + decription if word not in stop_words]:
            #     print(word)
            
            f.write('\n'.join([word for word in name + decription if word not in stop_words and word not in common_words]))



    