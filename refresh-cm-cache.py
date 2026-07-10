#!/usr/bin/env python3
"""Rafraîchit les prix Cardmarket : cm-market-cache.json + CM_MARKET_SEED dans index.html."""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
OUT = ROOT / "cm-market-cache.json"

SLUG_PREFIX = {
    "Scarlet-Violet": "Scarlet & Violet",
    "Paldea-Evolved": "Paldea Evolved",
    "Obsidian-Flames": "Obsidian Flames",
    "Paradox-Rift": "Paradox Rift",
    "Paldean-Fates": "Paldean Fates",
    "Temporal-Forces": "Temporal Forces",
    "Twilight-Masquerade": "Twilight Masquerade",
    "Shrouded-Fable": "Shrouded Fable",
    "Stellar-Crown": "Stellar Crown",
    "Surging-Sparks": "Surging Sparks",
    "Prismatic-Evolutions": "Prismatic Evolutions",
    "Journey-Together": "Journey Together",
    "Destined-Rivals": "Destined Rivals",
    "Black-Bolt": "Black Bolt",
    "White-Flare": "White Flare",
    "Mega-Evolution": "Mega Evolution",
    "Phantasmal-Flames": "Phantasmal Flames",
    "Ascended-Heroes": "Ascended Heroes",
    "Perfect-Order": "Perfect Order",
    "Chaos-Rising": "Chaos Rising",
    "Pitch-Black": "Pitch Black",
    "Sword-Shield": "Sword & Shield",
    "Rebel-Clash": "Rebel Clash",
    "Darkness-Ablaze": "Darkness Ablaze",
    "Vivid-Voltage": "Vivid Voltage",
    "Battle-Styles": "Battle Styles",
    "Chilling-Reign": "Chilling Reign",
    "Evolving-Skies": "Evolving Skies",
    "Fusion-Strike": "Fusion Strike",
    "Brilliant-Stars": "Brilliant Stars",
    "Astral-Radiance": "Astral Radiance",
    "Lost-Origin": "Lost Origin",
    "Silver-Tempest": "Silver Tempest",
    "Crown-Zenith": "Crown Zenith",
    "Champions-Path": "Champion\u2019s Path",
    "Shining-Fates": "Shining Fates",
    "Pokemon-GO": "Pokémon GO",
    "Sun-Moon": "Sun & Moon",
    "Guardians-Rising": "Guardians Rising",
    "Burning-Shadows": "Burning Shadows",
    "Crimson-Invasion": "Crimson Invasion",
    "Ultra-Prism": "Ultra Prism",
    "Forbidden-Light": "Forbidden Light",
    "Celestial-Storm": "Celestial Storm",
    "Dragon-Majesty": "Dragon Majesty",
    "Lost-Thunder": "Lost Thunder",
    "Team-Up": "Team Up",
    "Unbroken-Bonds": "Unbroken Bonds",
    "Unified-Minds": "Unified Minds",
    "Hidden-Fates": "Hidden Fates",
    "Cosmic-Eclipse": "Cosmic Eclipse",
    "Shining-Legends": "Shining Legends",
    "Detective-Pikachu": "Detective Pikachu",
    "Flashfire": "Flashfire",
    "Furious-Fists": "Furious Fists",
    "Phantom-Forces": "Phantom Forces",
    "Primal-Clash": "Primal Clash",
    "Roaring-Skies": "Roaring Skies",
    "Ancient-Origins": "Ancient Origins",
    "BREAKpoint": "BREAKpoint",
    "BREAKthrough": "BREAKthrough",
    "Fates-Collide": "Fates Collide",
    "Steam-Siege": "Steam Siege",
    "Black-White": "Black & White",
    "Emerging-Powers": "Emerging Powers",
    "Noble-Victories": "Noble Victories",
    "Next-Destinies": "Next Destinies",
    "Dark-Explorers": "Dark Explorers",
    "Dragons-Exalted": "Dragons Exalted",
    "Boundaries-Crossed": "Boundaries Crossed",
    "Plasma-Storm": "Plasma Storm",
    "Plasma-Freeze": "Plasma Freeze",
    "Plasma-Blast": "Plasma Blast",
    "HeartGold-SoulSilver": "HeartGold & SoulSilver",
    "Call-of-Legends": "Call of Legends",
    "Diamond-Pearl": "Diamond & Pearl",
    "Mysterious-Treasures": "Mysterious Treasures",
    "Secret-Wonders": "Secret Wonders",
    "Great-Encounters": "Great Encounters",
    "Majestic-Dawn": "Majestic Dawn",
    "Awakening-Legends": "Legends Awakened",
    "Rising-Rivals": "Rising Rivals",
    "Vainqueurs-Supremes": "Supreme Victors",
    "EX-Rubis-Saphir": "EX Ruby & Sapphire",
    "EX-Sandstorm": "EX Sandstorm",
    "EX-Dragon": "EX Dragon",
    "EX-Team-Magma-vs-Team-Aqua": "EX Team Magma vs Team Aqua",
    "EX-Deoxys": "EX Deoxys",
    "EX-Emerald": "EX Emerald",
    "EX-FireRed-LeafGreen": "EX FireRed & LeafGreen",
    "EX-Hidden-Legends": "EX Hidden Legends",
    "EX-Unseen-Forces": "EX Unseen Forces",
    "EX-Delta-Species": "EX Delta Species",
    "EX-Legend-Maker": "EX Legend Maker",
    "EX-Holon-Phantoms": "EX Holon Phantoms",
    "EX-Crystal-Guardians": "EX Crystal Guardians",
    "EX-Dragon-Frontiers": "EX Dragon Frontiers",
    "EX-Power-Keepers": "EX Power Keepers",
    "Base-Set": "Base Set",
    "Neo-Genesis": "Neo Genesis",
    "Neo-Discovery": "Neo Discovery",
    "Neo-Revelation": "Neo Revelation",
    "Neo-Destiny": "Neo Destiny",
    "Expedition-Base-Set": "Expedition Base Set",
    "Team-Rocket": "Team Rocket",
    "151": "151",
    "Celebrations": "Celebrations",
    "Generations": "Generations",
    "Jungle": "Jungle",
    "Fossil": "Fossil",
    "Evolutions": "Evolutions",
    "Stormfront": "Stormfront",
    "Platinum": "Platinum",
    "Undaunted": "Undaunted",
    "Triumphant": "Triumphant",
    "Unleashed": "Unleashed",
    "XY": "XY",
}

SKIP = (
    "Case", "Bundle", "Blister", "Coin", "Build & Battle", "Theme Deck", "Mini Tin",
    "Poster", "Binder", "Checklane", "Fun Pack", " JP", "ID/TH", "Sleeved", "Enhanced",
    "DuoPack", "TriPack", "Collection", "File Set", "PCG", "Trainer &", "Promo", "Gym",
    "Special Set", "(6 Cards)", "Display",
)

CM_SEED_RE = re.compile(r"const CM_MARKET_SEED = \{.*?\};\nlet cmMarket", re.S)


def prefix_for(slug: str) -> str:
    return SLUG_PREFIX.get(slug, slug.replace("-", " "))


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=120) as res:
        return json.load(res)


def build_cache(text: str, old: dict | None = None) -> dict:
    entries = re.findall(
        r'\{id:"([^"]+)", name:"[^"]+", block:"[^"]+", date:"[^"]*", booster:[^,]+, display:[^,]+, etb:[^,]+, cm:CM\("([^"]+)"\)',
        text,
    )
    products = fetch_json(
        "https://downloads.s3.cardmarket.com/productCatalog/productList/products_nonsingles_6.json"
    )
    guide = fetch_json(
        "https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_6.json"
    )
    prices = {g["idProduct"]: g for g in guide["priceGuides"]}

    def pick(prefix: str, kind: str):
        out = []
        for p in products["products"]:
            n = p["name"]
            if not n.startswith(prefix + " "):
                continue
            if any(s in n for s in SKIP):
                continue
            if kind == "booster" and p["categoryName"] == "Pokémon Booster" and n.endswith(" Booster"):
                out.append(p)
            elif kind == "display" and p["categoryName"] == "Pokémon Display" and "Booster Box" in n:
                out.append(p)
            elif (
                kind == "etb"
                and p["categoryName"] == "Pokémon Elite Trainer Boxes"
                and "Elite Trainer Box" in n
                and "Pokémon Center" not in n
                and "Case" not in n
            ):
                out.append(p)
        if not out:
            return None
        out.sort(key=lambda x: (len(x["name"]), x["name"]))
        return out[0]

    cache = {"updatedAt": guide["createdAt"], "series": {}}
    for entry_id, slug in entries:
        prefix = prefix_for(slug)
        row = {}
        for kind in ("booster", "display", "etb"):
            prod = pick(prefix, kind)
            if not prod:
                continue
            g = prices.get(prod["idProduct"])
            if not g:
                continue
            low, trend, avg = g.get("low"), g.get("trend"), g.get("avg")
            if low is None and trend is None and avg is None:
                continue
            cell = {"low": low, "trend": trend, "avg": avg}
            if old:
                prev_row = old.get("series", {}).get(entry_id, {}).get(kind, {})
                old_trend = prev_row.get("trend")
                if old_trend is not None:
                    cell["prevTrend"] = old_trend
            row[kind] = cell
        if row:
            cache["series"][entry_id] = row
    return cache


def patch_html_seed(html: str, cache: dict) -> str:
    payload = json.dumps(cache, ensure_ascii=False, separators=(",", ":"))
    repl = f"const CM_MARKET_SEED = {payload};\nlet cmMarket"
    if not CM_SEED_RE.search(html):
        raise RuntimeError("CM_MARKET_SEED introuvable dans index.html")
    return CM_SEED_RE.sub(repl, html, count=1)


def main() -> int:
    if not HTML.exists():
        print(f"ERREUR: {HTML.name} manquant", file=sys.stderr)
        return 1

    text = HTML.read_text(encoding="utf-8")
    old_cache = {}
    if OUT.exists():
        old_cache = json.loads(OUT.read_text(encoding="utf-8"))
    cache = build_cache(text, old_cache)
    OUT.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    HTML.write_text(patch_html_seed(text, cache), encoding="utf-8")
    print(f"OK {OUT.name} + index.html — {len(cache['series'])} séries — {cache['updatedAt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())