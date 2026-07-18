import json
from pathlib import Path
from graphify.build import build_from_json
from graphify.analyze import _node_community_map

extraction=json.loads(Path('graphify-out/.graphify_extract.json').read_text())
G=build_from_json(extraction)
analysis=json.loads(Path('graphify-out/.graphify_analysis.json').read_text())
communities={int(k):v for k,v in analysis['communities'].items()}
nc=_node_community_map(communities)
print('num nodes',G.number_of_nodes())
count=0
for node in G.nodes():
    cid=nc.get(node,0)
    print('node',node,'cid',cid,'type',type(cid))
    count+=1
    if count>5: break
