# siposbarni.com weboldal

Ez a mappa tartalmazza a siposbarni.com statikus portfolio oldal forrasat.

## Fontos fajlok

- `index.html` - az oldal vazszerkezete
- `styles.css` - a fekete-feher minimalista design
- `script.js` - galeria, keplapozo es urlap mukodes
- `content.json` - szovegek es kontakt linkek
- `artworks.json` - galeria adatok
- `assets/artworks` - festmenyek es thumbnail kepek
- `assets/rolam` - a Rolam szekcio forrasanyagai

## Telefonos frissites Google Drive-bol

A galeria forrasa az `assets/artworks` mappa. Telefonrol eleg a Google Drive-ban ide feltolteni a kepeket:

```text
assets/artworks/Sorozat neve/Kep cime - technika, hordozo 80x60cm.jpg
```

Pelda:

```text
assets/artworks/Budapest/Uj kep - olaj, farost 50x40cm.jpg
```

A sorozat/kategoria leirasat a mappaban levo `.txt` fajl adja. A frissites automatikusan ujrageneralja az `artworks.json` fajlt es a kis kepeket, amikor Cloudflare-csomagot keszitesz.

## Automata publikalas Cloudflare Pages + GitHub hasznalataval

Ha a projekt GitHub repositoryhoz van kotve, a `.github/workflows/build-gallery.yml` automatikusan ujrageneralja a galeriat, amikor az `assets/artworks` mappa valtozik.

Cloudflare Pages beallitas:

- Framework preset: None
- Build command: ures
- Build output directory: `/`
- Production branch: `main`

Ezutan a Drive-bol szinkronizalt fajlok GitHubra kerulese utan a Cloudflare Pages automatikusan publikal.

## Kezi publikalas Cloudflare-re

Modositas utan futtasd:

```powershell
python tools/build-cloudflare-zip.py
```

Ez letrehozza a feltoltheto csomagot:

```text
dist/siposbarni-cloudflare-upload.zip
```

Cloudflare-ben:

1. Workers & Pages
2. `siposbarni`
3. New deployment
4. Toltsd fel a `dist/siposbarni-cloudflare-upload.zip` fajlt
