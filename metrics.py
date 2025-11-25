"""
metrics.py
Logic for computing bandwidth deltas and normalizing SNMP counters.

Provides:
- computeBandwidth(prevCounters, newCounters, elapsedSeconds) -> per-interface bytes/sec
- normalizeCounterDiff(prev, curr, maxCounter) -> handles 32-bit rollover

Data structures: dicts mapping device->ifIndex->counter tuples.
Time complexity: O(I) per device where I = interfaces.
"""

from typing import Dict, Tuple
import time

# typical 32-bit counter max (ifIndex counters may be 32 or 64 bit; accept max as param)
DEFAULT_32BIT_MAX = 2 ** 32


def normalizeCounterDiff(prev: int, curr: int, maxCounter: int = DEFAULT_32BIT_MAX) -> int:
    """
    Compute positive diff between two monotonically increasing counters that may have wrapped.
    """
    if curr >= prev:
        return curr - prev
    # wrapped
    return (maxCounter - prev) + curr


def computeBandwidth(prevCounters: Dict[int, Tuple[int, int]],
                     newCounters: Dict[int, Tuple[int, int]],
                     elapsedSeconds: float,
                     counterMax: int = DEFAULT_32BIT_MAX) -> Dict[int, Tuple[float, float]]:
    """
    prevCounters/newCounters: {ifIndex: (in_bytes, out_bytes)}
    Returns {ifIndex: (in_bps, out_bps)} bytes per second (not bits).
    Time complexity: O(I) where I = number of interfaces processed.
    """
    res = {}
    if elapsedSeconds <= 0:
        elapsedSeconds = 1
    for ifIndex, newVals in newCounters.items():
        prev = prevCounters.get(ifIndex, (0, 0))
        inDiff = normalizeCounterDiff(prev[0], newVals[0], counterMax)
        outDiff = normalizeCounterDiff(prev[1], newVals[1], counterMax)
        inBps = inDiff / elapsedSeconds
        outBps = outDiff / elapsedSeconds
        res[ifIndex] = (inBps, outBps)
    return res
