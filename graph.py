import os
from os import path
import json

import networkx as nx
from networkx.algorithms import bipartite
from cdlib import algorithms, classes, evaluation, readwrite

class SpotifyGraph():

    def __init__(self, dir, features_dir):

        self.base_dir = path.join(dir, "dataset")
        self.save_dir = path.join(dir, "results")
        # self.tracks_pth = path.join(self.base_dir, "tracks.json")
        # self.col_pth = path.join(self.base_dir, "collections.json")
        self.graph_pth = path.join(self.base_dir, "filtered_graph.json")

        self.ft_dir = features_dir
        self.features_dict = {}

        self.load()

    def load(self):
        print("Loading graph...")
        # with open(self.tracks_pth, "r", encoding="utf-8") as f:
        #     self.tracks = json.load(f)
        # with open(self.col_pth, "r", encoding="utf-8") as f:
        #     self.collections = json.load(f)
        with open(self.graph_pth, "r", encoding="utf-8") as f:
            self.graph = json.load(f)

    def save_graph(self, G):
        with open(path.join(self.base_dir, "filtered_graph.json"), "w", encoding="utf-8") as f:
            json.dump(dict(tracks=[n for n in G.nodes() if n not in self.col_ids_deg.keys()],
                           collections=[n for n in G.nodes() if n in self.col_ids_deg.keys()],
                           edges=[{"from" : u, "to" : v} for u,v in G.edges()]),
                           f, ensure_ascii=False, indent=2)

    def to_nx_graph(self):
        '''Get dataset as a NetworkX graph.'''
        
        g = nx.Graph()
        g.add_nodes_from(self.graph["collections"], bipartite=0)
        g.add_nodes_from(self.graph["tracks"], bipartite=1) 
        edge_tuples = [ (e["from"], e["to"]) for e in self.graph["edges"] ] 
        g.add_edges_from( edge_tuples )

        #self.track_ids_deg = {i : g.degree[i] for i in self.graph["tracks"]}
        #col_ids_deg = {i : g.degree[i] for i in self.graph["collections"]}

        return g#, track_ids_deg, col_ids_deg

    def filter_graph(self, g, deg=1):
        print("Removing nodes with k<={}...".format(deg))
        print("Num nodes before: {}".format(len(g.nodes)))
        nodes_to_remove = [i for (i, d) in self.track_ids_deg.items() if d <= deg]
        g.remove_nodes_from(nodes_to_remove)
        print("Num nodes after: {}".format(len(g.nodes)))
        largest_cc = max(nx.connected_components(g), key=len)
        print("Saving new graph...")
        self.save_graph(g.subgraph(largest_cc))


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
        nodes_for_projection = [n for n, a in graph.nodes(data=True) if a["bipartite"]==1]
        print("Projecting on {} nodes".format(len(nodes_for_projection)))
        G_projected = bipartite.projected_graph(graph, nodes_for_projection, multigraph=is_multigraph)
        return G_projected
    
    def save_community(self, pred, algo_name):
        readwrite.write_community_csv(pred, path.join(self.save_dir, "{}_communities.csv".format(algo_name)), ",")

    def find_communities(self, g, algorithm):
        algorithm_name = algorithm.__name__
        try:
            print("Starting community detection for {} algorithm".format(algorithm_name))
            if algorithm_name == "overlapping_seed_set_expansion":
                #list of nodes as seeds (preferably each in different community)
                list_of_seeds = []
                community_prediction = algorithm(g, seeds=list_of_seeds)
            else:
                community_prediction = algorithm(g)
            self.save_community(community_prediction, algorithm_name)
        except Exception as e:
            print("Error with {} algorithm".format(algorithm_name))
            print(type(e), e)
        else:
            print("Saved communities file for {} algorithm".format(algorithm_name))


if __name__ == "__main__":

    # Example usage of the SpotifyGraph dataset class
    root = os.getcwd()
    data = SpotifyGraph(root, None)
    g = data.to_nx_graph()
    print("Num nodes:", len(g))
    print("Starting projection...")
    g = data.get_projected_graph(g)
    print("Num nodes after projection:", len(g))

    # GT_IDS for evaluation after community detection
    #playlist_ids, album_ids = dataset.get_playlists_vs_albums()


    # hand picked filter words that occour in name or description of the playlists
    #keywords = ["fitness", "workout"]       
    #selected_ids = dataset.get_playlists_by_keywords(keywords)

    # TO-DO: community detection with different algorithms
    list_of_overlapping_algorithms = [algorithms.aslpaw, 
                                      #algorithms.dcs, 
                                      #algorithms.lais2,
                                      #algorithms.overlapping_seed_set_expansion,
                                      #algorithms.umstmo,
                                      #algorithms.percomvc,
                                     ]
    print("Starting community detection...")
    for algo in list_of_overlapping_algorithms:
        data.find_communities(g, algo)
        print()


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