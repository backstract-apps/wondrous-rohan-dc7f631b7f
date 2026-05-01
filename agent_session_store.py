"""
session_store.py — Scalable per-session memory storage.

Architecture:
  L1: In-process CacheMemoryStore (fast, no I/O)          ← hits first
  L2: Per-session JSON files under ./sessions/<id>.json   ← survives restarts

Per-session files:
  - Each file is tiny (one chat's history)
  - Reads/writes are fully isolated — no inter-session locking
  - Trivially shardable across machines (shard by session_id prefix)
  - Drop-in Redis upgrade: replace _load_file / _save_file with r.get / r.set

Sessions index (sessions_index.json):
  - Lightweight metadata: id, title, created_at, updated_at, message_count
  - Never contains message content — stays small always
"""

import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SESSIONS_DIR = Path("sessions")
INDEX_FILE = Path("sessions_index.json")
SESSIONS_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
#  L1: In-process LRU-ish cache (bounded to avoid unbounded memory growth)
# ──────────────────────────────────────────────────────────────────────────────

class _L1Cache:
    MAX_ENTRIES = 500           # keep the 500 most-recently-used sessions hot
    TTL_SECONDS = 3600          # evict entries older than 1 hour

    def __init__(self):
        self._lock = threading.RLock()
        self._store: Dict[str, Dict] = {}   # session_id → {data, _ts}

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            entry = self._store.get(session_id)
            if entry is None:
                return None
            if time.time() - entry["_ts"] > self.TTL_SECONDS:
                del self._store[session_id]
                return None
            entry["_ts"] = time.time()       # refresh on read (LRU touch)
            return entry["data"]

    def set(self, session_id: str, data: Dict[str, Any]) -> None:
        with self._lock:
            if len(self._store) >= self.MAX_ENTRIES and session_id not in self._store:
                # Evict the oldest entry
                oldest = min(self._store, key=lambda k: self._store[k]["_ts"])
                del self._store[oldest]
            self._store[session_id] = {"data": data, "_ts": time.time()}

    def invalidate(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)


_l1 = _L1Cache()


# ──────────────────────────────────────────────────────────────────────────────
#  L2: Per-session file store
# ──────────────────────────────────────────────────────────────────────────────

def _session_path(session_id: str) -> Path:
    # Optional: shard into subdirs for very large deployments
    # prefix = session_id[:2]
    # return SESSIONS_DIR / prefix / f"{session_id}.json"
    return SESSIONS_DIR / f"{session_id}.json"


def _load_file(session_id: str) -> Dict[str, Any]:
    path = _session_path(session_id)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_file(session_id: str, data: Dict[str, Any]) -> None:
    path = _session_path(session_id)
    # Atomic write via temp file + rename (avoids partial-write corruption)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


# ──────────────────────────────────────────────────────────────────────────────
#  Public API: load / save session agent memory
# ──────────────────────────────────────────────────────────────────────────────

def load_session_memory(session_id: str) -> Dict[str, Any]:
    """Return agent memory (input_items etc.) for a session. Cache-first."""
    cached = _l1.get(session_id)
    if cached is not None:
        return cached
    data = _load_file(session_id)
    if data:
        _l1.set(session_id, data)
    return data


def save_session_memory(session_id: str, data: Dict[str, Any]) -> None:
    """Persist agent memory for a session to L1 + L2."""
    _l1.set(session_id, data)
    _save_file(session_id, data)


# ──────────────────────────────────────────────────────────────────────────────
#  Sessions index — lightweight metadata only
# ──────────────────────────────────────────────────────────────────────────────

_index_lock = threading.RLock()


def _load_index() -> Dict[str, Any]:
    if not INDEX_FILE.exists():
        return {}
    try:
        with INDEX_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_index(index: Dict[str, Any]) -> None:
    tmp = INDEX_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    tmp.replace(INDEX_FILE)


def create_session(
    title: Optional[str] = None,
    session_id: Optional[str] = "default"
) -> Dict[str, Any]:
    """Create a new session entry; return its metadata dict."""
    # session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    meta = {
        "id": session_id,
        "title": title or "New Chat",
        "created_at": now,
        "updated_at": now,
        "message_count": 0,
    }
    with _index_lock:
        index = _load_index()
        index[session_id] = meta
        _save_index(index)
    return meta


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    with _index_lock:
        return _load_index().get(session_id)


def list_sessions() -> List[Dict[str, Any]]:
    """Return all sessions sorted newest-first."""
    with _index_lock:
        index = _load_index()
    return sorted(index.values(), key=lambda s: s["updated_at"], reverse=True)


def update_session_meta(session_id: str, title: Optional[str] = None, increment_messages: int = 0) -> None:
    """Bump updated_at and optionally update title / message count."""
    with _index_lock:
        index = _load_index()
        if session_id not in index:
            return
        meta = index[session_id]
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()
        if title:
            meta["title"] = title
        meta["message_count"] = meta.get("message_count", 0) + increment_messages
        index[session_id] = meta
        _save_index(index)


def delete_session(session_id: str) -> bool:
    """Remove session from index and delete its file + L1 cache."""
    with _index_lock:
        index = _load_index()
        if session_id not in index:
            return False
        del index[session_id]
        _save_index(index)
    _l1.invalidate(session_id)
    path = _session_path(session_id)
    if path.exists():
        path.unlink()
    return True


# ──────────────────────────────────────────────────────────────────────────────
#  Chat message log (human-readable, separate from agent input_items)
# ──────────────────────────────────────────────────────────────────────────────

def get_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """Return the human-readable message list for a session."""
    data = _load_file(session_id)
    return data.get("messages", [])


def append_message(session_id: str, role: str, content: str) -> None:
    """Append a user or assistant message to the readable history."""
    path = _session_path(session_id)
    data = _load_file(session_id)
    messages = data.get("messages", [])
    messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    data["messages"] = messages
    _save_file(session_id, data)
    _l1.invalidate(session_id)   # invalidate so next load picks up merged state