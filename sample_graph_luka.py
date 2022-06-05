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
from interruptingcow import timeout

import networkx as nx
from networkx.algorithms import bipartite
from cdlib import algorithms, classes, evaluation, readwrite
from cdlib.classes import *
from tqdm import tqdm

from sklearn import metrics
from load_track_metadata import load_tracks

TIMEOUT_MINUTES = 35

def load_graph(n_samples = 800000) :
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
        
        samp_tracks_lab = random.sample(list(tracks), n_samples)
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
    
    Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
    G_max = G.subgraph(Gcc[0])
    
    return G, G_max, tracks, playlists


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
        
        
def find_communities(g, algorithm, metadata=None):
        algorithm_name = algorithm.__name__
        community_prediction = None
        try:
            with timeout(60*TIMEOUT_MINUTES, exception=RuntimeError):
                print("Starting community detection for {} algorithm".format(algorithm_name))
                if algorithm_name == "eva" or algorithm_name == "ilouvain":
                    community_prediction = algorithm(g, labels=metadata)
                else:
                    community_prediction = algorithm(g)
                print("Saving...")
                save_community(community_prediction, algorithm_name)
        except Exception as e:
            print("Error with {} algorithm".format(algorithm_name))
            print(type(e), e)
        else:
            print("Saved communities file for {} algorithm".format(algorithm_name))
        return community_prediction

def find_communities_weight(g, algorithm):
        algorithm_name = algorithm.__name__
        community_prediction = None
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
        return community_prediction

def get_community_results(G, algo, tracks_slim) :
    nodes_proj = G.nodes()
    counts_communities = {}
    
    maj_labeling = []
    truth_labeling = []
    
    with open('results/' + algo + '_communities.csv', 'r', encoding='utf-8') as file:
        print('Reading results/' + algo + '_communities.csv')
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
                    truth_labeling.append(tracks_slim[label]['genre'])
                else :
                    print(label + ' not found in tracks.')
                    truth_labeling.append('other')
                    
            for count in counts_communities[i][0] :
                counts_communities[i][0][count] /= all_n_sum
            majority_label = max(counts_communities[i][0], key=counts_communities[i][0].get)
            
            for comm_node in comm_nodes :
                idx_node = int(comm_node)
                maj_labeling.append(majority_label)
            
            i += 1
            comm_nodes = file.readline().split(',')
            
            
    report = metrics.classification_report(maj_labeling, truth_labeling)       
    
    with open('results/results_' + algo + '.txt', 'w') as fl:
        fl.write(report)
        print('Results saved to results/results_' + algo + '.txt')
        
    
def partition(G, tracks):
  P = {}
  for node in G.nodes(data = True):
      if node[1]['label'] in tracks :
          genre = tracks[node[1]['label']]['genre']
      else :
          genre = 'other'
      if genre not in P:
          P[genre] = []
      P[genre].append(node[0])
  return NodeClustering(list(P.values()), G, 'Truth')        


if __name__ == '__main__' :
    
    G, G_max, tracks, playlists = load_graph()
    tracks_slim = load_tracks()

    invalid_keys = {'genre', 'artist', 'name', 'key', 'mode', 'popularity', 'tempo', 'loudness'}
    metadata = {}
    for i, info in tracks_slim.items():
        metadata[i] = [(k,v) for k,v in info.items() if k not in invalid_keys]
    
    print("Starting projection...")
    G_proj = get_projected_graph(G_max)
    #G_w_proj = get_weighted_projected_graph(G_max, ratio=False)
    
    list_of_overlapping_algorithms = [algorithms.ilouvain,
                                      algorithms.eva
                                      ]

    # list_of_overlapping_algorithms = [algorithms.leiden, 
    #                                   algorithms.infomap, 
    #                                   algorithms.sbm_dl,
    #                                  ]
    
    partitions = {}
    print("Starting community detection...\n")
    for algo in list_of_overlapping_algorithms:
        partitions[algo.__name__] = find_communities(G_proj, algo, metadata=metadata)
        print('Done one')
    
    # list_of_overlapping_algorithms = [algorithms.leiden
    #                                ]
    # print("Starting community detection...\n")
    # for algo in list_of_overlapping_algorithms:
    #     partitions[algo.__name__ + '_weighted'] =  find_communities_weight(G_w_proj, algo)
    #     print('Done one')


    #P_w = partition(G_w_proj, tracks_slim)
    P = partition(G_proj, tracks_slim)
    
    #P_pred = readwrite.read_community_csv("results/leiden_communities.csv")
    NMIs = {}
    for part in partitions :
        if 'weighted' in part :  
            NMIs[part] = partitions[part].normalized_mutual_information(P_w).score
        else :
            NMIs[part] = partitions[part].normalized_mutual_information(P).score
        
        get_community_results(G_proj, part, tracks_slim)
    print(NMIs)
    
    #sz = evaluation.size(G_proj,P_pred)

