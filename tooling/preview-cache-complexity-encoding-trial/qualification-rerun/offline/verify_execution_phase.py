#!/usr/bin/env python3
"""Startup verification gated on writable-provider correctness and 130 fresh cases."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import contract as t
h=t.h
base=t.e.load('directional_execution_base',t.DIRECTORY/'offline/verify_execution.py')
protocol=base.protocol
verify_schedule=base.verify_schedule
observation=base.observation


def prerequisite(built,correctness):
    h.require(built==t.BUILT and correctness==t.CORRECTNESS,'fixed startup prerequisites')
    t.phase_proof(built,'built')
    verifier=t.e.load('directional_correctness_phase',t.DIRECTORY/'offline/verify_correctness_phase.py')
    proof=verifier.verify(correctness)
    record=correctness.with_name(correctness.name+'-independent.json')
    h.require(h.read(record)==proof and proof['status']=='passed' and proof['outcome']=='qualified' and
        proof['required_cases_passed']==130 and proof['completed_commands']==72 and proof['failed_command'] is None,
        'fresh independently verified provider and 130-case correctness required')
    return dict(historical=t.prerequisite(),built=dict(path=str(built),seal=h.digest(built/'seal.json')),
        correctness=dict(path=str(correctness),seal=h.digest(correctness/'seal.json'),independent_sha256=h.digest(record)))


base.prerequisite=prerequisite


def verify(root):
    result=base.verify(root)
    result['phase_verifier_sha256']=h.digest(Path(__file__))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    h.require(not args.output.exists() and not args.output.is_relative_to(args.evidence),'proof collision')
    try: result=verify(args.evidence.absolute())
    except (OSError,ValueError,KeyError,TypeError) as error:
        result=dict(status='failed',decision='Evidence insufficient',failure=str(error))
    h.write(args.output,result)
    print(h.json.dumps(result,indent=2))
    sys.exit(result['status']!='passed')
