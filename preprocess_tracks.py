# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 16:57:20 2022

@author: Kert PC
"""

import json
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

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
        
    if simple_genre == 'other' :
        #print(genre[:-2] + ' : ' + simple_genre)
        other_count[genre.split('"')[1]] += 1
    
    return simple_genre


slim_tracks = {}
other_count = defaultdict(int)

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
            slim_tracks[song_id] = {'name' : name, 'artist' : artist, 'genre' : genre}
            song_id = 'error'
            name = 'error'
            artist = 'error'
            genre = 'other'
            i += 1
        elif '}' in line:
            break
        
count = defaultdict(int)

for song_id in slim_tracks :
    count[slim_tracks[song_id]['genre']] += 1
    # this could be repourposed for gathering songs that are only part of a specific genre
    
count = dict(count)

y = np.array(list(count.values()))
mylabels = list(count)

plt.pie(y, labels = mylabels)
plt.savefig('../piechart.png', dpi=300)
plt.show() 
    
out_file = open("dataset/tracks_slim.json", "w", encoding='utf-8')
json.dump(slim_tracks, out_file, indent = 4)


