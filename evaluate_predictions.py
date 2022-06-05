import os
import json
from collections import defaultdict

from tqdm import tqdm
from cdlib import algorithms, classes, evaluation, readwrite

with open("dataset/custom_communities.json", "r", encoding="utf-8") as f:
    custom_communities = json.load(f)

ratio_of_genres_in_com = {}

results_dir = os.path.join(os.getcwd(),"results")
results = [i for i in os.listdir(results_dir) if i.endswith(".csv")]

# delež odkritega žanra
# delež žanrov v comm

for result in results:
    if "angel" in result:
        nr_of_genres_in_com = {}
        ratio_of_genres_in_com = {}
        coms = readwrite.read_community_csv(os.path.join(results_dir,result), ",", str)
        print(result)
        print("Detected {} communities:".format(len([len(c) for c in sorted(coms.communities, key=len)])))
        print("Largest 10 communities: ", [len(c) for c in sorted(coms.communities, key=len, reverse=True)][:10])
        print("Smallest 10 communities: ", [len(c) for c in sorted(coms.communities, key=len, reverse=False)][:10])

        sorted(custom_communities["tracks"].values(), key=len, reverse=True)
        for j, det_com in enumerate([c for c in coms.communities if len(c) >= 5]):
            nr_of_genres_in_com[j] = defaultdict(int)
            for i in tqdm(det_com):
                for custom_com, ids in custom_communities["tracks"].items():
                    if i in ids:
                        nr_of_genres_in_com[j][custom_com] += 1

            ratio_of_genres_in_com[j] = defaultdict(int)
            for cc, n in nr_of_genres_in_com[j].items():
                #ratio_of_genres_in_com[j][cc].append(nr_of_genres_in_com[j][cc])
                ratio_of_genres_in_com[j][cc] = round(nr_of_genres_in_com[j][cc]/sum(nr_of_genres_in_com[j].values()),2)
                

            ratio_of_genres_in_com[j] = dict(sorted(ratio_of_genres_in_com[j].items(), key=lambda item: item[1], reverse=True))

        out_file = open("results/{}.json".format(result.split(".")[0]), "w", encoding='utf-8')
        json.dump(ratio_of_genres_in_com, out_file, indent = 4)