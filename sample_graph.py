# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 10:54:17 2022

@author: Kert PC
"""

import os
from os import path
import json
import random
from collections import defaultdict

import networkx as nx
from networkx.algorithms import bipartite
from cdlib import algorithms, classes, evaluation, readwrite
from tqdm import tqdm

G = nx.Graph()
tracks = {}
playlists = {}

with open('dataset/graph.json', 'r', encoding='utf-8') as file:
    file.readline()
    line = file.readline()
    line = file.readline()
    i = 0
    while ']' not in line: 
        label = line.split('"')[1]
        G.add_node(i, label = label, bipartite=1)
        tracks[label] = i
        i += 1
        line = file.readline()
    
    samp_tracks_lab = random.sample(list(tracks), 500000)
    samp_tracks_val = [tracks[k] for k in samp_tracks_lab]
    sampled_tracks = dict(zip(samp_tracks_lab, samp_tracks_val))

    line = file.readline()
    line = file.readline()
    while ']' not in line: 
        label = line.split('"')[1]
        G.add_node(i, label = label, bipartite=0)
        playlists[label] = i
        i += 1
        line = file.readline()
        
    line = file.readline()
    while ']' not in line: 
        line = file.readline()
        if ']' in line :
            break
        from_label = file.readline().split('"')[3]
        to_label = file.readline().split('"')[3]
        line = file.readline()
        
        #if to_label in sampled_tracks :
        if from_label in playlists and to_label in sampled_tracks :
            pl = playlists[from_label]
            tr = tracks[to_label]
            G.add_edge(pl, tr)
            
    G.remove_nodes_from(list(nx.isolates(G)))
               
"""  
with open(path.join("dataset/sampled_graph.json"), "w", encoding="utf-8") as f:
    json.dump(dict(tracks=[n for n in G.nodes() if n in sampled_tracks.keys()],
                   collections=[n for n in G.nodes() if n in playlists.keys()],
                   edges=[{"from" : u, "to" : v} for u,v in G.edges()]),
                                 f, ensure_ascii=False, indent=2)
"""


def get_projected_graph(graph, is_multigraph=False):
        nodes_for_projection = [n for n, a in graph.nodes(data=True) if a["bipartite"]==1]
        print("Projecting on {} nodes".format(len(nodes_for_projection)))
        G_projected = bipartite.projected_graph(graph, nodes_for_projection, multigraph=is_multigraph)
        return G_projected
    
def get_weighted_projected_graph(graph, ratio=False):
    nodes_for_projection = [n for n, a in graph.nodes(data=True) if a["bipartite"]==1]
    print("Projecting on {} nodes".format(len(nodes_for_projection)))
    G_projected = bipartite.weighted_projected_graph(graph, nodes_for_projection, ratio=ratio)
    return G_projected


 
def save_community(pred, algo_name):
        readwrite.write_community_csv(pred, path.join("results/{}_communities.csv".format(algo_name)), ",")
        
        
def find_communities(g, algorithm):
        algorithm_name = algorithm.__name__
        try:
            print("Starting community detection for {} algorithm".format(algorithm_name))
            if algorithm_name == "overlapping_seed_set_expansion":
                #list of nodes as seeds (preferably each in different community)
                list_of_seeds = []
                community_prediction = algorithm(g, seeds=list_of_seeds)
            else:
                community_prediction = algorithm(g)
            print("Saving...")
            save_community(community_prediction, algorithm_name)
        except Exception as e:
            print("Error with {} algorithm".format(algorithm_name))
            print(type(e), e)
        else:
            print("Saved communities file for {} algorithm".format(algorithm_name))

def find_communities_weight(g, algorithm):
        algorithm_name = algorithm.__name__
        try:
            weights = []
            edge_data = g.edges.data("weight", default=0)
            for edge in edge_data :
                weights.append(edge[2])

            print("Starting community detection for {} algorithm".format(algorithm_name))
            community_prediction = algorithm(g, weights=weights)
            print("Saving...")
            save_community(community_prediction, algorithm_name + '_weighted')
        except Exception as e:
            print("Error with {} algorithm".format(algorithm_name))
            print(type(e), e)
        else:
            print("Saved communities file for {} algorithm".format(algorithm_name))




print("Starting projection...")
G_proj = get_projected_graph(G)
G_w_proj = get_weighted_projected_graph(G, ratio=False)

list_of_overlapping_algorithms = [  algorithms.label_propagation,
                                    algorithms.leiden
                                  ]
print("Starting community detection...\n")
for algo in list_of_overlapping_algorithms:
    find_communities(G_proj, algo)
    print('Done one')
    
list_of_overlapping_algorithms = [algorithms.leiden
                               ]
print("Starting community detection...\n")
for algo in list_of_overlapping_algorithms:
    find_communities_weight(G_w_proj, algo)
    print('Done one')
    
    
n_of_songs = 150000000
tracks_slim = {}
with open('dataset/tracks_slim.json', 'r', encoding='utf-8') as file:
    file.readline()
    i = 0
    song_id = 'error'
    name = 'error'
    artist = 'error'
    genre = 'other'
    while i < n_of_songs: 
        line = file.readline()
        if ': {' in line :
            song_id = line.split('"')[1]
        elif 'name' in line:
            name = line.split('"')[3]
        elif 'artist"' in line:
            artist = line.split('"')[3]
        elif 'genre' in line:
            in_list = True
            genre = line.split('"')[3] 
        elif '},' in line:
            tracks_slim[song_id] = {'name' : name, 'artist' : artist, 'genre' : genre}
            song_id = 'error'
            name = 'error'
            artist = 'error'
            genre = 'other'
            i += 1
        elif '}' in line:
            break


nodes_proj = G_proj.nodes()




counts_communities = {}
    
with open('results/leiden_weighted_communities.csv', 'r', encoding='utf-8') as file:
    comm_nodes = file.readline().split(',')
    i = 0
    all_n_sum = 0
    while len(comm_nodes) > 1000 :
        all_n_sum = len(comm_nodes)
        counts_communities[i] = (defaultdict(int), all_n_sum)
        for comm_node in comm_nodes :
            idx_node = int(comm_node)
            label = nodes_proj[idx_node]['label']
            if label in tracks_slim :
                counts_communities[i][0][tracks_slim[label]['genre']] += 1
            else :
                print(label + ' not found in tracks.')
                
        for count in counts_communities[i][0] :
            counts_communities[i][0][count] /= all_n_sum
        i += 1
        comm_nodes = file.readline().split(',')
        
    
    
    