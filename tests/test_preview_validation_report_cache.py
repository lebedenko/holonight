import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_preview_validation as base
import test_preview_delivery_scheduler as scheduler

a=base.a
ROOT=base.ROOT


class OfflineReplayCacheTests(unittest.TestCase):
    setUp=base.ValidationPreparationTests.setUp

    def test_indexed_scheduler_windows_match_full_scan_and_json_roundtrip(self):
        capture=scheduler.SchedulerTests.capture(self);clock=capture['clock']
        selected=[dict(operation='runtime',start=left,stop=right,begin=dict(pid=1,tid=2,span=index))
                  for index,(left,right) in enumerate(((5,35),(10,20),(30,40),(0,100)),1)]
        prepared=a.scheduler_evidence(capture,clock)
        actual=a.scheduler_windows(selected,capture,clock,prepared)
        timelines,issues=a.r.r.a.scheduler(capture,clock)
        expected=[]
        for span in selected:
            key=(1,2,1);left,right=span['start'],span['stop'];timeline=timelines[key]
            establishing={r['start_ns'] for r in timeline if r['start_ns']<right and r['stop_ns']>left}
            transitions=[e for e in capture['events'] if any(tuple(e.get(field,()))==key for field in ('prev','next','task'))
                         and e['ns']<=right and (e['ns']>=left or e['ns'] in establishing)]
            expected.append(dict(span=span['begin']['span'],task=list(key),operation=span['operation'],start_ns=left,stop_ns=right,
                                 **a.r.r.a.clipped(timeline,left,right),transitions=transitions))
        self.assertEqual(actual,dict(windows=expected,issues=issues))
        self.assertEqual(actual,json.loads(json.dumps(actual)))
        self.assertEqual(actual,a.scheduler_windows(selected,capture,clock))
        with self.assertRaises(ValueError): a.scheduler_windows(selected,copy.deepcopy(capture),clock,prepared)
        with self.assertRaises(ValueError): a.scheduler_windows(selected,capture,dict(name='other'),prepared)

    def test_indexed_transitions_preserve_ties_and_do_not_duplicate_self_switches(self):
        capture=scheduler.SchedulerTests.capture(self);clock=capture['clock']
        # Multiple establishing wakeups at one timestamp remain distinct records.
        capture['events'].insert(2,dict(capture['events'][1]))
        capture['events'].append(dict(kind='switch',ns=40,cpu=0,prev=[1,2,1],next=[1,2,1],prev_state='runnable'))
        selected=[dict(operation='runtime',start=left,stop=right,begin=dict(pid=1,tid=2,span=index))
                  for index,(left,right) in enumerate(((25,35),(35,45)),1)]
        value=a.scheduler_windows(selected,capture,clock)
        self.assertEqual([e['ns'] for e in value['windows'][0]['transitions']],[20,20,30])
        self.assertEqual([e['ns'] for e in value['windows'][1]['transitions']],[30,40])

    def test_cached_citations_match_historical_checks_and_reject_conflicting_duplicates(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            path=Path(temp)/'raw.stderr'
            path.write_text('DELIVERY {"operation":"x","ns":1}\nTRACE {"a":2}\n')
            one=dict(file=str(path),line=1,operation='x',ns=1)
            two=dict(file=str(path),line=2,text='TRACE {"a":2}')
            value=[one,dict(nested=[two,one]),two]
            expected=a.p.b.s.raw_citations(value)
            reads=[];original=Path.read_text
            def read_text(item,*args,**kwargs):
                reads.append(str(item));return original(item,*args,**kwargs)
            with patch.object(Path,'read_text',read_text): actual=a.raw_citations(value)
            self.assertEqual(actual,expected)
            self.assertEqual(reads,[str(path)])
            for bad in (dict(one,ns=2),dict(two,text='wrong'),dict(one,line=True),dict(one,line=0)):
                with self.subTest(bad=bad),self.assertRaises(ValueError): a.raw_citations([one,bad])

    def test_cached_citations_refuse_symlink_sources(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp);(root/'raw').write_text('line\n');(root/'link').symlink_to(root/'raw')
            with self.assertRaises(ValueError): a.raw_citations([dict(file=str(root/'link'),line=1,text='line')])


if __name__=='__main__': unittest.main()
