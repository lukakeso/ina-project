import json
from tqdm import tqdm
      
with open("dataset/selected_phrases.json", "r", encoding="utf-8") as f:
    phrase_dict = json.load(f)

with open("dataset/collections.json", "r", encoding="utf-8") as f:
    collections = json.load(f)

    # "type": "playlist",
    # "name": "Leto Ninho Maes Jul Zkr 🐐🐐🐐🐐🐐",
    # "num_tracks": 42,
    # "description": "",
    # "ztracks": [

custom_communities_w_track_ids = {}
for community_name, phrases in phrase_dict.items():
    custom_communities_w_track_ids[community_name] = []

custom_communities_w_col_ids = {}
for community_name, phrases in phrase_dict.items():
    custom_communities_w_col_ids[community_name] = []

def strip_string(s):
    s_ = s.lower().replace("(","").replace(")","").replace("{","").replace("}","")\
                  .replace("[","").replace("]","").replace("!","").replace("?","")\
                  .replace("(","").replace(")","").replace(",","").replace(".","")\
                  .replace(">","").replace("<","").replace(";","").replace(":","")\
                  .replace("&","").replace("%","").replace("/","").replace("\\","")\
                  .replace("$","").replace("|","").split()
    return s_

for playlist_id, info in tqdm(collections.items()):
    if "playlist" in info["type"] and info["num_tracks"] >= 5:
        for community_name, phrases in phrase_dict.items():
            next_comm = False
            for phrase in phrases:
                if phrase in strip_string(info["description"]) or phrase in strip_string(info["name"]):
                    custom_communities_w_track_ids[community_name] += info["ztracks"]
                    custom_communities_w_col_ids[community_name].append(playlist_id)
                    next_comm = True
                    break
            if next_comm:
                break
            
print("\nTracks:")
count = 0
duplicates = []
for comm, ids in custom_communities_w_track_ids.items():
    custom_communities_w_track_ids[comm] = list(set(ids))
    print("{}: {}".format(comm,len(custom_communities_w_track_ids[comm])))
for v in custom_communities_w_track_ids.values():
    duplicates += v
print("Total tracks w duplicates:", len(duplicates))
print("Total tracks w/o duplicates:", len(set(duplicates)))

print("\nPlaylists:")
count = 0
duplicates = []
for comm, ids in custom_communities_w_col_ids.items():
    custom_communities_w_col_ids[comm] = list(set(ids))
    print("{}: {}".format(comm,len(custom_communities_w_col_ids[comm])))
for v in custom_communities_w_col_ids.values():
    duplicates += v
print("Total playlists w duplicates:", len(duplicates))
print("Total playlists w/o duplicates:", len(set(duplicates)))


with open("dataset/custom_communities.json", "w", encoding="utf-8") as f:
    json.dump(dict(tracks=custom_communities_w_track_ids,
                   collections=custom_communities_w_col_ids), \
                    f, ensure_ascii=False, indent=4)            