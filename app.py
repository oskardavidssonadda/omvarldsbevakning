import copy
import json
import re
import uuid
from datetime import datetime
from html import escape as html_escape

import pandas as pd
import streamlit as st

from bevakning import (antal, hamta_nyheter, markera, normalisera, rensa_ord,
                       skapa_excel, skapa_word, tom_bevakning, vard)
from mallar import MALLAR

st.set_page_config(page_title="Omvärldsbevakning", page_icon="📰", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container {padding-top: 2.2rem; max-width: 1250px;}
[data-testid="stBaseButton-primary"] {background:#15243A; border-color:#15243A; color:#fff;}
[data-testid="stBaseButton-primary"]:hover {background:#24395A; border-color:#24395A; color:#fff;}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {justify-content:flex-start;}
mark {background:#FFE27A; color:#15243A; padding:0 .12em; border-radius:2px;}
.artikel {padding:.8rem 0; border-top:1px solid rgba(128,128,128,.25);}
.artikel a {font-weight:600; font-size:1.05rem; text-decoration:none; color:inherit;}
.artikel a:hover {text-decoration:underline;}
.meta {opacity:.7; font-size:.85rem; margin-top:.2rem;}
.chip {background:rgba(128,128,128,.15); border-radius:999px; padding:.05rem .55rem; margin-left:.4rem;}
.ingress {opacity:.8; margin:.35rem 0 0; display:-webkit-box; -webkit-line-clamp:3;
          -webkit-box-orient:vertical; overflow:hidden;}
.grupp {font-size:1.15rem; font-weight:700; margin:1.8rem 0 .2rem;}
.grupp span {opacity:.6; font-weight:400; font-size:.9rem; margin-left:.4rem;}
.stTabs [data-baseweb="tab"] {font-size:1rem; padding:.4rem .9rem;}
</style>
""", unsafe_allow_html=True)

FLIKAR = ["📡 Källor", "🔑 Nyckelord", "📰 Resultat"]
ss = st.session_state
ss.setdefault("oppna", {})     # id -> öppen bevakning med resultat
ss.setdefault("aktiv", None)   # None = startsidan
ss.setdefault("senast", None)  # vilken bevakning som ritades senast


# =================== Navigering ===================
def oppna_ny(bev, ikon, mall=None):
    pid = uuid.uuid4().hex[:8]
    ss.oppna[pid] = {"bev": bev, "start": copy.deepcopy(bev), "version": 0,
                     "resultat": None, "kortid": None, "ikon": ikon, "mall": mall}
    ss.aktiv = pid


def ga_till(pid):
    ss.aktiv = pid


def oppna_mall(m):
    oppna_ny(normalisera(copy.deepcopy(m["bevakning"])), m["ikon"], m["titel"])


def stang(pid):
    ss.oppna.pop(pid, None)
    ss.aktiv = None


def byt_flik(pid, flik):
    ss[f"flikmal_{pid}"] = flik


def hantera_fil(fil):
    if fil and ss.get("senast_fil") != fil.file_id:
        ss.senast_fil = fil.file_id
        try:
            oppna_ny(normalisera(json.load(fil)), "📂")
            st.rerun()
        except (ValueError, AttributeError):
            st.error("Filen gick inte att läsa. Välj en fil som sparats från appen.")


def sammanfattning(b):
    return f"{antal(len(b['kallor']), 'källa', 'källor')}, {antal(len(b['nyckelord']), 'nyckelord', 'nyckelord')}"


# =================== Startsida ===================
def startsida():
    st.title("Vad vill du bevaka?")
    st.write("Välj en färdig mall och ändra den som du vill, eller bygg en egen från grunden.")

    if ss.oppna:
        st.subheader("Fortsätt där du var")
        kol = st.columns(4, gap="medium")
        for i, (pid, e) in enumerate(ss.oppna.items()):
            with kol[i % 4], st.container(border=True):
                st.markdown(f"**{e['ikon']} {html_escape(e['bev']['namn'] or 'Namnlös')}**")
                st.caption(sammanfattning(e["bev"]) + (f", körd {e['kortid']}" if e["kortid"] else ""))
                st.button("Fortsätt", icon="➡️", key=f"fortsatt_{pid}", width="stretch", on_click=ga_till, args=(pid,))
        st.subheader("Eller börja på en ny")

    kol = st.columns(len(MALLAR) + 1, gap="medium")
    for k, m in zip(kol, MALLAR):
        redan = next((pid for pid, e in ss.oppna.items() if e["mall"] == m["titel"]), None)
        with k, st.container(border=True, height=260):
            st.markdown(f"#### {m['ikon']} {m['titel']}")
            st.write(m["text"])
            st.caption(sammanfattning(m["bevakning"]))
            if redan:
                st.button("Redan öppen, gå dit", key=f"mall_{m['titel']}", width="stretch", on_click=ga_till, args=(redan,))
            else:
                st.button("Använd mallen", key=f"mall_{m['titel']}", width="stretch", type="primary",
                          on_click=oppna_mall, args=(m,))
    with kol[-1], st.container(border=True, height=260):
        st.markdown("#### ✏️ Egen")
        st.write("Börja helt blankt med dina egna källor och nyckelord.")
        st.caption("Tom bevakning")
        st.button("Skapa egen", key="mall_egen", width="stretch", type="primary",
                  on_click=oppna_ny, args=(tom_bevakning(), "✏️"))

    st.write("")
    with st.expander("📂 Har du sparat en bevakning tidigare? Öppna den här"):
        hantera_fil(st.file_uploader("Välj fil", type="json", key="fil_start", label_visibility="collapsed"))


# =================== Bevakningssida ===================
def bevakningssida(pid):
    e = ss.oppna[pid]
    if ss.senast != pid:
        # Fälten återskapas från senaste läget när man kommer tillbaka till en bevakning
        e["start"] = copy.deepcopy(e["bev"])
        e["version"] += 1
        ss.senast = pid
    b, start, v = e["bev"], e["start"], e["version"]
    k = lambda n: f"{pid}_{n}_{v}"
    namn_fil = re.sub(r"[^\w]+", "_", b["namn"] or "bevakning").strip("_")

    st.button("Alla bevakningar och mallar", icon="⬅️", type="tertiary", on_click=ga_till, args=(None,))
    titel, kor_kol, mer = st.columns([7, 2.2, 1.3], vertical_alignment="center")
    with mer, st.popover("Mer", icon="⚙️", width="stretch"):
        b["namn"] = st.text_input("Namn på bevakningen", start["namn"], key=k("namn")).strip() or "Namnlös bevakning"
        st.download_button("Spara som fil", json.dumps(b, ensure_ascii=False, indent=2), f"{namn_fil}.json",
                           mime="application/json", icon="💾", width="stretch")
        st.caption("Spara filen om du vill kunna öppna bevakningen igen en annan dag.")
        st.divider()
        st.button("Stäng bevakningen", icon="✖️", width="stretch", on_click=stang, args=(pid,))
        st.caption("Ändringar som inte sparats försvinner.")
    with titel:
        st.markdown(f"# {e['ikon']} {html_escape(b['namn'])}")
        st.caption(sammanfattning(b) + (f", senast körd {e['kortid']}" if e["kortid"] else ""))
    with kor_kol:
        kor_topp = st.button("Kör bevakningen", icon="▶️", type="primary", width="stretch", key=k("kor_topp"))
    plats = st.empty()

    flikkey = k("flikar")
    if f"flikmal_{pid}" in ss:
        ss[flikkey] = ss.pop(f"flikmal_{pid}")
    elif flikkey not in ss:
        ss[flikkey] = FLIKAR[2] if e["resultat"] is not None else FLIKAR[0]
    t_kallor, t_ord, t_res = st.tabs(FLIKAR, key=flikkey, on_change="rerun")

    # ----- Källor -----
    with t_kallor:
        st.caption("Klicka på den tomma raden längst ner för att lägga till en källa. Bocka i **Filtrera** för breda "
                   "nyhetssajter och lämna den tom för källor som redan handlar om ditt ämne.")
        tabell = pd.DataFrame(start["kallor"] or [], columns=["namn", "url", "filtrera"])
        redigerad = st.data_editor(
            tabell, key=k("kallor"), num_rows="dynamic", hide_index=True, width="stretch",
            column_order=["namn", "filtrera", "url"],
            column_config={
                "namn": st.column_config.TextColumn("Namn", help="Valfritt. Blir sajtens adress om du lämnar tomt."),
                "filtrera": st.column_config.CheckboxColumn("Filtrera", default=True, width="small",
                                                            help="Bara artiklar som matchar dina nyckelord"),
                "url": st.column_config.TextColumn("RSS-länk", required=True),
            })
        kallor, ogiltiga = [], []
        for rad in redigerad.to_dict("records"):
            url = str(rad.get("url") or "").strip()
            if not url or url == "None":
                continue
            if not url.lower().startswith(("http://", "https://")):
                url = "https://" + url
            if " " in url or "." not in (vard(url) or ""):
                ogiltiga.append(url)
                continue
            namn = str(rad.get("namn") or "").strip()
            kallor.append({"namn": namn if namn and namn != "None" else vard(url), "url": url,
                           "filtrera": rad.get("filtrera") is not False})
        b["kallor"] = kallor
        if ogiltiga:
            st.warning("De här ser inte ut som webbadresser och hoppas över: " + ", ".join(ogiltiga))
        with st.expander("Hittar du ingen RSS-länk?"):
            st.write("Sök på sajtens namn och **RSS**. Många sajter har också flödet på adressen med "
                     "`/rss` eller `/feed` i slutet, till exempel `https://sajt.se/feed`.")
        st.button("Nästa: Nyckelord", icon="➡️", key=k("till_ord"), on_click=byt_flik, args=(pid, FLIKAR[1]))

    # ----- Nyckelord -----
    with t_ord:
        st.caption("Skriv ett ord och tryck **Enter**. Skriv `ränt*` för att få med räntan, räntor och räntehöjning.")

        def ordfalt(falt, etikett, platshallare, help=None):
            b[falt] = rensa_ord(st.multiselect(
                etikett, options=start[falt], default=start[falt], key=k(falt),
                accept_new_options=True, placeholder=platshallare, help=help))

        ordfalt("nyckelord", "Räcker ensamma för en träff", "Skriv ett nyckelord…")
        with st.expander("Avancerat: tvetydiga ord och kategorier"):
            ordfalt("tvetydiga_ord", "Tvetydiga ord", "T.ex. hammarby",
                    "Ger bara träff om ett kontextord också finns. Bra för namn som kan betyda flera saker.")
            ordfalt("kontextord", "Kontextord", "T.ex. tränare",
                    "Bekräftar att ett tvetydigt ord handlar om rätt sak.")
            ordfalt("kategoriord", "Kategoriord", "T.ex. fotboll",
                    "Matchas mot kategorierna som källan själv sätter på sina artiklar.")
        a, bb = st.columns([1, 1])
        a.button("Källor", icon="⬅️", key=k("till_kallor"), on_click=byt_flik, args=(pid, FLIKAR[0]))
        kor_ord = bb.button("Kör bevakningen", icon="▶️", type="primary", key=k("kor_ord"), width="stretch")

    # ----- Resultat -----
    with t_res:
        visa_resultat(e, b, namn_fil)

    # ----- Kör -----
    if kor_topp or kor_ord:
        if not b["kallor"]:
            plats.warning("Lägg till minst en källa under **Källor** först.")
        else:
            with plats, st.spinner(f"Hämtar {antal(len(b['kallor']), 'källa', 'källor')}…"):
                e["resultat"] = hamta_nyheter(b)
            e["kortid"] = datetime.now().strftime("%H:%M")
            byt_flik(pid, FLIKAR[2])
            st.rerun()


def visa_resultat(e, b, namn_fil):
    if e["resultat"] is None:
        har_kallor = bool(b["kallor"])
        har_ord = bool(b["nyckelord"]) or (har_kallor and not any(k["filtrera"] for k in b["kallor"]))
        st.subheader("Inga resultat än")
        st.markdown(
            f"{'✅' if har_kallor else '1️⃣'} Lägg till källor under **Källor**.\n\n"
            f"{'✅' if har_ord else '2️⃣'} Skriv in nyckelord under **Nyckelord**.\n\n"
            "3️⃣ Tryck på **Kör bevakningen** uppe till höger.")
        return

    df, statistik = e["resultat"]
    fel = int((statistik["Status"] != "OK").sum()) if not statistik.empty else 0
    med_traff = int((statistik["Träffar"] > 0).sum()) if not statistik.empty else 0

    topp, knappar = st.columns([3, 2], vertical_alignment="bottom")
    with topp:
        st.subheader(antal(len(df), "träff", "träffar") if len(df) else "Inga träffar")
        rad = f"Från {med_traff} av {antal(len(statistik), 'källa', 'källor')}." if len(df) else \
              "Prova fler nyckelord, en stjärna i slutet av orden eller fler källor."
        if fel:
            rad += f" {antal(fel, 'källa', 'källor')} gick inte att läsa, se nedan."
        st.caption(rad)
    if len(df):
        with knappar:
            k1, k2 = st.columns(2)
            k1.download_button("Excel", skapa_excel(df), f"{namn_fil}.xlsx", width="stretch", icon="📊")
            k2.download_button("Word", skapa_word(df, statistik, b["namn"]), f"{namn_fil}.docx", width="stretch", icon="📄")

    with st.expander("Så gick det per källa", expanded=fel > 0):
        st.dataframe(statistik, hide_index=True, width="stretch")
    if not len(df):
        return

    s1, s2 = st.columns([3, 2], vertical_alignment="bottom")
    sok = s1.text_input("Sök bland träffarna", placeholder="🔍 Sök bland träffarna", label_visibility="collapsed")
    vy = s2.segmented_control("Visa", ["Per källa", "Senaste först"], default="Per källa",
                              label_visibility="collapsed") or "Per källa"
    visa = df
    if sok.strip():
        q = sok.strip().lower()
        visa = df[(df["Titel"] + " " + df["Sammanfattning"] + " " + df["Källa"]).str.lower().str.contains(q, regex=False)]

    def artikel(r, med_kalla):
        kalla = f"{html_escape(r['Källa'])}, " if med_kalla else ""
        ingress = "" if r["Sammanfattning"] == "Ingen sammanfattning" else \
            f"<p class='ingress'>{markera(r['Sammanfattning'], r['_monster'])}</p>"
        return (f"<div class='artikel'><a href='{html_escape(r['Länk'])}' target='_blank'>"
                f"{markera(r['Titel'] or '(utan rubrik)', r['_monster'])}</a>"
                f"<div class='meta'>{kalla}{r['Publicerad']}<span class='chip'>{html_escape(r['Matchande nyckelord'])}</span></div>"
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
            delar.append(f"<div class='grupp'>{html_escape(kalla)}<span>{antal(len(grupp), 'träff', 'träffar')}</span></div>")
            delar += [artikel(r, False) for _, r in grupp.iterrows()]
        st.markdown("".join(delar), unsafe_allow_html=True)


# =================== Sidomeny ===================
def sidomeny():
    with st.sidebar:
        st.markdown("### 📰 Omvärldsbevakning")
        st.button("Startsida", icon="🏠", key="nav_start", width="stretch",
                  type="primary" if ss.aktiv is None else "secondary", on_click=ga_till, args=(None,))
        if ss.oppna:
            st.caption("Mina bevakningar")
            for pid, e in ss.oppna.items():
                st.button(e["bev"]["namn"] or "Namnlös", icon=e["ikon"], key=f"nav_{pid}", width="stretch",
                          type="primary" if pid == ss.aktiv else "secondary", on_click=ga_till, args=(pid,))
        st.button("Ny bevakning", icon="➕", key="nav_ny", type="tertiary", on_click=ga_till, args=(None,))
        st.divider()
        with st.expander("📂 Öppna sparad bevakning"):
            hantera_fil(st.file_uploader("Välj fil", type="json", key="fil_meny", label_visibility="collapsed"))
        st.caption("Appen minns inte dina bevakningar när du stänger fliken. Spara dem som fil via **Mer** på varje bevakning.")


# =================== Kör appen ===================
if ss.aktiv not in ss.oppna:
    ss.aktiv = None
if ss.aktiv is None:
    ss.senast = None
    startsida()
else:
    bevakningssida(ss.aktiv)
sidomeny()
