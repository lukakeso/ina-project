import matplotlib.pyplot as plt
import json
import seaborn as sns
from collections import defaultdict
import numpy as np

colors = sns.color_palette("hls", 17)
colors.append((0.5, 0.5, 0.5))

with open("dataset/custom_communities_corrected.json", "r", encoding="utf-8") as f:
    custom_communities = json.load(f)

#genre_order = ['rock', 'metal', 'jazz', 'indie', 'country', 'reggae', 'hip hop', 'rap', 'electronic', 'pop', 'latin', 'classical', 'worship', 'ethnic', 'ambient', 'soundtrack', 'radio', 'other']
#genre_order = ['rock & metal', 'jazz & blues', 'country', 'hip hop','electronic', 'pop', 'latin', 'classical', 'worship', 'ethnic', 'ambient', 'soundtrack', 'radio', 'other']
genre_order = sorted(list(custom_communities["tracks"].keys()))

count = defaultdict(int)

for genre, songs in custom_communities["tracks"].items():
    count[genre] = len(songs)
    
y = []
for genre in genre_order :
    y.append(count[genre])
y = np.array(y)

plt.pie(y, labels = genre_order, colors = colors, wedgeprops={"edgecolor":"k",'linewidth': 0.4, 'linestyle': 'solid', 'antialiased': True})
plt.savefig('piechart.png', dpi=300)
#plt.show() 