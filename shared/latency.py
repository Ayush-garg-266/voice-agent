import time
import numpy as np
from typing import List, Dict, Any

class LatencyTracker:
    def __init__(self):
        self.measurements: Dict[str, List[float]] = {}

    def record(self, component: str, duration_ms: float):
        if component not in self.measurements:
            self.measurements[component] = []
        self.measurements[component].append(duration_ms)

    def get_stats(self, component: str) -> Dict[str, float]:
        data = self.measurements.get(component, [])
        if not data:
            return {"count": 0, "p50": 0.0, "p95": 0.0, "mean": 0.0}
        return {
            "count": len(data),
            "p50": float(np.percentile(data, 50)),
            "p95": float(np.percentile(data, 95)),
            "mean": float(np.mean(data))
        }

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        return {comp: self.get_stats(comp) for comp in self.measurements}
