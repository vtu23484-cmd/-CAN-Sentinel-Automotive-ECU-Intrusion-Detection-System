"""Live SocketCAN monitor with model scoring, deterministic rules and durable audit trail."""
import time, uuid, os, joblib, can, socket, json
from features import FeatureBuilder, FEATURE_NAMES
from ecu_map import describe
from event_store import EventStore

class LiveDetector:
    def __init__(self, interface='vcan0', model_path='models/isolation_forest.joblib', store_path='data/can_sentinel.db'):
        if not os.path.exists(model_path): raise FileNotFoundError(f"Model not found: {model_path}. Run python3 python/train_model.py")
        bundle=joblib.load(model_path)
        if bundle.get('feature_names') != FEATURE_NAMES: raise ValueError('Model feature schema mismatch. Retrain using this project version.')
        self.model=bundle['model']; self.interface=interface; self.features=FeatureBuilder(); self.store=EventStore(store_path)
        self.session_id=str(uuid.uuid4())
        self.last_alert_at={}
    def run(self,on_frame=None,on_alert=None,stop_event=None):
        # Windows-compatible simulation transport uses localhost UDP. Real SocketCAN
        # remains available on Linux by passing --interface vcan0.
        bus=None; udp=None
        if self.interface.lower() in ('sim', 'udp', 'windows-sim'):
            udp=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp.bind(('127.0.0.1', 37000)); udp.settimeout(0.25)
        else:
            bus=can.Bus(interface='socketcan',channel=self.interface)
        try:
            while stop_event is None or not stop_event.is_set():
                if udp is not None:
                    try:
                        raw,_=udp.recvfrom(4096)
                        packet=json.loads(raw.decode('utf-8'))
                        can_id=int(packet['can_id']); data=str(packet['data']).upper(); dlc=int(packet.get('dlc', len(data)//2)); ts=float(packet.get('timestamp', time.time()))
                    except socket.timeout:
                        continue
                    except (ValueError, KeyError, UnicodeDecodeError, json.JSONDecodeError):
                        continue
                else:
                    msg=bus.recv(timeout=0.25)
                    if msg is None: continue
                    ts=time.time(); can_id=int(msg.arbitration_id); data=bytes(msg.data).hex().upper(); dlc=int(msg.dlc)
                frame={'timestamp':ts,'session_id':self.session_id,'interface':self.interface,'can_id':can_id,'can_id_hex':f'{can_id:03X}','dlc':dlc,'data':data}
                feat=self.features.transform(frame)
                score=float(self.model.decision_function([feat])[0]); prediction=int(self.model.predict([feat])[0])
                reasons=self._rule_reasons(frame,feat)
                is_anomaly=(prediction == -1) or bool(reasons)
                ecu=describe(can_id)
                record={**frame,'id_rate_1s':float(feat[0]),'interarrival_ms':float(feat[1]),'payload_entropy':float(feat[3]),'anomaly_score':score,'is_anomaly':is_anomaly,'suspected_ecu':ecu}
                self.store.add_frame(record)
                if on_frame: on_frame(record)
                if is_anomaly:
                    reason='; '.join(reasons) if reasons else 'Isolation Forest baseline deviation'
                    severity='CRITICAL' if feat[0] >= 500 or feat[1] < 1 else ('HIGH' if reasons else 'MEDIUM')
                    alert={**frame,'suspected_ecu':ecu,'anomaly_score':score,'severity':severity,'reason':reason,'data':data}
                    alert=self.store.upsert_alert(alert)
                    # UI receives only newly opened alerts; repeated events are counted in DB.
                    if on_alert and not alert['deduplicated']: on_alert(alert)
        finally:
            if bus is not None: bus.shutdown()
            if udp is not None: udp.close()
    @staticmethod
    def _rule_reasons(frame,feat):
        rate,delta,dlc,entropy=feat; reasons=[]
        if rate >= 100: reasons.append(f'Per-ID burst rate ({rate:.0f} frames/s)')
        if delta > 0 and delta < 1.0: reasons.append(f'Inter-arrival below 1 ms ({delta:.2f} ms)')
        if dlc > 8: reasons.append(f'Invalid classic CAN DLC ({dlc})')
        if frame['can_id'] not in range(0x800) and entropy >= 3.0: reasons.append('High payload entropy')
        return reasons
