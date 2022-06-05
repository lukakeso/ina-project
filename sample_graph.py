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

n_samples = 800000

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
        community_prediction = None
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



print("Starting projection...")
G_proj = get_projected_graph(G_max)
G_w_proj = get_weighted_projected_graph(G_max, ratio=False)

list_of_overlapping_algorithms = [  #algorithms.girvan_newman,
                                    algorithms.leiden
                                  ]

partitions = {}
print("Starting community detection...\n")
for algo in list_of_overlapping_algorithms:
    partitions[algo.__name__] = find_communities(G_proj, algo)
    print('Done one')

list_of_overlapping_algorithms = [algorithms.leiden
                               ]
print("Starting community detection...\n")
for algo in list_of_overlapping_algorithms:
    partitions[algo.__name__ + '_weighted'] =  find_communities_weight(G_w_proj, algo)
    print('Done one')

"""
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
            split = line.split('"')
            if len(split) > 3 :
                name = split[3]
            else :
                break
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
"""
"""
def get_genre(genre) :
    simple_genre = 'other'
    if 'rock' in genre or 'grunge' in genre or 'punk' in genre or 'metal' in genre or 'slayer' in genre:
        simple_genre = 'rock & metal' 
        
    #elif 'metal' in genre or 'slayer' in genre:
    #    simple_genre = 'metal'
        
    elif 'country' in genre or 'americana' in genre or 'honky' in genre or 'folk' in genre or 'redneck' in genre:
        simple_genre = 'country'
        
    elif 'jazz' in genre or 'big band' in genre or 'sax' in genre or 'blue' in genre or 'soul' in genre or 'funk' in genre or 'bossa' in genre or 'reggae' in genre or 'ska' in genre or 'dub' in genre:
        simple_genre = 'jazz & blues'
        
    #elif 'funk' in genre :
    #    simple_genre = 'funk'
        
    elif 'pop' in genre or 'neo mellow' in genre  or 'alt z' in genre or 'easy listening' in genre or 'eurovision' in genre or 'francoton' in genre or 'boy' in genre: 
        simple_genre = 'pop'
        
    #elif 'blue' in genre or 'soul' in genre :
    #    simple_genre = 'blues'
        
    #elif 'indie' in genre :
    #    simple_genre = 'indie'
        
    elif 'hip hop' in genre or 'rap' in genre or 'r&b' in genre or 'bop' in genre or 'disco' in genre or 'phonk' in genre or 'bass' in genre or 'grime' in genre  or 'drill' in genre or 'trap' in genre:
        simple_genre = 'hip hop'
        
    #elif 'rap' in genre :
    #    simple_genre = 'rap'
        
    elif 'edm' in genre or 'tehno' in genre or 'big room' in genre or 'house' in genre or 'core' in genre or 'step' in genre or 'dance' in genre or 'wave' in genre or 'electro' in genre or 'club' in genre or 'tronica' in genre or 'tech' in genre or 'trance' in genre: 
        simple_genre = 'electronic'
        
    elif 'classic' in genre or 'modernism' in genre or 'instrumental' in genre or 'baroque' in genre or 'romantic' in genre:
        simple_genre = 'classical'
        
    #elif 'reggae' in genre or 'ska' in genre or 'dub' in genre:
    #    simple_genre = 'reggae'
        
    elif 'gospel' in genre or 'gregorian' in genre or 'shamanic' in genre or 'christ' in genre or 'worship' in genre or 'pastor' in genre or 'cristiano' in genre  or 'adoracao' in genre or 'islam' in genre or 'quran' in genre or 'ccm' in genre: 
        simple_genre = 'worship'
        
    elif 'latin' in genre or 'tango' in genre or 'flamenco' in genre or 'opm' in genre or 'axe' in genre or 'tropical' in genre or 'cumbia' in genre or 'mariachi' in genre or 'mpb' in genre or 'corrido' in genre or 'salsa' in genre or 'bolero' in genre or 'gruper' in genre or 'melodica' in genre or 'musica' in genre or 'sierr' in genre or 'ranchera' in genre or 'sertanejo' in genre or 'arrocha' in genre or 'bachata' in genre or 'cuba' in genre or 'espan' in genre or 'chile' in genre or 'argent' in genre or 'banda' in genre or 'mexic' in genre:
        simple_genre = 'latin'
        
    elif 'kizomba' in genre or 'chutney' in genre or 'dangdut' in genre or 'folc' in genre or 'celtic' in genre or 'tradi' in genre or 'turk' in genre or 'arab' in genre or 'awaii' in genre or 'accordion' in genre or 'narodna' in genre or 'pagode' in genre or 'samba' in genre or 'angola' in genre or 'native' in genre or 'indigenous' in genre:
        simple_genre = 'ethnic'
        
    elif 'ambient' in genre or 'new age' in genre or 'relax' in genre or 'rain' in genre or 'meditation' in genre or 'library' in genre or 'lounge' in genre or 'noise' in genre or 'lo-fi' in genre or 'chill' in genre or 'writing' in genre or 'lesen' in genre or 'background' in genre or 'sleep' in genre or 'environ' in genre or 'spa' in genre: 
        simple_genre = 'ambient'
        
    elif 'film' in genre or 'wood' in genre or 'middle earth' in genre or 'anime' in genre or 'vgm' in genre or 'score' in genre or 'soundtrack' in genre or 'video game' in genre or 'final fantasy' in genre: 
        simple_genre = 'soundtrack'
        
    elif 'hoerspiel' in genre or 'adult standards' in genre or 'rai' in genre:
        simple_genre = 'radio'
        
    #elif 'kinder' in genre or 'lullaby' in genre or 'child' in genre or 'barnemusik' in genre or 'nurse' in genre or 'cartoon' in genre or 'barnmusik' in genre:
    #    simple_genre = 'children'
        
    #if simple_genre == 'other' :
        #print(genre[:-2] + ' : ' + simple_genre)
        #other_count[genre.split('"')[1]] += 1
    
    return simple_genre
"""
def get_genre(genre) :
    simple_genre = 'other'
    if 'rock' in genre or 'grunge' in genre or 'punk' in genre :
        simple_genre = 'rock' 
        
    elif 'metal' in genre or 'slayer' in genre:
        simple_genre = 'metal'
        
    elif 'country' in genre or 'americana' in genre or 'honky' in genre or 'folk' in genre or 'redneck' in genre:
        simple_genre = 'country'
        
    elif 'jazz' in genre or 'big band' in genre or 'sax' in genre or 'bossa' in genre:
        simple_genre = 'jazz'
        
    elif 'funk' in genre :
        simple_genre = 'funk'
        
    elif 'pop' in genre or 'neo mellow' in genre  or 'alt z' in genre or 'easy listening' in genre or 'eurovision' in genre or 'francoton' in genre or 'boy' in genre: 
        simple_genre = 'pop'
        
    elif 'blue' in genre or 'soul' in genre :
        simple_genre = 'blues'
        
    elif 'indie' in genre :
        simple_genre = 'indie'
        
    elif 'hip hop' in genre or 'r&b' in genre or 'bop' in genre or 'disco' in genre or 'phonk' in genre or 'bass' in genre or 'grime' in genre  or 'drill' in genre or 'trap' in genre:
        simple_genre = 'hip hop'
        
    elif 'rap' in genre :
        simple_genre = 'rap'
        
    elif 'edm' in genre or 'tehno' in genre or 'big room' in genre or 'house' in genre or 'core' in genre or 'step' in genre or 'dance' in genre or 'wave' in genre or 'electro' in genre or 'club' in genre or 'tronica' in genre or 'tech' in genre or 'trance' in genre: 
        simple_genre = 'electronic'
        
    elif 'classic' in genre or 'modernism' in genre or 'instrumental' in genre or 'baroque' in genre or 'romantic' in genre:
        simple_genre = 'classical'
        
    elif 'reggae' in genre or 'ska' in genre or 'dub' in genre:
        simple_genre = 'reggae'
        
    elif 'gospel' in genre or 'gregorian' in genre or 'shamanic' in genre or 'christ' in genre or 'worship' in genre or 'pastor' in genre or 'cristiano' in genre  or 'adoracao' in genre or 'islam' in genre or 'quran' in genre or 'ccm' in genre: 
        simple_genre = 'worship'
        
    elif 'latin' in genre or 'tango' in genre or 'flamenco' in genre or 'opm' in genre or 'axe' in genre or 'tropical' in genre or 'cumbia' in genre or 'mariachi' in genre or 'mpb' in genre or 'corrido' in genre or 'salsa' in genre or 'bolero' in genre or 'gruper' in genre or 'melodica' in genre or 'musica' in genre or 'sierr' in genre or 'ranchera' in genre or 'sertanejo' in genre or 'arrocha' in genre or 'bachata' in genre or 'cuba' in genre or 'espan' in genre or 'chile' in genre or 'argent' in genre or 'banda' in genre or 'mexic' in genre:
        simple_genre = 'latin'
        
    elif 'kizomba' in genre or 'chutney' in genre or 'dangdut' in genre or 'folc' in genre or 'celtic' in genre or 'tradi' in genre or 'turk' in genre or 'arab' in genre or 'awaii' in genre or 'accordion' in genre or 'narodna' in genre or 'pagode' in genre or 'samba' in genre or 'angola' in genre or 'native' in genre or 'indigenous' in genre:
        simple_genre = 'ethnic'
        
    elif 'ambient' in genre or 'new age' in genre or 'relax' in genre or 'rain' in genre or 'meditation' in genre or 'library' in genre or 'lounge' in genre or 'noise' in genre or 'lo-fi' in genre or 'chill' in genre or 'writing' in genre or 'lesen' in genre or 'background' in genre or 'sleep' in genre or 'environ' in genre or 'spa' in genre: 
        simple_genre = 'ambient'
        
    elif 'film' in genre or 'wood' in genre or 'middle earth' in genre or 'anime' in genre or 'vgm' in genre or 'score' in genre or 'soundtrack' in genre or 'video game' in genre or 'final fantasy' in genre: 
        simple_genre = 'soundtrack'
        
    elif 'hoerspiel' in genre or 'adult standards' in genre or 'rai' in genre:
        simple_genre = 'radio'
        
    elif 'kinder' in genre or 'lullaby' in genre or 'child' in genre or 'barnemusik' in genre or 'nurse' in genre or 'cartoon' in genre or 'barnmusik' in genre:
        simple_genre = 'children'
        
    #if simple_genre == 'other' :
        #print(genre[:-2] + ' : ' + simple_genre)
        #other_count[genre.split('"')[1]] += 1
    
    return simple_genre

other_count = {}
tracks_slim = {}

n_of_songs = 15000000
#with open('dataset/filtered_graph.json', "r", encoding="utf-8") as f:
#    graph = json.load(f)
#    filtered_tracks = graph["tracks"]

with open('dataset/tracks.json', 'r', encoding='utf-8') as file:

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
        elif 'artist_genres' in line:
            in_list = True
            if '[]' in line :
                in_list = False
            while in_list :
                line = file.readline()
                if ']' in line :
                    in_list = False
                    break
                if 'other' in genre :
                    genre = get_genre(line)
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
    
with open('results/leiden_communities.csv', 'r', encoding='utf-8') as file:
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
        
from cdlib.classes import *

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

from cdlib import evaluation

P_w = partition(G_w_proj, tracks_slim)
P = partition(G_proj, tracks_slim)

#P_pred = readwrite.read_community_csv("results/leiden_communities.csv")
NMIs = {}
for part in partitions :
    if 'weighted' in part :  
        NMIs[part] = partitions[part].normalized_mutual_information(P).score
    else :
        NMIs[part] = partitions[part].normalized_mutual_information(P_w).score
        
print(NMIs)

#sz = evaluation.size(G_proj,P_pred)

