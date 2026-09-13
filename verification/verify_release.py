"""Verify source-byte recovery and atlas structure; optionally replay bundled checks."""
from pathlib import Path
import argparse, collections, hashlib, json, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'atlas'
def sha(b): return hashlib.sha256(b).hexdigest()
def verify():
    recovery=json.loads((ROOT/'verification/source-recovery.json').read_text(encoding='utf-8'))
    for f in recovery['files']:
        b=(ROOT/f['public_path']).read_bytes()
        assert len(b)==f['bytes'] and sha(b)==f['sha256'], f['public_path']
    manifest_count=0
    for line in (ATLAS/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        expected,name=line.split(None,1); p=(ATLAS/name.lstrip('*')).resolve()
        assert p.is_relative_to(ATLAS.resolve())
        assert sha(p.read_bytes())==expected
        manifest_count+=1
    rows=json.loads((ATLAS/'brouwer-ground-truth.json').read_text(encoding='utf-8'))['records']
    assert len(rows)==len({tuple(r['params']) for r in rows})==119
    assert collections.Counter(r['status'] for r in rows)=={'EXISTS':91,'NONE':28}
    edges=[json.loads(s) for s in (ATLAS/'verified-edges.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
    assert len(edges)==len({(e['from'],e['to'],e['rule']) for e in edges})==141
    assert all(e['from']!=e['to'] for e in edges)
    endpoints=sorted({e[k] for e in edges for k in ('from','to')})
    assert len(endpoints)==211
    assert json.loads((ROOT/'data/endpoints.json').read_text(encoding='utf-8'))['endpoints']==endpoints
    transports=json.loads((ATLAS/'verification-output.json').read_text(encoding='utf-8'))['transports']
    assert len(transports)==8 and sum(t['oneSided'] for t in transports)==6
    assert sum(len(t['agreements']) for t in transports)==162
    assert sum(len(t['disagreements']) for t in transports)==0
    assert len(recovery['files'])==25 and manifest_count==24
    return {'ok':True,'source_files':25,'manifest_entries':24,'rows':119,'exists':91,'none':28,'edges':141,'endpoints':211,'transports':8,'one_sided_transports':6,'recorded_comparisons':162,'recorded_disagreements':0}
def replay():
    results=[]
    for name,args in [('srg_transports.py',['--no-write']),('independent_check.py',[]),('connectivity_impact.py',[])]:
        p=subprocess.run([sys.executable,str(ATLAS/name),*args],cwd=ATLAS,capture_output=True,text=True,timeout=300)
        final=json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else {}
        assert p.returncode==0 and final.get('ok') is True, (name,p.returncode,p.stderr,p.stdout)
        results.append({'script':'atlas/'+name,'arguments':args,'exit_code':p.returncode,'receipt':final,'stdout':p.stdout,'stderr':p.stderr})
    return results
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--replay',action='store_true');parser.add_argument('--receipt',type=Path);args=parser.parse_args()
    result=verify()
    if args.replay:
        result['replay']=replay();verify()
    if args.receipt:
        args.receipt.parent.mkdir(parents=True,exist_ok=True)
        args.receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='replay'},sort_keys=True))
