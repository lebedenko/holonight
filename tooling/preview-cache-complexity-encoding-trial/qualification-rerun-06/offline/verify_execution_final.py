#!/usr/bin/env python3
"""Final process-free verification, including the retained phase snapshot checks."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import contract as t
h=t.h
phase=t.e.load('final_execution_phase',t.DIRECTORY/'offline/verify_execution_phase.py')
# Use the captured original implementation for all three support contracts.
phase.base.support.tools=phase.base.support.support.tools


def verify(root):
    result=phase.verify(root)
    result['final_verifier_sha256']=h.digest(Path(__file__))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    h.require(not args.output.exists() and not args.output.is_relative_to(args.evidence),'verification collision')
    try: result=verify(args.evidence.absolute())
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as error:
        result=dict(status='failed',decision='Evidence insufficient',failure=str(error))
    h.write(args.output,result)
    print(h.json.dumps(result,indent=2))
    sys.exit(result['status']!='passed')
