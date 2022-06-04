# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 10:54:17 2022

@author: Kert PC
"""

import os
from os import path
import json
import random

import networkx as nx

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
        G.add_node(i, label = label)
        tracks[label] = i
        i += 1
        line = file.readline()
    
    samp_tracks_lab = random.sample(list(tracks), 14000)
    samp_tracks_val = [tracks[k] for k in samp_tracks_lab]
    sampled_tracks = dict(zip(samp_tracks_lab, samp_tracks_val))

    line = file.readline()
    line = file.readline()
    while ']' not in line: 
        label = line.split('"')[1]
        G.add_node(i, label = label)
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
               
    
with open(path.join("dataset/sampled_graph.json"), "w", encoding="utf-8") as f:
    json.dump(dict(tracks=[n for n in G.nodes() if n in sampled_tracks.keys()],
                   collections=[n for n in G.nodes() if n in playlists.keys()],
                   edges=[{"from" : u, "to" : v} for u,v in G.edges()]),
                                 f, ensure_ascii=False, indent=2)
        
