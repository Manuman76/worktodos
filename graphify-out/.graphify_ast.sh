#!/usr/bin/env bash
PY=$(cat graphify-out/.graphify_python)
$PY -c "import sys,json;from graphify.extract import collect_files, extract;from pathlib import Path;code_files=[];detect=json.loads(Path('graphify-out/.graphify_detect.json').read_text());[code_files.extend(collect_files(Path(f)) if Path(f).is_dir() else [Path(f)]) for f in detect.get('files',{}).get('code',[])];
if code_files:
    res=extract(code_files)
    Path('graphify-out/.graphify_ast.json').write_text(json.dumps(res,indent=2))
    echo 'AST: '$(len:=0)"