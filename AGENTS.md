# Pokestar — Instructions Agents

Site communautaire **La Cote du TCG Pokémon** — repères de prix boosters / displays / ETB,
boutique eBay affiliée, distributeurs automatiques.

| Champ | Valeur |
|-------|--------|
| URL prod | https://pokestar-tcg.com |
| Chemin | `NEWMETA/Pokestar/` |
| Repo Git | https://github.com/HoummadB/pokestar-tcg |
| Stack | SPA monolithique HTML/CSS/JS + Firebase Firestore/Auth |
| Contact | pokestar.store@gmail.com |
| Vendeur eBay | pokestartcg |

---

## Structure

```text
NEWMETA/Pokestar/
├── AGENTS.md              # cette fiche
├── index.html             # app complète (source unique)
├── cm-market-cache.json   # prix Cardmarket (maj quotidienne)
├── refresh-cm-cache.py    # sync CM → json + seed HTML
├── manifest.json          # PWA
├── sw.js                  # service worker (shell + cache CM)
├── favicon.ico            # favicon navigateur
├── favicon-32.png         # favicon PNG
├── icon-192.png           # icône PWA / apple-touch
├── icon-512.png           # icône PWA / OG
├── robots.txt             # SEO
├── vercel.json            # en-têtes sécurité (Vercel)
└── assets/brand-logo.jpg  # logo header + source icônes
```

Ne pas versionner de dump navigateur (`cote-des-boosters (25).html`, etc.).
Point d'entrée déploiement : **`index.html`** à la racine du site.

---

## Fonctionnement

- **Cote Pokestar** : prix communautaires / admin, stockés Firestore `pokestar_state/main`.
- **Logos & photos produit** : Firestore `pokestar_logos` (base64).
- **Prix Cardmarket** : guide officiel JSON (maj ~1×/jour), embarqué `CM_MARKET_SEED` + fichier `cm-market-cache.json`.
- **eBay vendu** : pas d'API — lien externe seulement.
- **UI** : hero logo série + tuiles Booster / Display / ETB (photo → logo → icône).

Firebase projet : `pokestar-tcg` (config client dans `index.html`).

---

## Commandes

Depuis `NEWMETA/Pokestar/` :

```bash
# Rafraîchir les prix Cardmarket (json + seed dans index.html)
python3 refresh-cm-cache.py

# Vérifier syntaxe JS
node -e "const fs=require('fs');const h=fs.readFileSync('index.html','utf8');const m=h.match(/<script>\\n([\\s\\S]*)<\\/script>\\s*<\\/body>/);new Function(m[1]);console.log('JS OK');"

# Servir en local
python3 -m http.server 8765
# → http://localhost:8765/
```

Cron recommandé (Hetzner ou Mac) : `refresh-cm-cache.py` 1×/jour puis redeploy des fichiers statiques.

Option Firestore : écrire le cache dans `pokestar_market/cardmarket` pour override sans redeploy HTML — le front lit ce doc si plus récent que le seed.

---

## Déploiement

Hébergement actuel : **Vercel** (statique).

Fichiers à publier ensemble :

- `index.html`
- `cm-market-cache.json`
- `manifest.json`
- `sw.js`
- `favicon.ico`, `favicon-32.png`
- `icon-192.png`, `icon-512.png`
- `robots.txt`, `vercel.json`
- `assets/brand-logo.jpg`

Après modification de `index.html` ou des prix CM :

1. `python3 refresh-cm-cache.py`
2. Vérifier rendu local (`python3 -m http.server`)
3. Deploy Vercel depuis `https://github.com/HoummadB/pokestar-tcg` (push `main` ou CLI)
4. Commit local ChakmallOs si scope terminé

**Push** : uniquement sur demande explicite de Hoummad.

---

## Missions agent typiques

| Mission | Action |
|---------|--------|
| Nouvelle série TCG | Ajouter entrée `BASE_DATA` dans `index.html`, puis `refresh-cm-cache.py` |
| Prix CM pas affichés | Lancer `refresh-cm-cache.py`, vérifier mapping slug CM |
| Logo série | Mode admin (pseudo `admin`) → upload hero ; stocké Firestore |
| Photo booster/display/ETB | Admin → survol vignette produit → `+` |
| UI / UX | Modifier CSS + fonctions `cardHero`, `productThumb`, `priceCell` dans `index.html` |
| Mentions légales / footer | Section `#legalView` et `<footer>` dans `index.html` |

---

## Interdits

- Scraper Cardmarket/eBay côté client (CORS + ToS).
- Dupliquer la fiche de poste ailleurs — canon ici + index `NEWMETA/AGENTS.md`.
- Exposer clés admin ou `ADMIN_CODE` dans la doc publique.
- Push prod sans validation Hoummad.

---

## Index NEWMETA

Produit listé dans `NEWMETA/AGENTS.md` § outils actifs. Statut : **Production** (site live pokestar-tcg.com).