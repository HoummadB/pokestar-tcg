#!/usr/bin/env python3
"""Rafraîchit les repères eBay vendu FR : ebay-sold-cache.json.

Phase prépa : sans identifiants eBay, génère le cache avec les requêtes par série.
Avec EBAY_APP_ID + EBAY_CERT_ID, interroge Marketplace Insights (ventes terminées).

Usage :
  python3 refresh-ebay-sold-cache.py              # dry-run si pas de clés
  python3 refresh-ebay-sold-cache.py --live         # force appel API (clés requises)
  python3 refresh-ebay-sold-cache.py --limit 5      # test sur 5 séries
  python3 refresh-ebay-sold-cache.py --series ev01  # une série
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
OUT = ROOT / "ebay-sold-cache.json"

EBAY_OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_INSIGHTS_URL = "https://api.ebay.com/buy/marketplace_insights/v1/item_sales/search"
EBAY_SCOPE = "https://api.ebay.com/oauth/api_scope/buy.marketplace.insights"
MARKETPLACE_ID = "EBAY_FR"
SALES_WINDOW_DAYS = 90
MIN_SALES = 1
REQUEST_DELAY_S = 0.35

FIELD_QUERIES = {
    "booster": "pokemon booster {name}",
    "display": "pokemon display {name}",
    "etb": "pokemon coffret dresseur {name}",
}

ENTRY_RE = re.compile(
    r'\{id:"([^"]+)", name:"([^"]+)", block:"[^"]+", date:"[^"]*", booster:[^,]+, display:[^,]+, etb:[^,]+, cm:CM\("([^"]+)"\)',
)


def parse_entries(text: str) -> list[tuple[str, str, str]]:
    return [(m[0], m[1], m[2]) for m in ENTRY_RE.findall(text)]


def build_queries(name: str) -> dict[str, str]:
    return {field: tpl.format(name=name) for field, tpl in FIELD_QUERIES.items()}


def fetch_json(url: str, headers: dict | None = None, data: bytes | None = None, method: str = "GET") -> dict:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.load(res)


def ebay_token(app_id: str, cert_id: str) -> str:
    cred = base64.b64encode(f"{app_id}:{cert_id}".encode()).decode()
    body = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": EBAY_SCOPE}).encode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {cred}",
    }
    payload = fetch_json(EBAY_OAUTH_URL, headers=headers, data=body, method="POST")
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"OAuth eBay sans access_token : {payload}")
    return token


def parse_sold_price(item: dict) -> float | None:
    for key in ("soldPrice", "price"):
        val = item.get(key)
        if isinstance(val, dict):
            val = val.get("value")
        if val is None:
            continue
        try:
            return float(val)
        except (TypeError, ValueError):
            continue
    return None


def parse_sold_date(item: dict) -> str | None:
    for key in ("soldDate", "lastSoldDate", "creationDate"):
        val = item.get(key)
        if val:
            return str(val)
    return None


def aggregate_sales(items: list[dict], cutoff: datetime) -> dict | None:
    rows: list[tuple[float, str]] = []
    for item in items:
        price = parse_sold_price(item)
        sold_at = parse_sold_date(item)
        if price is None or price <= 0:
            continue
        if sold_at:
            try:
                dt = datetime.fromisoformat(sold_at.replace("Z", "+00:00"))
                if dt < cutoff:
                    continue
            except ValueError:
                pass
        rows.append((price, sold_at or ""))

    if not rows:
        return None

    prices = [p for p, _ in rows]
    rows.sort(key=lambda r: r[1], reverse=True)
    last_price, last_at = rows[0]
    out: dict = {
        "count": len(prices),
        "lastPrice": round(last_price, 2),
        "lastSoldAt": last_at or None,
    }
    if len(prices) >= 3:
        out["avg"] = round(statistics.mean(prices), 2)
        out["median"] = round(statistics.median(prices), 2)
    return out


def search_item_sales(token: str, query: str, limit: int = 50) -> list[dict]:
    params = urllib.parse.urlencode({"q": query, "limit": str(limit)})
    url = f"{EBAY_INSIGHTS_URL}?{params}"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": MARKETPLACE_ID,
        "Content-Type": "application/json",
    }
    try:
        payload = fetch_json(url, headers=headers)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"eBay Insights HTTP {exc.code} pour « {query} » : {body}") from exc
    return payload.get("itemSales") or payload.get("item_sales") or []


def build_cache(
    entries: list[tuple[str, str, str]],
    *,
    live: bool,
    app_id: str | None,
    cert_id: str | None,
) -> dict:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cache: dict = {"updatedAt": now, "marketplace": MARKETPLACE_ID, "windowDays": SALES_WINDOW_DAYS, "series": {}}
    token = None
    cutoff = datetime.now(timezone.utc) - timedelta(days=SALES_WINDOW_DAYS)

    if live:
        if not app_id or not cert_id:
            raise RuntimeError("Mode --live : définir EBAY_APP_ID et EBAY_CERT_ID")
        token = ebay_token(app_id, cert_id)

    for entry_id, name, _slug in entries:
        row: dict = {}
        queries = build_queries(name)
        for field, query in queries.items():
            cell: dict = {"query": query}
            if live and token:
                sales = search_item_sales(token, query)
                stats = aggregate_sales(sales, cutoff)
                if stats:
                    cell.update(stats)
                time.sleep(REQUEST_DELAY_S)
            row[field] = cell
        cache["series"][entry_id] = row

    return cache


def main() -> int:
    parser = argparse.ArgumentParser(description="Cache eBay vendu FR pour Pokestar")
    parser.add_argument("--live", action="store_true", help="Appeler l'API eBay (clés requises)")
    parser.add_argument("--limit", type=int, default=0, help="Limiter le nombre de séries")
    parser.add_argument("--series", action="append", default=[], help="ID série (répétable)")
    args = parser.parse_args()

    if not HTML.exists():
        print(f"ERREUR: {HTML.name} manquant", file=sys.stderr)
        return 1

    text = HTML.read_text(encoding="utf-8")
    entries = parse_entries(text)
    if args.series:
        wanted = set(args.series)
        entries = [e for e in entries if e[0] in wanted]
    if args.limit > 0:
        entries = entries[: args.limit]

    app_id = __import__("os").environ.get("EBAY_APP_ID")
    cert_id = __import__("os").environ.get("EBAY_CERT_ID")
    live = args.live and bool(app_id and cert_id)

    if args.live and not live:
        print("AVERTISSEMENT: --live sans EBAY_APP_ID/EBAY_CERT_ID → dry-run requêtes seulement", file=sys.stderr)

    cache = build_cache(entries, live=live, app_id=app_id, cert_id=cert_id)
    OUT.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    mode = "live" if live else "dry-run"
    filled = sum(
        1
        for row in cache["series"].values()
        for cell in row.values()
        if cell.get("count", 0) >= MIN_SALES
    )
    print(f"OK {OUT.name} — {len(cache['series'])} séries — {mode} — {filled} cellules avec stats")
    if not live:
        print("Prochaine étape : créer compte eBay Developer (gratuit), clés Production, puis EBAY_APP_ID=… EBAY_CERT_ID=… python3 refresh-ebay-sold-cache.py --live --limit 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())