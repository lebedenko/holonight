import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('audit',Path(__file__).resolve().parents[1]/'scripts/analyze-preview-delivery-gaps-v4.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class IntervalTests(unittest.TestCase):
    def test_overlap_clipping_and_complement(self):
        r=a.intervals(5,20,[dict(start=0,stop=8),dict(start=7,stop=10),dict(start=15,stop=30)])
        self.assertEqual(r['covered'],[[5,10],[15,20]])
        self.assertEqual(r['uncovered'],[[10,15]])
        self.assertEqual(r['covered_ns']+r['uncovered_ns'],15)
    def test_empty_and_zero_window(self):
        self.assertEqual(a.intervals(0,5,[])['uncovered'],[[0,5]])
        self.assertEqual(a.intervals(5,5,[])['uncovered'],[])
