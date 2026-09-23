"""All logik för bevakningen. Appen (app.py) anropar funktionerna här."""
import re
from datetime import date
from io import BytesIO

import feedparser
import pandas as pd
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from openpyxl import load_workbook


# ---------- Tolka det användaren skriver in ----------

def las_kallor(text):
    """Gör om rader som 'Namn | https://...' till en dict."""
    kallor = {}
    for rad in text.splitlines():
        if "|" in rad:
            namn, url = rad.split("|", 1)
            if namn.strip() and url.strip():
                kallor[namn.strip()] = url.strip()
    return kallor


def kallor_till_text(kallor):
    return "\n".join(f"{namn} | {url}" for namn, url in kallor.items())


def las_ord(text):
    """Ord separerade med ny rad eller komma, gemener."""
    return [o.strip().lower() for o in re.split(r"[,\n]", text) if o.strip()]


# ---------- Matchning (samma tre steg som originalet) ----------

def _finns_som_ord(ord_, text):
    return re.search(r"\b" + re.escape(ord_) + r"\b", text) is not None


def hitta_matchning(titel, sammanfattning, kategorier, inst):
    """
    1. RSS-kategori innehåller ett kategoriord -> träff
    2. Ett nyckelord finns -> träff
    3. Ett tvetydigt ord finns -> träff bara om ett kontextord också finns
    """
    text = f"{titel} {sammanfattning}".lower()
    kategorier = [k.lower() for k in kategorier]

    for kat in kategorier:
        for k in inst["kategoriord"]:
            if k in kat:
                return True, f"kategori: {k}"

    for o in inst["nyckelord"]:
        if _finns_som_ord(o, text):
            return True, o

    for o in inst["tvetydiga_ord"]:
        if _finns_som_ord(o, text):
            for k in inst["kontextord"]:
                if k in text:
                    return True, f"{o} + {k}"

    return False, None


def _rensa_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


# ---------- Hämta ----------

def hamta_nyheter(inst):
    resultat, statistik = [], []
    kallor = [(n, u, False) for n, u in inst["rena_kallor"].items()]
    kallor += [(n, u, True) for n, u in inst["blandade_kallor"].items()]

    for namn, url, filtrera in kallor:
        try:
            feed = feedparser.parse(url)
        except Exception:
            feed = None

        if not feed or not feed.entries:
            statistik.append({"Källa": namn, "Artiklar": 0, "Träffar": 0,
                              "Status": "Kunde inte läsa flödet, kolla länken"})
            continue

        traffar = 0
        for entry in feed.entries:
            titel = entry.get("title", "")
            sammanfattning = _rensa_html(entry.get("summary", ""))
            kategorier = [t.get("term", "") for t in entry.get("tags", []) or []]

            if filtrera:
                matchar, orsak = hitta_matchning(titel, sammanfattning, kategorier, inst)
                if not matchar:
                    continue
            else:
                orsak = "källa utan filter"

            traffar += 1
            resultat.append({
                "Källa": namn,
                "Titel": titel,
                "Länk": entry.get("link", ""),
                "Publicerad": entry.get("published", "Okänt datum"),
                "Sammanfattning": sammanfattning or "Ingen sammanfattning",
                "Matchande nyckelord": orsak,
            })

        statistik.append({"Källa": namn, "Artiklar": len(feed.entries),
                          "Träffar": traffar, "Status": "OK"})

    df = pd.DataFrame(resultat)
    if not df.empty:
        df = df.drop_duplicates(subset="Länk").reset_index(drop=True)
    return df, pd.DataFrame(statistik)


# ---------- Excel ----------

def skapa_excel(df):
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    wb = load_workbook(buf)
    ws = wb.active
    rubriker = [c.value for c in ws[1]]
    if "Länk" in rubriker:
        kol = rubriker.index("Länk") + 1
        for rad in range(2, ws.max_row + 1):
            cell = ws.cell(row=rad, column=kol)
            if cell.value:
                cell.hyperlink = cell.value
                cell.style = "Hyperlink"
    ut = BytesIO()
    wb.save(ut)
    return ut.getvalue()


# ---------- Word ----------

def _bokmarke(paragraph, namn, id_):
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(id_))
    start.set(qn("w:name"), namn)
    paragraph._p.insert(0, start)
    slut = OxmlElement("w:bookmarkEnd")
    slut.set(qn("w:id"), str(id_))
    paragraph._p.append(slut)


def _intern_lank(paragraph, text, bokmarke):
    lank = OxmlElement("w:hyperlink")
    lank.set(qn("w:anchor"), bokmarke)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    farg = OxmlElement("w:color")
    farg.set(qn("w:val"), "0000FF")
    rpr.append(farg)
    understruken = OxmlElement("w:u")
    understruken.set(qn("w:val"), "single")
    rpr.append(understruken)
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    lank.append(run)
    paragraph._p.append(lank)


def skapa_word(df, statistik, rubrik):
    doc = Document()
    doc.add_heading(f"{rubrik}: {date.today():%Y-%m-%d}", level=1)
    doc.add_paragraph(f"Totalt {len(df)} artiklar från {df['Källa'].nunique()} källor.")

    kallor = list(df["Källa"].unique())
    antal = dict(zip(statistik["Källa"], statistik["Träffar"]))

    doc.add_heading("Översikt: antal träffar per källa", level=2)
    for i, kalla in enumerate(kallor):
        _intern_lank(doc.add_paragraph(), f"{kalla}: {antal.get(kalla, 0)} träffar", f"kalla_{i}")

    for i, kalla in enumerate(kallor):
        h = doc.add_heading(f"{kalla} ({antal.get(kalla, 0)} träffar)", level=2)
        _bokmarke(h, f"kalla_{i}", i + 1)
        for _, rad in df[df["Källa"] == kalla].iterrows():
            doc.add_paragraph().add_run(rad["Titel"]).bold = True
            doc.add_paragraph(f"Publicerad: {rad['Publicerad']}")
            doc.add_paragraph(f"Ingress: {rad['Sammanfattning']}")
            doc.add_paragraph(f"Länk: {rad['Länk']}")
            doc.add_paragraph(f"Matchning: {rad['Matchande nyckelord']}")
            doc.add_paragraph("")

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
