"""Resume bounded public model searches, sequential per source and parallel across sources.
Use prepare_catalog_import.py to review/mirror covers before applying the Go import.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from photobook_worker import collect
models={'吳元元':['吳元元','吳婕安','元元'],'林襄':['林襄'],'張雅涵':['張雅涵','禾羽','Kimi'],'林莎':['林莎','Super Lisa'],'峮峮':['峮峮','吳函峮'],'瑟七':['瑟七','Seul7']}
import argparse
parser=argparse.ArgumentParser(description='Search Taiwan photobook models, retaining resumable source results')
parser.add_argument('--output',required=True)
parser.add_argument('--model-file',help='JSON object mapping verified model names to aliases')
parser.add_argument('--models',nargs='*')
parser.add_argument('--sources',nargs='*',default=['bookwalker-tw','readmoo-tw','ruten-tw','yahoo-tw'])
parser.add_argument('--max-detail-pages',type=int,default=14)
args=parser.parse_args()
if args.model_file: models.update(json.loads(Path(args.model_file).read_text(encoding='utf-8-sig')))
if args.models and any(name not in models for name in args.models): parser.error('Every requested model must exist in the model registry')
if args.max_detail_pages < 1: parser.error('--max-detail-pages must be positive')
if args.models: models={name:models[name] for name in args.models}
path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);results=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []

from concurrent.futures import ThreadPoolExecutor
import threading
lock=threading.Lock()
sources=[('bookwalker-tw','digital_store',['www.bookwalker.com.tw']),('readmoo-tw','digital_store',['readmoo.com']),('pubu-tw','digital_store',['www.pubu.com.tw']),('ruten-tw','marketplace',['www.ruten.com.tw','pub.ruten.com.tw']),('yahoo-tw','marketplace',['tw.bid.yahoo.com'])]
if any(sid not in {source[0] for source in sources} for sid in args.sources): parser.error('Unknown discovery source')
sources=[source for source in sources if source[0] in args.sources]
def run_source(spec, phase):
 sid,kind,hosts=spec
 for model in phase:
  names=models[model]
  if any(r['model']==model and r['request']['sourceId']==sid for r in results):continue
  fmt='digital' if kind=='digital_store' else 'physical'
  job={'sourceId':sid,'operation':'active_discovery','query':model if fmt=='digital' else model+' 寫真','format':fmt,'humanModelKeywords':names,'catalogModelNames':[name for aliases in models.values() for name in aliases],'fetchDetails':True,'maxPages':2,'maxDetailPages':args.max_detail_pages if fmt=='digital' else 6,'maxItems':20,'skipBlockedDetails':True,'source':{'id':sid,'kind':kind,'region':'TW','allowedHosts':hosts,'allowedFormats':[fmt],'defaultFormat':fmt,'ratePerMinute':6}}
  try:entry={'model':model,'request':job,'batch':collect(job)}
  except Exception as e:entry={'model':model,'request':job,'error':str(e)}
  with lock:
   results.append(entry);path.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
  print(json.dumps({'model':model,'source':sid,'items':len(entry.get('batch',{}).get('items',[])),'hasMore':entry.get('batch',{}).get('hasMore'),'error':entry.get('error')},ensure_ascii=False),flush=True)
# Keep each host serial without making faster sources wait for a blocked host.
with ThreadPoolExecutor(max_workers=4) as pool:
 futures=[pool.submit(run_source,spec,list(models)) for spec in sources]
 for f in futures:f.result()
