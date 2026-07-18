import json
from pathlib import Path
from graphify.build import build_from_json
from graphify.export import to_html

extraction=json.loads(Path('graphify-out/.graphify_extract.json').read_text())
analysis=json.loads(Path('graphify-out/.graphify_analysis.json').read_text())
labels=json.loads(Path('graphify-out/.graphify_labels.json').read_text())
G=build_from_json(extraction)
communities={k:v for k,v in analysis['communities'].items()}
to_html(G,communities,'graphify-out/graph.html',community_labels=labels or None, member_counts={})
print('graph.html written - open in any browser, no server needed')