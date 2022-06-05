import json
import networkx as nx
import matplotlib.pyplot as plt




for name in ["graph", "filtered_graph"]:
    with open('dataset/{}.json'.format(name), "r", encoding="utf-8") as f:
        graph = json.load(f)
    g = nx.Graph()
    g.add_nodes_from(graph["collections"], bipartite=0)
    g.add_nodes_from(graph["tracks"], bipartite=1) 
    edge_tuples = [ (e["from"], e["to"]) for e in graph["edges"] ] 
    g.add_edges_from( edge_tuples )

    if name == "graph":
        o_degrees = [d for _, d in g.degree()]
    elif name == "filtered_graph":
        f_degrees = [d for _, d in g.degree()]

max_deg = 60+1
fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(111)

ax.hist(f_degrees, bins=max_deg, range=(0,max_deg), edgecolor='black', log=True, fc=(1, 0, 0, 0.4))
n, bins, patches = ax.hist(o_degrees, bins=max_deg, range=(0,max_deg), edgecolor='black', log=True, fc=(0, 0, 1, 0.4))


ticks = [patch.get_x() + patch.get_width()/2 for patch in patches]
ticklabels = [i for i in range(max_deg)]
plt.xticks(ticks, ticklabels)
#plt.yscale('log')
plt.tight_layout()


plt.savefig('degree_dist.png')