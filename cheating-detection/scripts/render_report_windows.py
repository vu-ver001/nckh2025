"""Use the document skill renderer with native Word conversion when LibreOffice is absent."""
from pathlib import Path
import importlib.util
import subprocess
import os
import sys

ROOT=Path(__file__).resolve().parents[1]
SKILL=Path.home()/'.codex/plugins/cache/openai-primary-runtime/documents/26.905.11957/skills/documents/render_docx.py'
RUNTIME=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'
os.environ['PATH']=str(RUNTIME/'native/poppler/Library/bin')+os.pathsep+os.environ['PATH']
spec=importlib.util.spec_from_file_location('document_skill_renderer',SKILL)
renderer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def word_conversion(doc_path,user_profile,convert_tmp_dir,stem,verbose):
    pdf=Path(convert_tmp_dir)/(stem+'.pdf')
    result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
        str(ROOT/'scripts/export_word_pdf.ps1'),'-InputDoc',str(Path(doc_path).resolve()),
        '-OutputPdf',str(pdf)],capture_output=True,text=True,timeout=180)
    if result.returncode or not pdf.is_file():
        raise RuntimeError(result.stdout+'\n'+result.stderr)
    return str(pdf),'Native Microsoft Word PDF export; LibreOffice unavailable'


renderer.convert_to_pdf=word_conversion
renderer.main()
