import json
from pathlib import Path
from graphify.extract import collect_files, extract

detect=json.loads(Path('graphify-out/.graphify_detect.json').read_text())
code_files=[]
for f in detect.get('files',{}).get('code',[]):
    p=Path(f)
    if p.is_dir():
        code_files.extend(collect_files(p))
    else:
        code_files.append(p)

if code_files:
    res=extract(code_files)
    Path('graphify-out/.graphify_ast.json').write_text(json.dumps(res,indent=2))
    print(f'AST: {len(res["nodes"]) } nodes, {len(res["edges"]) } edges')
else:
    Path('graphify-out/.graphify_ast.json').write_text(json.dumps({'nodes':[],'edges':[],'input_tokens':0,'output_tokens':0}))
    print('No code files - skipping AST extraction')