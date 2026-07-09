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
- **Logos de série** : Firestore `pokestar_logos` (base64). **Photos produit** : manifest local `assets/product-photos/manifest.json`, puis Firestore manuel et Scrydex en secours.
- **Prix Cardmarket UE** : guide officiel JSON (maj ~1×/jour), embarqué `CM_MARKET_SEED` + fichier `cm-market-cache.json`. Le guide n'est pas un prix France-only.
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

## Qualité des photos produit

- Le manifest local ne doit référencer que des visuels dont le type produit et
  la série sont vérifiés.
- Le bloc EX (`ex01` à `ex15`) n'a pas d'ETB historique vérifiable : ses 15
  références heuristiques ont été retirées du manifest le 2026-07-10. Le rendu
  affiche donc le glyphe ETB neutre jusqu'à validation d'une source dédiée.
- Les 15 logos hero EX sont absents de `pokestar_logos` dans l'état contrôlé le
  2026-07-10 : ils sont servis localement depuis `assets/series-logos/`, avec
  le mapping et les URLs du catalogue Pokémon TCG API conservés dans le
  manifest. Vérifier les droits d'usage avant toute nouvelle série ou usage
  commercial élargi.

## Périmètre des prix

- `cm-market-cache.json` et `CM_MARKET_SEED` viennent du guide Cardmarket
  agrégé UE : l'URL `/fr/` traduit l'interface, elle ne limite pas le guide
  aux vendeurs français.
- Pour une cote France, la piste identifiée est l'API Pokéindex (`api.pokeindex.fr`)
  qui agrège Cardmarket, eBay, Vinted et Leboncoin. La clé doit rester côté
  serveur/cron et le service est payant ; aucune clé ne doit entrer dans le
  front public.
- Tant que cette source n'est pas activée, l'interface doit afficher
  explicitement « Cardmarket UE » et ne pas présenter ces valeurs comme le
  marché français.

---

## Interdits

- Scraper Cardmarket/eBay côté client (CORS + ToS).
- Dupliquer la fiche de poste ailleurs — canon ici + index `NEWMETA/AGENTS.md`.
- Exposer clés admin ou `ADMIN_CODE` dans la doc publique.
- Push prod sans validation Hoummad.

---

## Index NEWMETA

Produit listé dans `NEWMETA/AGENTS.md` § outils actifs. Statut : **Production** (site live pokestar-tcg.com).
