"""Synthetic encoding eligibility checks; real processes are forbidden."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

DIRECTORY=Path(__file__).resolve().parents[1]/'tooling/preview-cache-encoding-trial'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
c=load('encoding_test_contract',DIRECTORY/'contract.py')
# Keep the verifier's generic import isolated from other historical suites.
old=sys.modules.get('contract')
sys.modules['contract']=c
v=load('encoding_test_verifier',DIRECTORY/'offline/verify.py')
d=load('encoding_test_controller',DIRECTORY/'run.py')
if old is None:
    sys.modules.pop('contract',None)
else:
    sys.modules['contract']=old


class EncodingTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(subprocess,'Popen',side_effect=AssertionError('real process forbidden')))
        self.enterContext(patch.object(subprocess,'run',side_effect=AssertionError('real process forbidden')))

    def raw(self):
        raw=dict(qt='6.12.0',corpus=[],rows=[])
        for identity in c.IDS:
            image=dict(id=identity,pixels='pixels',alpha=True,icc='icc')
            raw['corpus'].append(image)
            metadata={'Thumb::URI':'file:///trial/source-'+identity.rsplit('-',1)[0], 'Thumb::MTime':'1700000000',
                'Thumb::Size':'1234567','X-HoloNight::MTimeMsec':'1700000000123','Files::Revision':'encoding-trial-v1',
                'Files::OrientationPolicy':'applied-v1','X-HoloNight::OrientationPolicy':'applied-v1'}
            schedule=[(m,True,-1,0) for m in c.MODES]
            schedule += [(c.MODES[(b+offset)%3],False,b,i) for b in range(6) for offset in range(3) for i in range(5)]
            for mode,warmup,block,observation in schedule:
                raw['rows'].append(dict(image,mode=mode,warmup=warmup,block=block,observation=observation,
                    ns=100000 if warmup else 100 if mode=='default' else 50,bytes=100,sha256='sha',metadata=dict(metadata)))
        return raw

    def both(self,raw):
        result=c.assess(raw)
        self.assertEqual(result,v.summarize(raw))
        return result

    def test_rotated_schedule_warmups_and_tie_break(self):
        result=self.both(self.raw())
        self.assertEqual(result['selected'],'11')
        self.assertEqual(result['cells']['textured-256']['default']['p95'],100)

    def test_size_cap_is_exact_and_applies_to_every_image(self):
        for size,failures in ((125,[]),(126,['flat-128'])):
            raw=self.raw()
            for row in raw['rows']:
                if row['id']=='flat-128' and row['mode']=='11':
                    row['bytes']=size
            self.assertEqual(self.both(raw)['eligibility']['11']['size_failures'],failures)

    def test_no_eligible_setting_defers(self):
        raw=self.raw()
        for row in raw['rows']:
            if row['mode']!='default':
                row['bytes']=126
        self.assertEqual(self.both(raw)['decision'],'Deferred')

    def test_both_primary_statistics_must_strictly_improve(self):
        raw=self.raw()
        for mode in ('11','0'):
            measured=[r for r in raw['rows'] if r['id']=='textured-256' and r['mode']==mode and not r['warmup']]
            measured[-2]['ns']=100
            measured[-1]['ns']=100
        self.assertIsNone(self.both(raw)['selected'])

    def test_nearest_rank_p95_is_observation_29_of_30(self):
        raw=self.raw()
        rows=[r for r in raw['rows'] if r['id']=='textured-256' and r['mode']=='11' and not r['warmup']]
        for i,row in enumerate(rows): row['ns']=i+1
        self.assertEqual(self.both(raw)['cells']['textured-256']['11'],dict(bytes=100,median=15.5,p95=29))

    def test_ties_use_median_then_total_bytes_then_11(self):
        raw=self.raw()
        for row in raw['rows']:
            if row['mode']=='0': row['bytes']=99
        self.assertEqual(self.both(raw)['selected'],'0')
        for row in raw['rows']:
            if row['mode']=='0' and not row['warmup'] and row['block']<3: row['ns']=51
        self.assertEqual(self.both(raw)['selected'],'11')

    def test_malformed_interrupted_and_reordered_evidence_rejected(self):
        mutations=[lambda r:r['rows'].pop(),lambda r:r['rows'].reverse(),lambda r:r['rows'][3].update(ns=True),
            lambda r:r['rows'][3].update(ns=float('nan')),lambda r:r['rows'][3].update(pixels='changed'),
            lambda r:r['rows'][3]['metadata'].update({'Thumb::Size':'2'}),lambda r:r.update(qt='other')]
        for mutate in mutations:
            raw=self.raw(); mutate(raw)
            for assess in (c.assess,v.summarize):
                with self.assertRaises((ValueError,KeyError,TypeError)):
                    assess(raw)

    def test_source_change_preserves_commit_and_cancellation(self):
        original=(c.historical.Q/'C/source'/c.SOURCE).read_text()
        for mode in ('11','0'):
            candidate=c.transform(original,mode)
            self.assertIn('writer.setCompression('+mode+');',candidate)
            self.assertEqual(original.count('cancelled.load()'),candidate.count('cancelled.load()'))
            self.assertIn('if (!file.commit())',candidate)
            with self.assertRaises(ValueError): c.transform(candidate,mode)
        with self.assertRaises(ValueError): c.transform(original,'1')

    def test_resealed_stopped_evidence_cannot_be_accepted(self):
        with patch.object(c.h,'digest',return_value='different-resealed-inventory'):
            with self.assertRaisesRegex(ValueError,'retained stopped evidence identity changed'):
                v.verify_stopped(Path('/synthetic'),{}, {})

    def test_timeout_cannot_select_a_candidate_or_claim_cleanup(self):
        root=Path('/synthetic')
        schedule=[['build'],['compile'],['ldd'],['mapping'],[str(root/'native-build/investigate'),str(root/'corpus'),str(root/'raw.json')]]
        documents={'schedule.json':schedule,'libraries.json':{'/synthetic/library':'library'}}
        for index in range(5):
            documents[f'command-{index}.json']=dict(argv=schedule[index],cwd=str(root/'corpus'),timeout_seconds=30,environment={})
            if index<4:
                documents[f'result-{index}.json']=dict(exit=0,cleanup=True,start_ns=index*2,stop_ns=index*2+1)
        def digest(path):
            if path.name=='seal.json': return 'f7375f273dcc0d899fad9ca9ca78dd66525844a208a9a9967da10b9fabd1d58e'
            if path.name=='qpnghandler.cpp': return c.SOURCE_SHA
            return 'library'
        def read_text(path,*args,**kwargs):
            return 'PNG_LEVEL 1\nPNG_LEVEL 0\n' if path.name=='3.stderr' else 'cleanup.terminate(process,deadline=cleanup_start+5)\nos.killpg(process.pid,0)'
        with patch.object(c.h,'digest',side_effect=digest), patch.object(c.h,'read',side_effect=lambda p:documents[p.name]), patch.object(Path,'read_text',read_text):
            result=v.verify_stopped(root,dict(status='stopped',decision='Evidence insufficient',completed=4,failure='timed out after 30 seconds'),{str(c.DIRECTORY/'run.py'):'controller'})
        self.assertEqual(result['decision'],'Evidence insufficient')
        self.assertIsNone(result['selected'])
        self.assertFalse(result['complete_raw_observations'])
        self.assertEqual(result['cleanup'],'unverified: timeout result was not persisted')

    def recorded_command(self, wait_error=None, launch_error=None, cleanup_error=None, exit_code=0):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output=Path(temporary.name)
        process=SimpleNamespace(pid=12345,returncode=exit_code)
        def wait(timeout):
            self.assertEqual(timeout,300)
            if wait_error:
                process.returncode=None
                raise wait_error
            return exit_code
        process.wait=wait
        def terminate(owned,deadline):
            self.assertIs(owned,process)
            if cleanup_error:
                raise cleanup_error
            process.returncode=-15 if wait_error else exit_code
        with patch.object(subprocess,'Popen',side_effect=launch_error,return_value=process), \
                patch.object(c.historical.e,'load',return_value=SimpleNamespace(terminate=terminate)), \
                patch.object(d.os,'killpg',side_effect=ProcessLookupError):
            try:
                d.command(output,4,['synthetic-investigate'],{},300)
                raised=False
            except ValueError:
                raised=True
        result=c.h.read(output/'result-4.json')
        self.assertEqual(c.h.read(output/'command-4.json')['timeout_seconds'],300)
        self.assertEqual(v.verify_result(result,0),not raised)
        return result,raised

    def test_success_persists_owned_cleanup_and_reaping(self):
        result,raised=self.recorded_command()
        self.assertFalse(raised)
        self.assertTrue(result['cleanup'] and result['reaped'] and result['group_absent'])

    def test_timeout_persists_failure_exit_and_cleanup_before_stopping(self):
        result,raised=self.recorded_command(wait_error=subprocess.TimeoutExpired(['synthetic'],300))
        self.assertTrue(raised)
        self.assertTrue(result['timed_out'] and result['cleanup'] and result['reaped'])
        self.assertEqual(result['exit'],-15)

    def test_interrupt_persists_cleanup_without_claiming_timeout(self):
        result,raised=self.recorded_command(wait_error=KeyboardInterrupt())
        self.assertTrue(raised)
        self.assertFalse(result['timed_out'])
        self.assertEqual(result['failure'],'KeyboardInterrupt')
        self.assertTrue(result['cleanup'])

    def test_launch_failure_persists_no_owned_process(self):
        result,raised=self.recorded_command(launch_error=PermissionError('authorization denied'))
        self.assertTrue(raised)
        self.assertIsNone(result['pid'])
        self.assertFalse(result['reaped'])
        self.assertTrue(result['cleanup'] and result['group_absent'])

    def test_cleanup_failure_is_recorded_and_stops_even_after_success(self):
        result,raised=self.recorded_command(cleanup_error=ValueError('cleanup deadline'))
        self.assertTrue(raised)
        self.assertFalse(result['cleanup'])
        self.assertEqual(result['cleanup_failure'],'cleanup deadline')

    def test_nonzero_exit_stops_after_cleanup(self):
        result,raised=self.recorded_command(exit_code=9)
        self.assertTrue(raised)
        self.assertEqual(result['exit'],9)
        self.assertTrue(result['cleanup'])

    def test_fabricated_cleanup_or_success_is_rejected(self):
        result,_=self.recorded_command()
        for key,value in [('reaped',False),('group_absent',False),('cleanup_seconds',5.01),
                ('cleanup_seconds',float('nan')),('exit',None),('pid',True),('timed_out',True)]:
            with self.assertRaises(ValueError):
                v.verify_result(dict(result,**{key:value}),0)

    def test_retry_has_new_path_and_distinct_aggregate_limit(self):
        self.assertNotEqual(c.OUTPUT,c.STOPPED_OUTPUT)
        self.assertEqual(c.COMMAND_TIMEOUTS,(600,600,30,30,300))


if __name__=='__main__': unittest.main()
