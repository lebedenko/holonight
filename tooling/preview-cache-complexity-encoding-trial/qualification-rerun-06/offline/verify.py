#!/usr/bin/env python3
"""Reuse the unchanged, independently verified preparation/build evidence."""
from pathlib import Path
import pwd
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import contract as t


def verify(root):
    original=t.e.load('retained_build_contract',t.DIRECTORY.parent/'qualification/contract.py')
    owner=root.stat().st_uid
    account=pwd.getpwuid(owner)
    original.environment=lambda: dict(PATH='/usr/bin:/bin',HOME=account.pw_dir,LANG='C.UTF-8',
        QT_QPA_PLATFORM='offscreen',CMAKE_BUILD_PARALLEL_LEVEL='4',XDG_RUNTIME_DIR='/run/user/'+str(owner),
        DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/'+str(owner)+'/bus')
    previous=sys.modules.get('contract')
    sys.modules['contract']=original
    try:
        verifier=t.e.load('retained_build_verifier',original.DIRECTORY/'offline/verify.py')
        return verifier.verify(root)
    finally:
        if previous is None: sys.modules.pop('contract',None)
        else: sys.modules['contract']=previous

# The startup verifier also consumes the retained linkage and loaded-image checks.
support=t.e.load('retained_loading_support',t.DIRECTORY.parent/'qualification/offline/verify.py')
linkage=support.linkage
mapped=support.mapped
