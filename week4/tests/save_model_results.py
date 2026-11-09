import json
from pathlib import Path

from test_model_comparison import results

output = Path("week4/results/model_comparison.json")
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w") as file:
    json.dump(results, file, indent=4)

print(f"\n[SUCCESS] Results saved to {output}")
