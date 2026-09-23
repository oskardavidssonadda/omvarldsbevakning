import copy
import json
import re
import uuid
from datetime import datetime
from html import escape as esc

import streamlit as st

from bevakning import (antal, hamta_nyheter, markera, normalisera, rensa_ord,
                       skapa_excel, skapa_word, tom_bevakning, vard)
from mallar import GRUPPER, MALLAR

st.set_page_config(page_title="Omvärldsbevakning", page_icon="📰", layout="wide",
                   initial_sidebar_state="expanded")

EGEN = {"farg": "#0E9AA7", "etikett": "Egen", "punkt": "blue"}
FRAN_FIL = {"farg": "#64748B", "etikett": "Från fil", "punkt": "gray"}
FLIKAR = ["1. Källor", "2. Nyckelord", "3. Resultat"]


def slug(text):
    return re.sub(r"[^a-z0-9]", "", text.lower().translate(str.maketrans("åäöé", "aaoe")))

CSS = """
.block-container {padding-top: 1.6rem; padding-bottom: 4rem; max-width: 1200px;}
header[data-testid="stHeader"] {background: transparent;}

/* Startsidans toppbild */
.hero {position: relative; overflow: hidden; border-radius: 22px; padding: 2.6rem 2.6rem 2.4rem; margin-bottom: 2rem;
  color: #fff; background: linear-gradient(120deg, #4B2FE8 0%, #7C4DFF 50%, #FF7A59 100%);}
.hero::after {content: ""; position: absolute; right: -60px; top: -80px; width: 320px; height: 320px; border-radius: 50%;
  background: rgba(255,255,255,.12);}
.hero::before {content: ""; position: absolute; right: 140px; bottom: -120px; width: 220px; height: 220px; border-radius: 50%;
  background: rgba(255,255,255,.08);}
.hero-liten {font-weight: 600; opacity: .85; letter-spacing: .02em; margin-bottom: .6rem;}
.hero-titel {font-family: "Bricolage Grotesque", sans-serif; font-weight: 800; font-size: clamp(2.2rem, 4.5vw, 3.4rem);
  line-height: 1.02; letter-spacing: -.02em; max-width: 16ch;}
.hero-text {font-size: 1.1rem; opacity: .92; max-width: 46ch; margin-top: .9rem;}

.sektion {font-family: "Bricolage Grotesque", sans-serif; font-weight: 700; font-size: 1.35rem; margin: 1.6rem 0 .6rem;}

/* Kort */
[class*="st-key-kort_"] {background: #fff; border-top-width: 5px !important; min-height: 245px;
  box-shadow: 0 1px 2px rgba(29,27,58,.05), 0 8px 24px rgba(29,27,58,.06); transition: transform .15s, box-shadow .15s;}
[class*="st-key-kort_"]:hover {transform: translateY(-3px); box-shadow: 0 2px 4px rgba(29,27,58,.06), 0 14px 32px rgba(29,27,58,.10);}
[class*="st-key-kort_"] > div:last-child {margin-top: auto;}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-kort_"]) {flex: 1 1 auto;}
[class*="st-key-kort_"] {flex: 1 1 auto;}
[class*="st-key-fortsatt_"] {min-height: 0;}
.etikett {display: inline-block; font-size: .75rem; font-weight: 700; padding: .18rem .6rem; border-radius: 999px;}
.kort-titel {font-family: "Bricolage Grotesque", sans-serif; font-weight: 700; font-size: 1.45rem; line-height: 1.15; margin: .6rem 0 .45rem;}
.kort-text {opacity: .8; margin: 0 0 .5rem; line-height: 1.45;}
.kort-meta {font-size: .85rem; opacity: .6; margin: 0;}

/* Bevakningens toppband */
.band {border-radius: 20px; padding: 1.4rem 1.6rem; color: #fff; margin-bottom: .2rem;
  background: linear-gradient(120deg, var(--farg) 0%, color-mix(in srgb, var(--farg) 55%, #1D1B3A) 100%);}
.band .etikett {background: rgba(255,255,255,.2); color: #fff;}
.band-titel {font-family: "Bricolage Grotesque", sans-serif; font-weight: 800; font-size: clamp(1.8rem, 3.2vw, 2.5rem);
  line-height: 1.05; letter-spacing: -.02em; margin-top: .5rem; overflow-wrap: anywhere;}
.band-meta {opacity: .85; margin-top: .35rem;}

/* Flikar */
.stTabs [data-baseweb="tab-list"] {gap: .4rem;}
.stTabs [data-baseweb="tab"] {font-weight: 600; font-size: 1.02rem; padding: .5rem 1rem;}

/* Källor */
[class*="st-key-kalla_"] {background: #fff; border: 1px solid #E2DEF3; border-radius: 14px; padding: .7rem 1rem;}
.kalla-namn {font-weight: 700; font-size: 1.02rem;}
.kalla-url {font-size: .85rem; opacity: .65; overflow-wrap: anywhere; word-break: break-all;}
.kalla-ok {font-size: .85rem; color: #16A36A; font-weight: 600;}
.kalla-fel {font-size: .85rem; color: #D6453D; font-weight: 600;}

/* Resultat */
.stat {width: 100%; border-collapse: collapse; font-size: .92rem; background: #fff; border-radius: 12px; overflow: hidden;}
.stat th, .stat td {text-align: left; padding: .5rem .8rem; border-bottom: 1px solid #ECE9F7; vertical-align: top;}
.stat th {font-weight: 700; background: #F2F0FC;}
.stat td.tal, .stat th.tal {text-align: right;}
.stat td.ok {color: #16A36A; font-weight: 600;}
.stat td.fel {color: #D6453D; font-weight: 600;}
mark {background: #FFE58F; color: #1D1B3A; padding: 0 .15em; border-radius: 3px;}
.grupp {display: flex; align-items: center; gap: .6rem; margin: 2rem 0 .6rem;
  font-family: "Bricolage Grotesque", sans-serif; font-weight: 700; font-size: 1.25rem;}
.grupp span {font-family: Figtree, sans-serif; font-size: .8rem; font-weight: 700; background: #EDEAFB; color: #5B3DF5;
  padding: .15rem .6rem; border-radius: 999px;}
.artikel {background: #fff; border: 1px solid #ECE9F7; border-radius: 14px; padding: .9rem 1.1rem; margin-bottom: .6rem;
  transition: border-color .15s;}
.artikel:hover {border-color: #C9C0F7;}
.artikel a {font-weight: 700; font-size: 1.06rem; text-decoration: none; color: #1D1B3A; line-height: 1.35;}
.artikel a:hover {color: #5B3DF5;}
.meta {font-size: .85rem; opacity: .65; margin-top: .25rem;}
.chip {background: #EDEAFB; color: #4B2FE8; border-radius: 999px; padding: .08rem .6rem; margin-left: .5rem; font-weight: 600; opacity: 1;}
.ingress {opacity: .78; margin: .4rem 0 0; line-height: 1.5;}

/* Sidomeny */
.logo {display: flex; align-items: center; gap: .55rem; font-family: "Bricolage Grotesque", sans-serif;
  font-weight: 800; font-size: 1.25rem; margin: .2rem 0 1.2rem;}
.logo span {width: 14px; height: 14px; border-radius: 4px; background: linear-gradient(135deg, #8F7BFF, #FF7A59);}
[data-testid="stSidebar"] .stButton button {justify-content: flex-start;}
@media (prefers-reduced-motion: reduce) {[class*="st-key-kort_"], .artikel {transition: none;}
  [class*="st-key-kort_"]:hover {transform: none;}}
"""
kortfarger = "".join(f".st-key-kort_{slug(m['titel'])} {{border-top-color: {m['farg']} !important;}}"
                     for m in MALLAR) + f".st-key-kort_egen {{border-top-color: {EGEN['farg']} !important;}}"
st.markdown(f"<style>{CSS}{kortfarger}</style>", unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("oppna", {})
ss.setdefault("aktiv", None)
ss.setdefault("senast", None)


# =================== Data och navigering ===================
def nytt_id():
    return uuid.uuid4().hex[:8]


def oppna_ny(bev, stil, mall=None):
    for k in bev["kallor"]:
        k.setdefault("_id", nytt_id())
    pid = nytt_id()
    ss.oppna[pid] = {"bev": bev, "start": copy.deepcopy(bev), "version": 0, "resultat": None,
                     "kortid": None, "mall": mall, **stil}
    ss.aktiv = pid


def oppna_mall(m):
    oppna_ny(normalisera(copy.deepcopy(m["bevakning"])), {k: m[k] for k in ("farg", "etikett", "punkt")}, m["titel"])


def ga_till(pid):
    ss.aktiv = pid


def stang(pid):
    ss.oppna.pop(pid, None)
    ss.aktiv = None


def byt_flik(pid, flik):
    ss[f"flikmal_{pid}"] = flik


def satt_filter(pid, kid):
    for k in ss.oppna[pid]["bev"]["kallor"]:
        if k["_id"] == kid:
            k["filtrera"] = ss[f"{pid}_filt_{kid}"]


def ta_bort_trasiga(pid, namn):
    b = ss.oppna[pid]["bev"]
    b["kallor"] = [k for k in b["kallor"] if k["namn"] not in namn]


def ta_bort_kalla(pid, kid):
    b = ss.oppna[pid]["bev"]
    b["kallor"] = [k for k in b["kallor"] if k["_id"] != kid]


def som_fil(b):
    ren = {**b, "kallor": [{k: v for k, v in kalla.items() if not k.startswith("_")} for kalla in b["kallor"]]}
    return json.dumps(ren, ensure_ascii=False, indent=2)


def hantera_fil(fil):
    if fil and ss.get("senast_fil") != fil.file_id:
        ss.senast_fil = fil.file_id
        try:
            oppna_ny(normalisera(json.load(fil)), FRAN_FIL)
            st.rerun()
        except (ValueError, AttributeError):
            st.error("Filen gick inte att läsa. Välj en fil som sparats från appen.")


def sammanfattning(b):
    return f"{antal(len(b['kallor']), 'källa', 'källor')}, {antal(len(b['nyckelord']), 'nyckelord', 'nyckelord')}"


def kort(nyckel, farg, etikett, titel, text, meta):
    c = st.container(border=True, key=f"kort_{nyckel}")
    c.markdown(
        f"<span class='etikett' style='color:{farg};background:{farg}1F'>{esc(etikett)}</span>"
        f"<div class='kort-titel'>{esc(titel)}</div><p class='kort-text'>{esc(text)}</p>"
        f"<p class='kort-meta'>{esc(meta)}</p>", unsafe_allow_html=True)
    return c


# =================== Startsida ===================
def startsida():
    st.markdown(
        "<div class='hero'><div class='hero-liten'>Omvärldsbevakning</div>"
        "<div class='hero-titel'>Vad vill du hålla koll på?</div>"
        "<div class='hero-text'>Välj en färdig mall och gör den till din egen, eller bygg en bevakning från grunden. "
        "Appen samlar dagens artiklar från dina källor och plockar ut det som matchar dina nyckelord.</div></div>",
        unsafe_allow_html=True)

    if ss.oppna:
        st.markdown("<div class='sektion'>Fortsätt där du var</div>", unsafe_allow_html=True)
        st.markdown("<style>" + "".join(f".st-key-kort_fortsatt_{pid} {{border-top-color: {e['farg']} !important;}}"
                                         for pid, e in ss.oppna.items()) + "</style>", unsafe_allow_html=True)
        kol = st.columns(4, gap="medium")
        for i, (pid, e) in enumerate(ss.oppna.items()):
            with kol[i % 4]:
                c = kort(f"fortsatt_{pid}", e["farg"], e["etikett"], e["bev"]["namn"] or "Namnlös",
                         sammanfattning(e["bev"]), f"Körd {e['kortid']}" if e["kortid"] else "Inte körd än")
                c.button("Fortsätt", key=f"fortsatt_{pid}", width="stretch", on_click=ga_till, args=(pid,))
        st.markdown("<div class='sektion'>Eller börja på en ny</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='sektion'>Välj bland {len(MALLAR)} mallar</div>", unsafe_allow_html=True)

    grupp = st.pills("Visa mallar för", ["Alla"] + GRUPPER, default="Alla", key="grupp_filter",
                     label_visibility="collapsed") or "Alla"
    synliga = [m for m in MALLAR if grupp == "Alla" or m["grupp"] == grupp]
    kort_lista = [("mall", m) for m in synliga] + [("egen", None)]
    for rad in range(0, len(kort_lista), 4):
        kol = st.columns(4, gap="medium")
        for k, (typ, m) in zip(kol, kort_lista[rad:rad + 4]):
            with k:
                if typ == "egen":
                    c = kort("egen", EGEN["farg"], "Egen", "Från grunden",
                             "Helt blank. Lägg in dina egna källor och nyckelord.", "Tom bevakning")
                    c.button("Skapa egen", key="mall_egen", width="stretch", type="primary",
                             on_click=oppna_ny, args=(tom_bevakning("Min bevakning"), EGEN))
                    continue
                redan = next((pid for pid, e in ss.oppna.items() if e["mall"] == m["titel"]), None)
                c = kort(slug(m["titel"]), m["farg"], m["etikett"], m["titel"], m["text"],
                         sammanfattning(m["bevakning"]))
                if redan:
                    c.button("Redan öppen, gå dit", key=f"mall_{slug(m['titel'])}", width="stretch",
                             on_click=ga_till, args=(redan,))
                else:
                    c.button("Använd mallen", key=f"mall_{slug(m['titel'])}", width="stretch", type="primary",
                             on_click=oppna_mall, args=(m,))

    st.write("")
    with st.expander("Har du sparat en bevakning tidigare? Öppna den här"):
        hantera_fil(st.file_uploader("Välj fil", type="json", key="fil_start", label_visibility="collapsed"))


# =================== Bevakningssida ===================
def bevakningssida(pid):
    e = ss.oppna[pid]
    if ss.senast != pid:
        e["start"] = copy.deepcopy(e["bev"])
        e["version"] += 1
        ss.senast = pid
    b, start, v = e["bev"], e["start"], e["version"]
    k = lambda n: f"{pid}_{n}_{v}"
    namn_fil = re.sub(r"[^\w]+", "_", b["namn"] or "bevakning").strip("_")

    st.button("← Alla bevakningar och mallar", type="tertiary", on_click=ga_till, args=(None,))
    band, knappar = st.columns([7, 2.4], vertical_alignment="center", gap="medium")
    with knappar:
        kor_topp = st.button("Kör bevakningen", type="primary", width="stretch", key=k("kor_topp"))
        with st.popover("Namn, spara och stäng", width="stretch"):
            b["namn"] = st.text_input("Namn på bevakningen", start["namn"], key=k("namn")).strip() or "Namnlös bevakning"
            st.download_button("Spara som fil", som_fil(b), f"{namn_fil}.json", mime="application/json", width="stretch")
            st.caption("Spara filen om du vill kunna öppna bevakningen igen en annan dag.")
            st.divider()
            st.button("Stäng bevakningen", width="stretch", on_click=stang, args=(pid,))
            st.caption("Ändringar som inte sparats försvinner.")
    with band:
        st.markdown(
            f"<div class='band' style='--farg:{e['farg']}'><span class='etikett'>{esc(e['etikett'])}</span>"
            f"<div class='band-titel'>{esc(b['namn'])}</div>"
            f"<div class='band-meta'>{sammanfattning(b)}{', senast körd ' + e['kortid'] if e['kortid'] else ''}</div></div>",
            unsafe_allow_html=True)
    plats = st.empty()

    flikkey = k("flikar")
    if f"flikmal_{pid}" in ss:
        ss[flikkey] = ss.pop(f"flikmal_{pid}")
    elif flikkey not in ss:
        ss[flikkey] = FLIKAR[2] if e["resultat"] is not None else FLIKAR[0]
    t_kallor, t_ord, t_res = st.tabs(FLIKAR, key=flikkey, on_change="rerun")

    with t_kallor:
        flik_kallor(pid, e, b, k)
    with t_ord:
        kor_ord = flik_nyckelord(pid, b, start, k)
    with t_res:
        flik_resultat(e, b, namn_fil)

    if kor_topp or kor_ord:
        if not b["kallor"]:
            plats.warning("Lägg till minst en källa under Källor först.")
        else:
            with plats, st.spinner(f"Hämtar {antal(len(b['kallor']), 'källa', 'källor')}…"):
                e["resultat"] = hamta_nyheter(b)
            e["kortid"] = datetime.now().strftime("%H:%M")
            byt_flik(pid, FLIKAR[2])
            st.rerun()


def flik_kallor(pid, e, b, k):
    st.write("Slå på **Filtrera** för breda nyhetssajter, så kommer bara artiklar med dina nyckelord med. "
             "Stäng av det för källor som redan handlar om ditt ämne.")
    status = {}
    if e["resultat"] is not None:
        status = {r["Källa"]: r for r in e["resultat"][1].to_dict("records")}

    trasiga = [n for n, r in status.items() if r["Status"] != "OK" and any(x["namn"] == n for x in b["kallor"])]
    if trasiga:
        a, c = st.columns([3, 1.4], vertical_alignment="center")
        a.warning(f"{antal(len(trasiga), 'källa', 'källor')} gick inte att läsa senast. De är markerade i rött nedan.")
        c.button(f"Ta bort {'den' if len(trasiga) == 1 else 'dem'}", key=k("bort_trasiga"), width="stretch",
                 on_click=ta_bort_trasiga, args=(pid, trasiga))
    if not b["kallor"]:
        st.info("Inga källor än. Lägg till din första här nedanför.")
    for kalla in b["kallor"]:
        kid = kalla["_id"]
        with st.container(key=f"kalla_{pid}_{kid}"):
            c1, c2, c3 = st.columns([6, 1.6, 1.1], vertical_alignment="center")
            rad = f"<div class='kalla-namn'>{esc(kalla['namn'])}</div><div class='kalla-url'>{esc(kalla['url'])}</div>"
            s = status.get(kalla["namn"])
            if s:
                rad += (f"<div class='kalla-ok'>{antal(s['Träffar'], 'träff', 'träffar')} senast</div>" if s["Status"] == "OK"
                        else f"<div class='kalla-fel'>{esc(s['Status'])}</div>")
            c1.markdown(rad, unsafe_allow_html=True)
            c2.toggle("Filtrera", value=kalla["filtrera"], key=f"{pid}_filt_{kid}", on_change=satt_filter, args=(pid, kid))
            c3.button("Ta bort", key=f"{pid}_bort_{kid}", type="tertiary", on_click=ta_bort_kalla, args=(pid, kid))

    with st.form(k("ny_kalla"), clear_on_submit=True):
        st.markdown("**Lägg till en källa**")
        f1, f2 = st.columns([3, 2])
        url = f1.text_input("RSS-länk", placeholder="https://sajt.se/rss")
        namn = f2.text_input("Namn (valfritt)", placeholder="T.ex. SVT Nyheter")
        filtrera = st.toggle("Filtrera med nyckelord", value=True)
        if st.form_submit_button("Lägg till källa", type="primary"):
            url = url.strip()
            if url and not url.lower().startswith(("http://", "https://")):
                url = "https://" + url
            if not url or " " in url or "." not in (vard(url) or ""):
                st.error("Det där ser inte ut som en webbadress.")
            elif any(x["url"] == url for x in b["kallor"]):
                st.error("Den källan finns redan i listan.")
            else:
                b["kallor"].append({"namn": namn.strip() or vard(url), "url": url, "filtrera": filtrera, "_id": nytt_id()})
                st.rerun()
    st.caption("Hittar du ingen RSS-länk? Sök på sajtens namn och RSS, eller prova att lägga till /rss eller /feed "
               "efter adressen, till exempel https://sajt.se/feed.")
    st.button("Nästa: Nyckelord →", key=k("till_ord"), on_click=byt_flik, args=(pid, FLIKAR[1]))


def flik_nyckelord(pid, b, start, k):
    st.write("Skriv ett ord och tryck **Enter**. Lägg till en stjärna, som `ränt*`, för att få med räntan, räntor och räntehöjning.")

    def ordfalt(falt, etikett, platshallare, help=None):
        b[falt] = rensa_ord(st.multiselect(
            etikett, options=start[falt], default=start[falt], key=k(falt),
            accept_new_options=True, placeholder=platshallare, help=help))

    ordfalt("nyckelord", "Nyckelord som räcker ensamma för en träff", "Skriv ett nyckelord och tryck Enter")
    with st.expander("Avancerat: tvetydiga ord och kategorier"):
        ordfalt("tvetydiga_ord", "Tvetydiga ord", "T.ex. hammarby",
                "Ger bara träff om ett kontextord också finns. Bra för namn som kan betyda flera saker.")
        ordfalt("kontextord", "Kontextord", "T.ex. tränar*",
                "Bekräftar att ett tvetydigt ord handlar om rätt sak. Stjärna fungerar här också.")
        ordfalt("kategoriord", "Kategoriord", "T.ex. fotboll",
                "Matchas mot kategorierna som källan själv sätter på sina artiklar.")
    a, _, c = st.columns([1.3, 2, 1.6])
    a.button("← Källor", key=k("till_kallor"), on_click=byt_flik, args=(pid, FLIKAR[0]))
    return c.button("Kör bevakningen", type="primary", key=k("kor_ord"), width="stretch")


def flik_resultat(e, b, namn_fil):
    if e["resultat"] is None:
        har_kallor = bool(b["kallor"])
        har_ord = bool(b["nyckelord"]) or (har_kallor and not any(x["filtrera"] for x in b["kallor"]))
        steg = [(har_kallor, "Lägg till källor under Källor."), (har_ord, "Skriv in nyckelord under Nyckelord."),
                (False, "Tryck på Kör bevakningen uppe till höger.")]
        st.markdown("<div class='sektion'>Inga resultat än</div>", unsafe_allow_html=True)
        for i, (klar, text) in enumerate(steg, 1):
            st.markdown(f"{'~~' if klar else ''}**{i}.** {text}{'~~ klart' if klar else ''}")
        return

    df, statistik = e["resultat"]
    fel = int((statistik["Status"] != "OK").sum()) if not statistik.empty else 0
    med_traff = int((statistik["Träffar"] > 0).sum()) if not statistik.empty else 0

    topp, knappar = st.columns([3, 2], vertical_alignment="bottom")
    with topp:
        st.markdown(f"<div class='sektion' style='font-size:2rem;margin:.4rem 0 0'>"
                    f"{antal(len(df), 'träff', 'träffar') if len(df) else 'Inga träffar'}</div>", unsafe_allow_html=True)
        rad = f"Från {med_traff} av {antal(len(statistik), 'källa', 'källor')}." if len(df) else \
              "Prova fler nyckelord, en stjärna i slutet av orden eller fler källor."
        if fel:
            rad += f" {antal(fel, 'källa', 'källor')} gick inte att läsa, se nedan."
        st.caption(rad)
    if len(df):
        with knappar:
            k1, k2 = st.columns(2)
            k1.download_button("Ladda ner Excel", skapa_excel(df), f"{namn_fil}.xlsx", width="stretch")
            k2.download_button("Ladda ner Word", skapa_word(df, statistik, b["namn"]), f"{namn_fil}.docx", width="stretch")

    with st.expander("Så gick det per källa", expanded=fel > 0):
        rader = "".join(
            f"<tr><td>{esc(r['Källa'])}</td><td class='tal'>{r['Artiklar'] if r['Status'] == 'OK' else ''}</td>"
            f"<td class='tal'>{r['Träffar'] if r['Status'] == 'OK' else ''}</td>"
            f"<td class='{'ok' if r['Status'] == 'OK' else 'fel'}'>{esc(r['Status'])}</td></tr>"
            for r in statistik.to_dict("records"))
        st.markdown(f"<table class='stat'><tr><th>Källa</th><th class='tal'>Artiklar</th><th class='tal'>Träffar</th>"
                    f"<th>Status</th></tr>{rader}</table>", unsafe_allow_html=True)
    if not len(df):
        return

    s1, s2 = st.columns([3, 2], vertical_alignment="bottom")
    sok = s1.text_input("Sök bland träffarna", placeholder="Sök bland träffarna", label_visibility="collapsed")
    vy = s2.segmented_control("Visa", ["Per källa", "Senaste först"], default="Per källa",
                              label_visibility="collapsed") or "Per källa"
    visa = df
    if sok.strip():
        q = sok.strip().lower()
        visa = df[(df["Titel"] + " " + df["Sammanfattning"] + " " + df["Källa"]).str.lower().str.contains(q, regex=False)]

    def artikel(r, med_kalla):
        kalla = f"{esc(r['Källa'])}, " if med_kalla else ""
        ingress = "" if r["Sammanfattning"] == "Ingen sammanfattning" else \
            f"<p class='ingress'>{markera(r['Sammanfattning'], r['_monster'])}</p>"
        return (f"<div class='artikel'><a href='{esc(r['Länk'])}' target='_blank'>"
                f"{markera(r['Titel'] or '(utan rubrik)', r['_monster'])}</a>"
                f"<div class='meta'>{kalla}{r['Publicerad']}<span class='chip'>{esc(r['Matchande nyckelord'])}</span></div>"
                f"{ingress}</div>")

    if visa.empty:
        st.info("Inget matchar sökningen.")
    elif vy == "Senaste först":
        st.markdown("".join(artikel(r, True) for _, r in visa.sort_values("_tid", ascending=False).iterrows()),
                    unsafe_allow_html=True)
    else:
        delar = []
        for kalla in visa["Källa"].unique():
            grupp = visa[visa["Källa"] == kalla].sort_values("_tid", ascending=False)
            delar.append(f"<div class='grupp'>{esc(kalla)}<span>{antal(len(grupp), 'träff', 'träffar')}</span></div>")
            delar += [artikel(r, False) for _, r in grupp.iterrows()]
        st.markdown("".join(delar), unsafe_allow_html=True)


# =================== Sidomeny ===================
def sidomeny():
    with st.sidebar:
        st.markdown("<div class='logo'><span></span>Omvärldsbevakning</div>", unsafe_allow_html=True)
        st.button("Startsida", key="nav_start", width="stretch",
                  type="primary" if ss.aktiv is None else "secondary", on_click=ga_till, args=(None,))
        if ss.oppna:
            st.caption("Mina bevakningar")
            for pid, e in ss.oppna.items():
                namn = re.sub(r"([\\`*_\[\]<>#~:|])", r"\\\1", e["bev"]["namn"] or "Namnlös")
                st.button(f":{e['punkt']}[●]  {namn}", key=f"nav_{pid}", width="stretch",
                          type="primary" if pid == ss.aktiv else "secondary", on_click=ga_till, args=(pid,))
        st.button("+ Ny bevakning", key="nav_ny", type="tertiary", on_click=ga_till, args=(None,))
        st.divider()
        with st.expander("Öppna sparad bevakning"):
            hantera_fil(st.file_uploader("Välj fil", type="json", key="fil_meny", label_visibility="collapsed"))
        st.caption("Appen minns inte dina bevakningar när du stänger fliken. "
                   "Spara dem som fil under Namn, spara och stäng.")


if ss.aktiv not in ss.oppna:
    ss.aktiv = None
if ss.aktiv is None:
    ss.senast = None
    startsida()
else:
    bevakningssida(ss.aktiv)
sidomeny()
