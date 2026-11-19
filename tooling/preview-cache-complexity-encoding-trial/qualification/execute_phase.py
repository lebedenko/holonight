#!/usr/bin/env python3
"""Startup interface requiring writable-provider qualification before any commands."""
import argparse
from pathlib import Path
import sys
import execute as base
base.v=base.e.load('directional_startup_verifier',base.c.DIRECTORY/'offline/verify_execution_phase.py')
execute=base.execute

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--built',type=Path,required=True)
    parser.add_argument('--correctness',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--authenticate',action='store_true')
    args=parser.parse_args()
    try: result=execute(args.built.absolute(),args.correctness.absolute(),args.output.absolute(),args.authenticate)
    except base.ERRORS as error:
        print('No attempt created: '+str(error),file=sys.stderr)
        sys.exit(1)
    print(base.h.json.dumps(result,indent=2))
    sys.exit(result['status']!='complete')
