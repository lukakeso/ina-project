import os
from os import path
import json

import networkx as nx
from networkx.algorithms import bipartite

class SpotifyGraph():

    def __init__(self, dir, features_dir):
        
        self.base_dir = dir
        self.tracks_pth = path.join(dir, "tracks.json")
        self.col_pth = path.join(dir, "collections.json")
        self.graph_pth = path.join(dir, "graph.json")

        self.img_dir = path.join(dir, "images")
        self.clip_dir = path.join(dir, "clips")

        self.ft_dir = features_dir
        self.features_dict = {}

        self.load()


    def load(self):
        print("Loading graph...")
        with open(self.tracks_pth, "r", encoding="utf-8") as f:
            self.tracks = json.load(f)
        with open(self.col_pth, "r", encoding="utf-8") as f:
            self.collections = json.load(f)
        with open(self.graph_pth, "r", encoding="utf-8") as f:
            self.graph = json.load(f)
    
    def to_nx_graph(self):
        '''Get dataset as a NetworkX graph.'''
        
        g = nx.Graph()
        g.add_nodes_from(self.graph["collections"], bipartite=0)
        g.add_nodes_from(self.graph["tracks"], bipartite=1) 
        edge_tuples = [ (e["from"], e["to"]) for e in self.graph["edges"] ] 
        g.add_edges_from( edge_tuples )

        track_ids = list(self.tracks)
        col_ids = list(self.collections)

        return g, track_ids, col_ids
    
    def get_playlists_vs_albums(self):
        playlist_ids, album_ids = [],[]
        for id,info in self.collections.items():
            if "playlist" in info["type"]:
                playlist_ids.append(id)
            elif "album" in info["type"]:
                album_ids.append(id)

        return playlist_ids, album_ids
    
    def get_playlists_by_keywords(self, keywords):
        playlist_ids = []

        def keywords_in_info(keywords, info):
            return True if (any(word in info["name"].lower() for word in keywords) or \
                            any(word in info["description"].lower() for word in keywords)) else False

        for id,info in self.collections.items():
            if "playlist" in info["type"] and keywords_in_info(keywords, info):
                playlist_ids.append(id)

        return playlist_ids
    
    def get_projected_graph(self, graph, is_multigraph=False):
        G_projected = bipartite.projected_graph(graph, self.graph["tracks"], multigraph=is_multigraph)
        return G_projected

if __name__ == "__main__":

    # Example usage of the SpotifyGraph dataset class
    root = os.getcwd()
    dataset = SpotifyGraph(path.join(root, "dataset"), None)
    g, track_ids, col_ids = dataset.to_nx_graph()


    # GT_IDS for evaluation after community detection
    playlist_ids, album_ids = dataset.get_playlists_vs_albums()


    # hand picked filter words that occour in name or description of the playlists
    keywords = ["fitness", "workout"]       
    selected_ids = dataset.get_playlists_by_keywords(keywords)
    print(len(selected_ids))


    # TO-DO: community detection with different algorithms




    # JSON COLLECTIONS STRUCTURE FOR EACH PLAYLIST - example
    # "type": "playlist",
    # "name": "Adrenaline Workout",
    # "num_tracks": 31,
    # "description": "If your workout doubles as an outlet for your aggression",
    # "ztracks": [ track ids ]


# to je iz hw3 sam sample 

            # g = girvan_newman_graph(mi)
            # louvain = algorithms.louvain(g)
            # walktrap = algorithms.walktrap(g)
            # label_prop = algorithms.label_propagation(g)
            # true_labels = classes.NodeClustering([[3*i + j for i in range(24)] for j in range(3)], g)

            # a += evaluation.normalized_mutual_information(true_labels, louvain).score
            # b += evaluation.normalized_mutual_information(true_labels, walktrap).score
            # c += evaluation.normalized_mutual_information(true_labels, label_prop).score

            ##############################################################################

            # truth = [[i for i in range(1000)]]
            # g = nx.gnm_random_graph(1000, 1000*k)
            # true_labels = classes.NodeClustering(truth, g)
            # louvain = algorithms.louvain(g)
            # walktrap = algorithms.walktrap(g)
            # label_prop = algorithms.label_propagation(g)

            # a += evaluation.variation_of_information(true_labels, louvain).score
            # b += evaluation.variation_of_information(true_labels, walktrap).score
            # c += evaluation.variation_of_information(true_labels, label_prop).score