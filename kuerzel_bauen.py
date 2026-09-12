"""Baut kuerzel.json: die Zuordnung Boersenkuerzel zu Firmenname.

WOZU (Nutzerauftrag 12.09.2026): "Ich moechte IOT eingeben koennen,
Samsara wird erkannt und vom Helfer getradet." Ohne Firmennamen scheitert
die Suche bei DEGIRO an kurzen Kuerzeln, die nicht im Namen stecken - sie
arbeitet auf dem NAMEN (am 08.09.2026 an MU gemessen, das Munich Re und
Murata liefert, aber nie Micron). Die Kandidatenliste von Heliot kennt nur
die 240 ueberwachten Werte; alles darueber hinaus kommt aus dieser Datei.

QUELLE ist das Kuerzelverzeichnis der amerikanischen Boersenaufsicht
(company_tickers.json). Gemessen am 12.09.2026: 10.426 Kuerzel, 798 kB,
in 0,25 s geladen, und alle 240 Kandidaten stehen darin.

WARUM DIESES EIGENE REPO: Die SEC schickt keinen
Access-Control-Allow-Origin-Kopf (gemessen 12.09.2026). Ein Abruf aus der
Seite heraus wird vom Browser also geblockt. raw.githubusercontent.com
schickt ihn ("*", ebenfalls gemessen) - deshalb holt Heliot die fertige
Datei von hier, und die Aktion in .github/workflows/kuerzel.yml haelt sie
taeglich frisch. Das Repo ist oeffentlich, weil eine private Datei nur mit
Zugangsschluessel lesbar waere und ein Schluessel in einer Webseite fuer
jeden lesbar ist. Es enthaelt ausschliesslich diese oeffentliche
Boersenliste.

GEPUTZT WIRD GENAU EINES: Die SEC haengt den Gruendungsstaat an
("NEWMONT Corp /DE/"). Alles ab dem Schraegstrich faellt weg - damit
bestehen alle 240 Kandidaten die Namens-Gegenprobe des Helfers (ohne die
Regel nur 229).

GESCHRIEBEN WIRD NUR BEI ECHTER AENDERUNG: Sonst truege die Datei jeden Tag
ein neues Baudatum, die Aktion legte jeden Tag einen Stand ab und jeder
Browser lud 333 kB ohne Gewinn.

Aufruf:  python kuerzel_bauen.py
"""
import datetime
import io
import json
import pathlib
import re
import time
import urllib.error
import urllib.request

WURZEL = pathlib.Path(__file__).resolve().parent
ZIEL = WURZEL / "kuerzel.json"
QUELLE = "https://www.sec.gov/files/company_tickers.json"
# Die SEC verlangt eine Kennung mit Kontaktadresse.
KENNUNG = "Heliot Kuerzelverzeichnis mathias.schmuckerschlag@gmail.com"

# Mindestumfang: Bleibt die Antwort weit darunter, ist etwas schiefgegangen
# (Wartungsseite, halber Download) und die alte Datei bleibt stehen.
MINDESTENS = 8000
PROBE = {"IOT": "Samsara", "AAPL": "Apple", "NVDA": "NVIDIA"}
# Die SEC drosselt gelegentlich. Ein einzelner Aussetzer soll den taeglichen
# Lauf nicht rot faerben, ehe nicht dreimal nichts gekommen ist.
VERSUCHE = 3
PAUSE = 20


def holen():
    letzter = None
    for versuch in range(VERSUCHE):
        try:
            bitte = urllib.request.Request(QUELLE, headers={"User-Agent": KENNUNG})
            with urllib.request.urlopen(bitte, timeout=60) as antwort:
                return json.loads(antwort.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError) as fehler:
            letzter = fehler
            print("Versuch %d von %d gescheitert: %s" % (versuch + 1, VERSUCHE, fehler))
            if versuch + 1 < VERSUCHE:
                time.sleep(PAUSE)
    raise SystemExit("Die SEC hat %d mal nicht geliefert (%s). "
                     "Die vorhandene Datei bleibt unangetastet." % (VERSUCHE, letzter))


def putzen(name):
    return re.sub(r"\s*/.*$", "", name or "").strip(" ,.")


def alterStand():
    try:
        with io.open(ZIEL, "r", encoding="utf-8") as f:
            return json.load(f).get("kuerzel") or {}
    except Exception:
        return None


def bauen():
    roh = holen()
    kuerzel = {}
    for eintrag in roh.values():
        sym = str(eintrag.get("ticker") or "").strip().upper()
        name = putzen(str(eintrag.get("title") or ""))
        if sym and name and sym not in kuerzel:
            kuerzel[sym] = name

    if len(kuerzel) < MINDESTENS:
        raise SystemExit("Nur %d Kuerzel gelesen, erwartet waren mindestens %d. "
                         "Die vorhandene Datei bleibt unangetastet." % (len(kuerzel), MINDESTENS))
    for sym, teil in PROBE.items():
        if teil.lower() not in kuerzel.get(sym, "").lower():
            raise SystemExit("Die Probe %s ergab '%s', erwartet war '%s' darin. "
                             "Die vorhandene Datei bleibt unangetastet."
                             % (sym, kuerzel.get(sym, ""), teil))

    sortiert = dict(sorted(kuerzel.items()))
    if alterStand() == sortiert:
        print("kuerzel.json: unveraendert, %d Kuerzel. Nichts geschrieben." % len(sortiert))
        return

    daten = {
        "gebaut_am": datetime.date.today().isoformat(),
        "quelle": "SEC company_tickers.json",
        "kuerzel": sortiert,
    }
    text = json.dumps(daten, ensure_ascii=False, separators=(",", ":"))
    with io.open(ZIEL, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("%s: %d Kuerzel, %d Bytes" % (ZIEL.name, len(kuerzel), len(text.encode("utf-8"))))
    for sym in PROBE:
        print("   %-5s %s" % (sym, kuerzel[sym]))


if __name__ == "__main__":
    bauen()
