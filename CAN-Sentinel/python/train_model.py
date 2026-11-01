#!/usr/bin/env python3
"""Train Isolation Forest from a synthetic normal-traffic baseline."""
import argparse
import os
import random
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from features import FEATURE_NAMES

def make_baseline(rows=5000, seed=42):
    rng = random.Random(seed)
    data = []
    # Approximate per-ID traffic timing from the virtual normal traffic generator.
    for _ in range(rows):
        choice = rng.random()
        if choice < 0.55:
            rate, delta, dlc, entropy = rng.gauss(52, 5), abs(rng.gauss(20, 3)), 8, rng.uniform(1.5, 3.0)
        elif choice < 0.78:
            rate, delta, dlc, entropy = rng.gauss(20, 3), abs(rng.gauss(50, 7)), 8, rng.uniform(0.5, 2.0)
        elif choice < 0.90:
            rate, delta, dlc, entropy = rng.gauss(5, 1), abs(rng.gauss(200, 25)), 8, rng.uniform(0.3, 1.5)
        else:
            rate, delta, dlc, entropy = rng.gauss(10, 2), abs(rng.gauss(100, 12)), 8, rng.uniform(0.1, 1.2)
        data.append([max(0, rate), delta, dlc, entropy])
    return pd.DataFrame(data, columns=FEATURE_NAMES)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='models/isolation_forest.joblib')
    ap.add_argument('--rows', type=int, default=5000)
    ap.add_argument('--csv', help='Optional feature CSV with the four feature columns')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    df = pd.read_csv(args.csv) if args.csv else make_baseline(args.rows)
    missing = [c for c in FEATURE_NAMES if c not in df.columns]
    if missing:
        raise SystemExit(f'Missing feature columns: {missing}')
    X = df[FEATURE_NAMES].replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy()
    model = IsolationForest(n_estimators=150, contamination=0.03, random_state=42)
    model.fit(X)
    joblib.dump({'model': model, 'feature_names': FEATURE_NAMES, 'trained_at': time.time()}, args.output)
    df.to_csv('data/baseline_features.csv', index=False)
    print(f'Trained IsolationForest on {len(df)} baseline rows. Saved: {args.output}')
    print('Note: default baseline is synthetic; replace it with representative normal captures before evaluating accuracy.')

if __name__ == '__main__':
    main()
