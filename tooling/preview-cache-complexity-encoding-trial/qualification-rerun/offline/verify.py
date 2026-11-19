#!/usr/bin/env python3
"""Reuse the unchanged, independently verified preparation/build evidence."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import contract as t


def verify(root):
    original=t.e.load('retained_build_contract',t.DIRECTORY.parent/'qualification/contract.py')
    previous=sys.modules.get('contract')
    sys.modules['contract']=original
    try:
        verifier=t.e.load('retained_build_verifier',original.DIRECTORY/'offline/verify.py')
        return verifier.verify(root)
    finally:
        if previous is None: sys.modules.pop('contract',None)
        else: sys.modules['contract']=previous
