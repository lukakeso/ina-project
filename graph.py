import os
from os import path
import json
from collections import defaultdict
from interruptingcow import timeout

from tqdm import tqdm
import networkx as nx
from networkx.algorithms import bipartite
from cdlib import algorithms, classes, evaluation, readwrite

class SpotifyGraph():

    def __init__(self, dir, features_dir):

        self.base_dir = path.join(dir, "dataset")
        self.save_dir = path.join(dir, "results")
        self.tracks_pth = path.join(self.base_dir, "tracks.json")
        self.col_pth = path.join(self.base_dir, "collections.json")
        self.graph_pth = path.join(self.base_dir, "graph.json")

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
            json.dump(dict(tracks=[n for n in G.nodes() if n in self.track_ids_deg.keys()],
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

        self.track_ids_deg = {i : g.degree[i] for i in self.graph["tracks"]}
        self.col_ids_deg = {i : g.degree[i] for i in self.graph["collections"]}

        return g#, track_ids_deg, col_ids_deg

    def filter_graph(self, g, deg=1):
        print("Removing nodes with k<={}...".format(deg))
        print("Num nodes before filter: {}".format(len(g.nodes)))
        nodes_to_remove = [i for (i, d) in self.track_ids_deg.items() if d <= deg]
        g.remove_nodes_from(nodes_to_remove)
        # nodes_to_remove = [i for (i, d) in self.track_ids_deg.items() if d >= 51 and d <= 53]
        # g.remove_nodes_from(nodes_to_remove)
        print("Num nodes after filter: {}".format(len(g.nodes)))
        largest_cc = max(nx.connected_components(g), key=len)
        print("Largest 5 CCs: ", [len(c) for c in sorted(nx.connected_components(g), key=len, reverse=True)][:5])
        print("Num nodes final: {}".format(len(largest_cc)))
        print("Saving new graph...")
        g = g.subgraph(largest_cc)
        self.save_graph(g)
        return g


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
    
    def get_custom_projected_graph(self, graph, is_multigraph=False):
        with open("dataset/custom_communities.json", "r", encoding="utf-8") as f:
            comm = json.load(f)
        nodes_for_projection, nodes_for_projection_t, nodes_for_projection_c = [],[],[]
        for tracks in comm["tracks"].values():
            nodes_for_projection_t += tracks
        print("Tracks: ", len(nodes_for_projection_t))
        for col in comm["collections"].values():
            nodes_for_projection_c += col
        print("Collections: ", len(nodes_for_projection_c))

        nodes_for_subgraph = nodes_for_projection_t + nodes_for_projection_c
        nodes_for_subgraph = list(set(nodes_for_subgraph))
        print("Nodes w/o duplicates: ",len(nodes_for_subgraph))
        g = graph.subgraph(nodes_for_subgraph)
        print("Total CCs: ", len([len(c) for c in sorted(nx.connected_components(g), key=len, reverse=True)]))
        print("Largest 5 CCs: ", [len(c) for c in sorted(nx.connected_components(g), key=len, reverse=True)][:5])
        print("Smallest 5 CCs: ", [len(c) for c in sorted(nx.connected_components(g), key=len, reverse=False)][:5])
        
        largest_cc = max(nx.connected_components(g), key=len)
        G_bipartite = graph.subgraph(largest_cc)
        nodes_for_projection_t = [n for n in nodes_for_projection_t if n in G_bipartite.nodes()]
        nodes_for_projection_c = [n for n in nodes_for_projection_c if n in G_bipartite.nodes()]
        print("Projecting on {} nodes".format(len(set(nodes_for_projection_t))))

        G_projected = bipartite.projected_graph(G_bipartite, nodes_for_projection_t, multigraph=is_multigraph)
        return G_projected, G_bipartite
    
    def save_community(self, pred, algo_name):
        readwrite.write_community_csv(pred, path.join(self.save_dir, "{}_communities.csv".format(algo_name)), ",")

    def find_communities(self, g, algorithm):
        algorithm_name = algorithm.__name__
        try:
            with timeout(60*35, exception=RuntimeError):
                print("Starting community detection for {} algorithm".format(algorithm_name))
                if algorithm_name == "angel":
                    community_prediction = algorithm(g, threshold=0.3, min_community_size=500)
                elif algorithm_name == "node_perception":
                    community_prediction = algorithm(g, threshold=0.3, overlap_threshold=0.3, min_comm_size=500)
                elif algorithm_name == "CPM_Bipartite":
                    community_prediction = algorithm(g, 1)
                elif algorithm_name == "spectral":
                    community_prediction = algorithm(g, kmax=17)
                else:
                    community_prediction = algorithm(g)
                print("Saving...")
                self.save_community(community_prediction, algorithm_name)
        except Exception as e:
            print("Error with {} algorithm".format(algorithm_name))
            print(type(e), e)
        else:
            print("Saved communities file for {} algorithm".format(algorithm_name))

    def find_common_keywords(self):
        all_keywords = defaultdict(int)
        for id, info in tqdm(self.collections.items()):
            if "playlist" in info["type"]:
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
                                .replace("$","").replace("|","").split()

                name = info["name"].lower()\
                                .replace("(","").replace(")","").replace("{","").replace("}","")\
                                .replace("[","").replace("]","").replace("!","").replace("?","")\
                                .replace("(","").replace(")","").replace(",","").replace(".","")\
                                .replace("-","").replace("–","").replace(";","").replace(":","")\
                                .replace("&","").replace("%","").replace("/","").replace("\\","")\
                                .replace("$","").replace("|","").split()
                
                for word in name + decription:
                    all_keywords[word] += 1
        
        
        with open(path.join(self.base_dir, "phrases.json"), "w", encoding="utf-8") as f:
            json.dump(dict(phrases=dict(sorted(all_keywords.items(), key=lambda item: item[1], reverse=True))), \
                            f, ensure_ascii=False, indent=2)


if __name__ == "__main__":

    # Example usage of the SpotifyGraph dataset class
    root = os.getcwd()
    data = SpotifyGraph(root, None)
    g = data.to_nx_graph()
    print("Num nodes:", len(g))
    #data.find_common_keywords()
    print("Bipartite?", bipartite.is_bipartite(g))


    print("Starting projection...")
    #g_ = data.get_projected_graph(g)
    print(len(g.nodes), bipartite.is_bipartite(g))
    g_, gb_ = data.get_custom_projected_graph(g)
    print(len(g_.nodes), bipartite.is_bipartite(g_))
    print(len(gb_.nodes), bipartite.is_bipartite(gb_))
    print("Total CCs: ", len([len(c) for c in sorted(nx.connected_components(g_), key=len, reverse=True)]))
    print("Largest 5 CCs: ", [len(c) for c in sorted(nx.connected_components(g_), key=len, reverse=True)][:5])
    
    list_of_overlapping_algorithms = [algorithms.angel,
                                    algorithms.core_expansion,
                                    algorithms.node_perception,
                                    algorithms.lpanni,
                                    algorithms.graph_entropy,
                                    algorithms.umstmo,

                                    #   algorithms.lemon,
                                    #   algorithms.multicom,
                                    #   algorithms.overlapping_seed_set_expansion,
                                    ]
    list_of_crisp_algorithms = [algorithms.leiden, 
                                algorithms.infomap, 
                                algorithms.sbm_dl,
                                ]
    list_of_bipartite_algorithms = [#algorithms.bimlpa, 
                                    algorithms.condor,
                                    algorithms.CPM_Bipartite,
                                    #algorithms.infomap_bipartite,
                                    algorithms.spectral,
                                    ]
    print("Starting community detection...\n")

    # for algo in list_of_overlapping_algorithms:
    #     data.find_communities(g_, algo)
    #     print()
    for algo in list_of_bipartite_algorithms:
        data.find_communities(gb_, algo)
        print()
    # for algo in list_of_crisp_algorithms:
    #     data.find_communities(g_, algo)
    #     print()