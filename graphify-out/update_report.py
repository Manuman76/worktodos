import json
from pathlib import Path
from graphify.build import build_from_json
from graphify.cluster import score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate

extraction=json.loads(Path('graphify-out/.graphify_extract.json').read_text())
detection=json.loads(Path('graphify-out/.graphify_detect.json').read_text())
analysis=json.loads(Path('graphify-out/.graphify_analysis.json').read_text())
labels=json.loads(Path('graphify-out/.graphify_labels.json').read_text())
G=build_from_json(extraction)
communities={int(k):v for k,v in analysis['communities'].items()}
cohesion={int(k):v for k,v in analysis['cohesion'].items()}
tokens={'input':extraction.get('input_tokens',0),'output':extraction.get('output_tokens',0)}

questions=suggest_questions(G,communities,labels)
report=generate(G,communities,cohesion,labels,god_nodes(G),surprising_connections(G,communities),detection,tokens,'.',suggested_questions=questions)
Path('graphify-out/GRAPH_REPORT.md').write_text(report)
print('Report updated with community labels')