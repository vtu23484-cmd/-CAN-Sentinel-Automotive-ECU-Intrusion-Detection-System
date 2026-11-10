import os,sys,tempfile,unittest
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','python'))
from features import payload_entropy,FeatureBuilder
from event_store import EventStore
class FeatureTests(unittest.TestCase):
 def test_empty_entropy(self): self.assertEqual(payload_entropy(''),0.0)
 def test_constant_payload_entropy(self): self.assertEqual(payload_entropy('00000000'),0.0)
 def test_high_entropy_positive(self): self.assertGreater(payload_entropy('0011223344556677'),0.0)
 def test_feature_shape(self): self.assertEqual(len(FeatureBuilder().transform({'timestamp':100,'can_id':1,'dlc':8,'data':'0011223344556677'})),4)
 def test_rate_is_per_can_id(self):
  b=FeatureBuilder(); b.transform({'timestamp':1,'can_id':1,'dlc':1,'data':'00'}); f=b.transform({'timestamp':1.1,'can_id':2,'dlc':1,'data':'00'}); self.assertEqual(f[0],1.0); self.assertEqual(f[1],0.0)
 def test_store_persists_frame_and_deduplicates_alert(self):
  with tempfile.TemporaryDirectory() as d:
   s=EventStore(os.path.join(d,'test.db')); r={'timestamp':1,'session_id':'s','interface':'vcan0','can_id':1,'can_id_hex':'001','dlc':1,'data':'00','id_rate_1s':1,'interarrival_ms':0,'payload_entropy':0,'anomaly_score':-0.1,'is_anomaly':True,'suspected_ecu':'test'}; s.add_frame(r)
   a={**r,'severity':'HIGH','reason':'burst'}; self.assertFalse(s.upsert_alert(a)['deduplicated']); a['timestamp']=2; self.assertTrue(s.upsert_alert(a)['deduplicated'])
if __name__=='__main__': unittest.main()
