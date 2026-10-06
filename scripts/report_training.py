"""Write a small progress file from a local or cloud training loop."""
import argparse
import json
from pathlib import Path


def report(path, current, total, loss=None, state='executing'):
    # Use a persistent directory on cloud runners, then sync this file to the PC.
    target=Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    data={'state':state, 'current':current, 'total':total}
    if loss is not None: data['loss']=loss
    temporary=target.with_suffix('.tmp')
    temporary.write_text(json.dumps(data),encoding='utf-8')
    temporary.replace(target)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path'); parser.add_argument('current',type=int); parser.add_argument('total',type=int)
    parser.add_argument('--loss',type=float); parser.add_argument('--state',choices=['executing','idle','error'],default='executing')
    args=parser.parse_args(); report(args.path,args.current,args.total,args.loss,args.state)
