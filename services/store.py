"""
In-process result store for medical reports.

Flask cookie sessions cannot reliably hold full report payloads.
We keep a short-lived server-side cache keyed by a session token.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import OrderedDict
from typing import Any, Dict, Optional


class ResultStore:
    def __init__(self, max_items: int = 200, ttl_seconds: int = 60 * 60 * 6) -> None:
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds
        self._items: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
        self._lock = threading.Lock()

    def put(self, payload: Dict[str, Any]) -> str:
        key = uuid.uuid4().hex
        with self._lock:
            self._items[key] = {"created": time.time(), "data": payload}
            self._items.move_to_end(key)
            self._evict()
        return key

    def get(self, key: Optional[str]) -> Optional[Dict[str, Any]]:
        if not key:
            return None
        with self._lock:
            item = self._items.get(key)
            if not item:
                return None
            if time.time() - item["created"] > self.ttl_seconds:
                self._items.pop(key, None)
                return None
            self._items.move_to_end(key)
            return item["data"]

    def _evict(self) -> None:
        now = time.time()
        expired = [k for k, v in self._items.items() if now - v["created"] > self.ttl_seconds]
        for k in expired:
            self._items.pop(k, None)
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)


result_store = ResultStore()
