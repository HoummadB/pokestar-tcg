# Pokestar V1 HTML — Instructions Agents

Site communautaire **La Cote du TCG Pokémon** — repères de prix boosters / displays / ETB,
boutique eBay affiliée, distributeurs automatiques.

| Champ | Valeur |
|-------|--------|
| URL prod | https://pokestar-tcg.com |
| Chemin | `NEWMETA/Pokestar-HTML/` |
| Repo Git | https://github.com/HoummadB/pokestar-html |
| Stack | SPA monolithique HTML/CSS/JS + Firebase Firestore/Auth |
| Contact | pokestar.store@gmail.com |
| Vendeur eBay | pokestartcg |
| Statut | V1 en production, maintenance et stabilisation uniquement |

La V2 vit dans `NEWMETA/Pokestar/` avec un repo Git distinct. Ne pas ajouter de
nouveau chantier structurel dans cette V1 : corriger seulement la securite, le
deploiement, le legal et les regressions necessaires jusqu'a la bascule.

---

## Structure

```text
NEWMETA/Pokestar-HTML/
├── AGENTS.md              # cette fiche
├── index.html             # app complète (source unique)
├── cm-market-cache.json   # prix Cardmarket (maj quotidienne)
├── ebay-sold-cache.json   # repères eBay vendu FR (maj cron, vide tant que pas de clés)
├── refresh-cm-cache.py    # sync CM → json + seed HTML
├── refresh-ebay-sold-cache.py  # sync eBay vendu → json (dry-run sans clés)
├── tools/
│   ├── photo-review.html       # panier corrections Booster-Display-ETB
│   └── photo-review-state.json # décisions et paniers résolus versionnés
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
- **Logos de série** : Firestore `pokestar_logos` (base64). **Photos produit** : manifest local `assets/product-photos/manifest.json`, puis Firestore manuel et Scrydex en secours. Les héros de 107 séries sont des visuels français récupérés depuis [PkmCards](https://www.pkmcards.fr/series/) et stockés dans `assets/series-logos/`; 11 séries historiques gardent le CDN Pokémon TCG API faute de visuel PkmCards correspondant.
- **Prix Cardmarket UE** : guide officiel JSON (maj ~1×/jour), embarqué `CM_MARKET_SEED` + fichier `cm-market-cache.json`. Le guide n'est pas un prix France-only.
- **eBay vendu** : lien externe + cache serveur `ebay-sold-cache.json` (phase en cours).
  Sans clés eBay Developer, le cache ne contient que les requêtes ; la ligne
  `eBay FR` affiche la **dernière vente** dès qu'une est trouvée (90 j). La
  médiane n'apparaît qu'à partir de 3 ventes, en complément.
- **UI** : hero logo série + tuiles Booster / Display / ETB (photo → logo → icône).

Firebase projet : `pokestar-tcg` (config client dans `index.html`).

---

## Commandes

Depuis `NEWMETA/Pokestar-HTML/` :

```bash
# Rafraîchir les prix Cardmarket (json + seed dans index.html)
python3 refresh-cm-cache.py

# Repères eBay vendu FR (dry-run sans clés ; live avec EBAY_APP_ID + EBAY_CERT_ID)
python3 refresh-ebay-sold-cache.py
EBAY_APP_ID=… EBAY_CERT_ID=… python3 refresh-ebay-sold-cache.py --live --limit 5

# Vérifier syntaxe JS
node -e "const fs=require('fs');const h=fs.readFileSync('index.html','utf8');const m=h.match(/<script>\\n([\\s\\S]*)<\\/script>\\s*<\\/body>/);new Function(m[1]);console.log('JS OK');"

# Servir en local
python3 -m http.server 8765
# → http://localhost:8765/

# Contrôler et inclure les photos produit
# → http://localhost:8765/tools/photo-review.html
```

Le helper photo fonctionne dans tout navigateur moderne. Pour un mauvais
visuel : copier la recherche proposée ou ouvrir Google Images depuis la tuile,
coller une image ou son URL, ou glisser un fichier dans la zone de collage.
Le helper affiche « Image jointe — incluse dans le JSON » quand le fichier est
réellement embarqué ; un simple commentaire de nom de fichier ne suffit pas.
ajouter une note, puis utiliser **Copier le JSON** ou **Exporter le JSON**. Le
glisser-déposer d'une grande photo sur une autre prépare une interversion : les
deux emplacements entrent ensemble dans le panier. Le
panier reste local jusqu'à traitement par un agent. Après application des
fichiers dans le repo, l'agent met à jour `tools/photo-review-state.json`
(`resolved`) afin que les lignes traitées quittent automatiquement le panier.
La vue initiale affiche tous les emplacements (Booster, Display et ETB) ; le
filtre **À examiner** masque volontairement les visuels déjà traités.
Chaque résolution utilise la clé `<serie-id>:<field>` et au minimum
`{"resolvedAt":"<ISO>","manifestVersion":"<version>"}`.

Cron recommandé (Hetzner ou Mac) : `refresh-cm-cache.py` 1×/jour puis redeploy des fichiers statiques.

Option Firestore : écrire le cache dans `pokestar_market/cardmarket` ou
`pokestar_market/ebay_sold` pour override sans redeploy HTML — le front lit le
doc le plus récent.

Compte eBay Developer : **gratuit** sur developer.ebay.com → Application
Production → `App ID` + `Cert ID` en variables d'environnement (jamais dans le
front). Valider d'abord avec `--live --limit 5` avant cron complet (~354
requêtes / jour si toutes les séries).

---

## Déploiement

Hébergement actuel : **Vercel** (statique).

Fichiers à publier ensemble :

- `index.html`
- `cm-market-cache.json`
- `ebay-sold-cache.json` (quand rempli)
- `manifest.json`
- `sw.js`
- `favicon.ico`, `favicon-32.png`
- `icon-192.png`, `icon-512.png`
- `robots.txt`, `vercel.json`
- `assets/brand-logo.jpg`
- `assets/product-photos/manifest.json` et les photos qu'il référence
- `assets/series-logos/`

Après modification de `index.html` ou des prix CM :

1. `python3 refresh-cm-cache.py`
2. Vérifier rendu local (`python3 -m http.server`)
3. Deploy Vercel depuis `https://github.com/HoummadB/pokestar-html` (push `main` ou CLI)
4. Commit local ChakmallOs si scope terminé

**Push** : uniquement sur demande explicite de Hoummad.

---

## Missions agent typiques

| Mission | Action |
|---------|--------|
| Nouvelle série TCG | Ajouter entrée `BASE_DATA` dans `index.html`, puis `refresh-cm-cache.py` |
| Prix CM pas affichés | Lancer `refresh-cm-cache.py`, vérifier mapping slug CM |
| Logo série | Mode admin (pseudo `admin`) → upload hero ; stocké Firestore |
| Préparer une correction photo | `tools/photo-review.html` → rechercher, coller image/lien, commenter, exporter le JSON |
| Appliquer un panier photo | Lire le JSON, vérifier la source, écrire l'image et le manifest, puis marquer la clé dans `photo-review-state.json.resolved`. Pour `swap-local-path`, sauvegarder les deux sources avant toute écriture et appliquer la paire atomiquement. |
| Override photo ponctuel | Admin → survol vignette produit → `+` (Firestore, pas le catalogue local canonique) |
| UI / UX | Modifier CSS + fonctions `cardHero`, `productThumb`, `priceCell` dans `index.html` |
| Mentions légales / footer | Section `#legalView` et `<footer>` dans `index.html` |

## Qualité des photos produit

- La présence d'un fichier dans le manifest ne vaut pas validation visuelle :
  la collecte bulk initiale a utilisé des slots Scrydex heuristiques. Le statut
  vérifié ou à revoir est porté par `tools/photo-review-state.json`.
- Toute nouvelle entrée ou tout remplacement dans le manifest doit utiliser un
  visuel dont le type produit et la série ont été vérifiés.
- `tools/photo-review.html` est le flux canonique pour préparer les corrections
  des 354 slots. Il ne modifie pas directement le catalogue : il produit un
  JSON borné à transmettre à l'agent. Les décisions acquises et paniers résolus
  sont dans `tools/photo-review-state.json` ; ne pas les dupliquer dans une
  autre note active.
- Le bloc EX (`ex01` à `ex15`) n'a pas d'ETB historique vérifiable : ses 15
  références heuristiques ont été retirées du manifest le 2026-07-10. Le rendu
  affiche donc le glyphe ETB neutre jusqu'à validation d'une source dédiée.
- Les logos hero Firestore ne sont pas nécessaires pour le catalogue de base :
  les 118 séries ont désormais un hero local dans le manifest. 107 utilisent
  un visuel de série français PkmCards et 11 gardent un logo du catalogue
  Pokémon TCG API faute de visuel PkmCards correspondant. Vérifier les droits
  d'usage avant toute nouvelle série ou usage commercial élargi.

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

Produit listé dans `NEWMETA/AGENTS.md` § outils actifs. Statut : **Production
V1 en maintenance** (site live pokestar-tcg.com). La nouvelle version se
prepare dans `NEWMETA/Pokestar/`.
