# Kuerzelverzeichnis fuer Heliot

Diese Ablage enthaelt genau eine Nutzdatei: `kuerzel.json`, die Zuordnung von
Boersenkuerzel zu Firmenname aus dem Verzeichnis der amerikanischen
Boersenaufsicht (SEC, `company_tickers.json`), 10.426 Eintraege.

**Wozu:** Die Handels-App Heliot schickt dem Helfer im DEGIRO-Tab zu jedem
Auftrag den Firmennamen mit. Die Suche bei DEGIRO arbeitet auf dem Namen, und
kurze Kuerzel stecken oft nicht darin (an MU gemessen: liefert Munich Re und
Murata, aber nie Micron). Ohne Namen bricht der Kauf von Hand ab.

**Warum oeffentlich:** Die SEC schickt keinen
`Access-Control-Allow-Origin`-Kopf, ein Abruf aus der Seite heraus wird vom
Browser gesperrt. `raw.githubusercontent.com` schickt ihn, aber nur bei
oeffentlichen Ablagen. Eine private Ablage waere nur mit Zugangsschluessel
lesbar, und ein Schluessel in einer Webseite ist fuer jeden lesbar.
Hier liegt deshalb ausschliesslich die oeffentliche Boersenliste, nichts
Persoenliches.

**Frischgehalten** wird sie von `.github/workflows/kuerzel.yml`: taeglich
gegen 06:10 Wiener Zeit, dazu von Hand ausloesbar. Abgelegt wird nur, wenn
sich wirklich etwas geaendert hat.

**Abgerufen** wird sie unter
`https://raw.githubusercontent.com/mat-schmuck/heliot-kuerzel/main/kuerzel.json`.

**Selbst bauen:** `python kuerzel_bauen.py`
