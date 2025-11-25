"""
alert_manager.py
Priority alert queue and helper to persist alerts.

Data structures:
- in-memory heap (list used with heapq) storing (-severity, timestamp, id, message)
Time complexity:
- pushAlert: O(log A)
- popTop: O(log A)
"""

import heapq
import time
from typing import Tuple, List
from database import addAlert

_alertHeap = []
_nextId = 1


def pushAlert(severity: int, message: str) -> int:
    """
    Push an alert into the in-memory heap and persist to DB.
    Returns generated alert id (simple increment).
    """
    global _nextId
    alertId = _nextId
    _nextId += 1
    timestamp = int(time.time())
    entry = (-severity, timestamp, alertId, message)
    heapq.heappush(_alertHeap, entry)
    # persist
    addAlert(alertId, severity, timestamp, message)
    return alertId


def topAlerts(limit: int = 20) -> List[Tuple[int, int, int, str]]:
    """
    Return top `limit` alerts (sorted by severity descending, then timestamp descending)
    without popping them.
    Time complexity: O(A log A) if building sorted list but we will use nlargest for efficiency O(A + k log A)
    """
    import heapq as _hq
    top = _hq.nsmallest(limit, _alertHeap)
    # convert back to readable tuples (id, severity, timestamp, message)
    return [(entry[2], -entry[0], entry[1], entry[3]) for entry in top]


def popTop():
    """
    Pop top alert (highest severity).
    """
    if not _alertHeap:
        return None
    entry = heapq.heappop(_alertHeap)
    return (entry[2], -entry[0], entry[1], entry[3])
