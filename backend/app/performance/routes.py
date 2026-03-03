# backend/app/performance/routes.py

from fastapi import APIRouter
from ..metrics import performance_metrics

router = APIRouter(tags=["Performance"])

@router.get("/performance/stats")
async def get_performance_stats():
    if not performance_metrics:
        return {"message": "No metrics collected yet"}
        
    avg_latency = sum(m["latency"] for m in performance_metrics) / len(performance_metrics)
    status_counts = {}
    for m in performance_metrics:
        s = str(m["status"])
        status_counts[s] = status_counts.get(s, 0) + 1
        
    return {
        "count": len(performance_metrics),
        "average_latency_ms": round(avg_latency * 1000, 2),
        "status_distribution": status_counts,
        "recent_metrics": performance_metrics[-10:] # Last 10
    }
