#!/usr/bin/env python3
"""Reuse the unchanged attempt-05 qualification and its original verifier context."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import contract as t


def verify(root):
    directory=t.DIRECTORY.parent/'qualification-rerun-05'
    original=t.e.load('retained_correctness_contract',directory/'contract.py')
    previous=sys.modules.get('contract')
    sys.modules['contract']=original
    try:
        verifier=t.e.load('retained_correctness_verifier',directory/'offline/verify_correctness_phase.py')
        return verifier.verify(root)
    finally:
        if previous is None: sys.modules.pop('contract',None)
        else: sys.modules['contract']=previous
