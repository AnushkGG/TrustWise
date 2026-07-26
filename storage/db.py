import hashlib
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def init_db() -> None:
    """Initialize trusted content storage table."""
    conn = sqlite3.connect(Config.DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trusted_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                query_key TEXT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                url TEXT,
                published_at TEXT,
                content_type TEXT,
                trust_score REAL,
                content_hash TEXT UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )

        # Backward-compatible migration for existing DBs created before query_key.
        cols = [row[1] for row in conn.execute("PRAGMA table_info(trusted_items)").fetchall()]
        if "query_key" not in cols:
            conn.execute("ALTER TABLE trusted_items ADD COLUMN query_key TEXT")
        if "journal" not in cols:
            conn.execute("ALTER TABLE trusted_items ADD COLUMN journal TEXT")
        if "citation_count" not in cols:
            conn.execute("ALTER TABLE trusted_items ADD COLUMN citation_count INTEGER DEFAULT 0")
        if "keywords" not in cols:
            conn.execute("ALTER TABLE trusted_items ADD COLUMN keywords TEXT")

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_trusted_items_query_key_created_at "
            "ON trusted_items(query_key, created_at DESC)"
        )
        conn.commit()
    finally:
        conn.close()


def save_trusted_items(items: List[Dict[str, Any]], query: str) -> Dict[str, int]:
    """Persist trusted items and skip duplicates by content hash."""
    if not items:
        return {"inserted": 0, "skipped": 0}

    init_db()

    inserted = 0
    skipped = 0
    query_key = _build_query_key(query)
    conn = sqlite3.connect(Config.DB_PATH)

    try:
        for item in items:
            title = (item.get("title") or "").strip()
            content = (item.get("content") or "").strip()
            source = item.get("source")
            url = item.get("url")
            published_at = item.get("published_at")
            content_type = item.get("content_type")
            trust_score = (item.get("trust") or {}).get("score")
            
            # Additional metadata fields
            journal = item.get("journal") or ""
            citation_count = int(item.get("citation_count") or 0)
            kws = item.get("keywords") or []
            keywords = ",".join(kws) if isinstance(kws, list) else str(kws)

            if not title or not content:
                skipped += 1
                continue

            content_hash = _build_content_hash(title, url or "", content)

            try:
                conn.execute(
                    """
                    INSERT INTO trusted_items (
                        query, query_key, title, content, source, url, published_at,
                        content_type, trust_score, content_hash, created_at,
                        journal, citation_count, keywords
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        query,
                        query_key,
                        title,
                        content,
                        source,
                        url,
                        published_at,
                        content_type,
                        trust_score,
                        content_hash,
                        datetime.utcnow().isoformat(),
                        journal,
                        citation_count,
                        keywords,
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                skipped += 1

        conn.commit()
    finally:
        conn.close()

    logger.info("[Storage] Saved trusted items: inserted=%s skipped=%s", inserted, skipped)
    return {"inserted": inserted, "skipped": skipped}


def get_cached_trusted_items(query: str, min_items: int = 3, limit: int = 8) -> List[Dict[str, Any]]:
    """Return cached trusted items for the same normalized query only."""
    init_db()

    query_key = _build_query_key(query)
    if not query_key:
        return []

    normalized_query = _normalize_query(query)
    sql = (
        "SELECT title, content, source, url, published_at, content_type, trust_score, created_at, "
        "journal, citation_count, keywords "
        "FROM trusted_items "
        "WHERE query_key = ? OR LOWER(query) = ? "
        "ORDER BY created_at DESC LIMIT ?"
    )
    params: List[Any] = [query_key, normalized_query, limit]

    conn = sqlite3.connect(Config.DB_PATH)
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    if len(rows) < min_items:
        return []

    cached = []
    for row in rows:
        cached.append(
            {
                "title": row[0],
                "content": row[1],
                "source": row[2],
                "url": row[3],
                "published_at": row[4],
                "content_type": row[5],
                "trust": {
                    "score": float(row[6] or 0.0),
                    "trusted": True,
                    "duplicate": False,
                    "domain": "",
                    "reasons": ["Served from trusted local cache"],
                    "relevance": 1.0,
                },
                "cached_at": row[7],
                "journal": row[8] or "",
                "citation_count": int(row[9] or 0),
                "keywords": [k.strip() for k in (row[10] or "").split(",") if k.strip()] if row[10] else [],
            }
        )

    logger.info("[Storage] Cache hit with %s records for exact query '%s'", len(cached), query)
    return cached


def _build_content_hash(title: str, url: str, content: str) -> str:
    base = f"{title.lower()}::{url.lower()}::{content[:500].lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _extract_terms(query: str) -> List[str]:
    stop = {"tell", "me", "about", "latest", "recent", "find", "get", "show", "the", "a", "an", "on", "in", "for"}
    words = re.findall(r"[a-zA-Z0-9]+", query.lower())
    return [w for w in words if len(w) > 2 and w not in stop]


def _normalize_query(query: str) -> str:
    return " ".join(re.findall(r"[a-zA-Z0-9]+", (query or "").lower())).strip()


def _build_query_key(query: str) -> str:
    terms = _extract_terms(query)
    if not terms:
        return ""
    canonical = " ".join(sorted(set(terms)))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
