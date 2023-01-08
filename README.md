# Sweet Harmony: What playlists tell us about songs
<sup>This is the main repository for the INA project. The repository was created for a project that was part of Introduction to Network Analysis course at the University of Ljubljana, Faculty for computer and information science.</sub>

## Abstract
In this paper we study a bipartite network of Spotify playlists and tracks. Before any community detection is applied, we project the bipartite network onto the track nodes. We apply a number of community detection algorithms on this unipartite network, and evaluate the resulting communities with regard to the genres of the tracks, and custom-made groupings. We conclude that there is a lot of overlap in the most popular genres, resulting in fuzzy, although still distinct, communities, but we notice that much stronger communities form along linguistic/geographic lines and more specific obscure genres or groupings.

## Dependencies, environment creation and activation

 - python>=3.8
 - ipython>=8.3.0
 - networkx>=2.7
 - scipy>=1.8.1
 - seaborn>=0.11.2
 - tqdm


**Genre distribution**
![Image of a piechart](/assets/piechart.png)

**Custom grouping distribution**
![Image of a generated graph](/assets/piechart_custom_comm.png)

**Tag clouds of children, study, electronic and country grouping**
![Image of a generated graph](/assets/wordcloud.png)