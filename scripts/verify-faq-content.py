from pathlib import Path
from html.parser import HTMLParser
import re,json,html,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'dist'); findings=[]; total=0
class Visible(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.text=[]
    def handle_starttag(self,t,a):
        if t in ('script','style'): self.skip+=1
    def handle_endtag(self,t):
        if t in ('script','style'): self.skip-=1
    def handle_data(self,d):
        if not self.skip: self.text.append(d)
def norm(s): return ' '.join(html.unescape(s).split()).casefold()
def nodes(d):
    if isinstance(d,list):
        for x in d: yield from nodes(x)
    elif isinstance(d,dict):
        yield d
        if '@graph' in d: yield from nodes(d['@graph'])
for f in sorted(root.rglob('*.html')):
    if any(x in f.relative_to(root).parts for x in ('.git','node_modules')): continue
    s=f.read_text(); p=Visible(); p.feed(s); visible=norm(' '.join(p.text))
    for m in re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',s,re.S):
        for n in nodes(json.loads(m[1])):
            if n.get('@type')!='FAQPage': continue
            total+=1; missing=[]
            for q in n.get('mainEntity',[]):
                question=q.get('name','');answer=q.get('acceptedAnswer',{}).get('text','')
                if norm(question) not in visible: missing.append({'field':'question','text':question})
                if norm(answer) not in visible: missing.append({'field':'answer','text':answer})
            if missing: findings.append({'path':str(f.relative_to(root)),'missingVisibleFields':missing})
result={'FAQNodes':total,'unsupportedFAQNodes':len(findings),'pages':findings,'method':'Normalized text containment outside script/style; screen for source review, not Google validation.'}
print(json.dumps(result,indent=2));
if findings: raise SystemExit('FAQ markup must match visible questions and answers.')
