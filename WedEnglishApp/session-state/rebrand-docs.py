from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
paths=list((root/'docs/use-cases').glob('*'))+[root/'docs/report-work/final-refresh/diagrams.cjs']
for p in paths:
 if p.suffix not in ('.svg','.html','.md','.puml','.cjs'):continue
 s=p.read_text(encoding='utf-8')
 s=re.sub(r'HITC English(?: Center)?','NHK English times',s,flags=re.I)
 p.write_text(s,encoding='utf-8')
print('Updated diagram sources and use case documentation')
