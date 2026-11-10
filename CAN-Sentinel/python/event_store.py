"""Durable local event store (SQLite WAL); suitable for lab/pilot use."""
import json, sqlite3, threading, os
from pathlib import Path

class EventStore:
    def __init__(self, path="data/can_sentinel.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.Lock()
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA foreign_keys=ON")
            db.executescript("""
            CREATE TABLE IF NOT EXISTS frames (
              id INTEGER PRIMARY KEY AUTOINCREMENT, event_time REAL NOT NULL,
              session_id TEXT NOT NULL, interface TEXT NOT NULL, can_id INTEGER NOT NULL,
              can_id_hex TEXT NOT NULL, dlc INTEGER NOT NULL, data TEXT NOT NULL,
              id_rate_1s REAL NOT NULL, interarrival_ms REAL NOT NULL,
              payload_entropy REAL NOT NULL, anomaly_score REAL NOT NULL,
              is_anomaly INTEGER NOT NULL, suspected_ecu TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_frames_time ON frames(event_time);
            CREATE INDEX IF NOT EXISTS idx_frames_canid_time ON frames(can_id,event_time);
            CREATE TABLE IF NOT EXISTS alerts (
              id INTEGER PRIMARY KEY AUTOINCREMENT, alert_key TEXT NOT NULL,
              first_seen REAL NOT NULL, last_seen REAL NOT NULL, session_id TEXT NOT NULL,
              interface TEXT NOT NULL, can_id INTEGER NOT NULL, can_id_hex TEXT NOT NULL,
              suspected_ecu TEXT NOT NULL, severity TEXT NOT NULL, reason TEXT NOT NULL,
              anomaly_score REAL NOT NULL, occurrence_count INTEGER NOT NULL DEFAULT 1,
              status TEXT NOT NULL DEFAULT 'OPEN', sample_data TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_alerts_status_time ON alerts(status,last_seen);
            """)
    def _connect(self):
        db=sqlite3.connect(self.path, timeout=10)
        db.row_factory=sqlite3.Row
        return db
    def add_frame(self, r):
        with self._lock, self._connect() as db:
            db.execute("""INSERT INTO frames(event_time,session_id,interface,can_id,can_id_hex,dlc,data,id_rate_1s,interarrival_ms,payload_entropy,anomaly_score,is_anomaly,suspected_ecu)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""", (r['timestamp'],r['session_id'],r['interface'],r['can_id'],r['can_id_hex'],r['dlc'],r['data'],r['id_rate_1s'],r['interarrival_ms'],r['payload_entropy'],r['anomaly_score'],int(r['is_anomaly']),r['suspected_ecu']))
    def upsert_alert(self, a, cooldown_seconds=10):
        key=f"{a['interface']}:{a['can_id']}:{a['reason']}"
        with self._lock, self._connect() as db:
            row=db.execute("SELECT id,last_seen FROM alerts WHERE alert_key=? AND status='OPEN' ORDER BY id DESC LIMIT 1",(key,)).fetchone()
            if row and a['timestamp']-row['last_seen'] <= cooldown_seconds:
                db.execute("UPDATE alerts SET last_seen=?,occurrence_count=occurrence_count+1,anomaly_score=MIN(anomaly_score,?),sample_data=? WHERE id=?",(a['timestamp'],a['anomaly_score'],a['data'],row['id']))
                a['deduplicated']=True
            else:
                db.execute("""INSERT INTO alerts(alert_key,first_seen,last_seen,session_id,interface,can_id,can_id_hex,suspected_ecu,severity,reason,anomaly_score,sample_data)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(key,a['timestamp'],a['timestamp'],a['session_id'],a['interface'],a['can_id'],a['can_id_hex'],a['suspected_ecu'],a['severity'],a['reason'],a['anomaly_score'],a['data']))
                a['deduplicated']=False
        return a
    def export_csv(self, table, output):
        import csv
        if table not in ('frames','alerts'): raise ValueError('Unsupported table')
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db, open(output,'w',newline='',encoding='utf-8') as f:
            cur=db.execute(f'SELECT * FROM {table} ORDER BY id')
            writer=csv.writer(f); writer.writerow([c[0] for c in cur.description]); writer.writerows(cur.fetchall())
