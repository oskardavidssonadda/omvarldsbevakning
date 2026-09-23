import copy
import json
import re
from html import escape as html_escape

import pandas as pd
import streamlit as st

from bevakning import (ORDFALT, antal, hamta_nyheter, markera, normalisera, rensa_ord,
                       skapa_excel, skapa_word, tom_bevakning, vard)
from mallar import MALLAR

st.set_page_config(page_title="Omvärldsbevakning", page_icon="📰", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1300px;}
mark {background: #FFE27A; color: #15243A; padding: 0 .12em; border-radius: 2px;}
.artikel {padding: .8rem 0; border-top: 1px solid rgba(128,128,128,.25);}
.artikel a {font-weight: 600; font-size: 1.05rem; text-decoration: none; color: inherit;}
.artikel a:hover {text-decoration: underline;}
.meta {opacity: .7; font-size: .85rem; margin-top: .2rem;}
.chip {background: rgba(128,128,128,.15); border-radius: 999px; padding: .05rem .55rem; margin-left: .4rem;}
.ingress {opacity: .8; margin: .35rem 0 0; display: -webkit-box; -webkit-line-clamp: 3;
          -webkit-box-orient: vertical; overflow: hidden;}
.grupp {font-size: 1.15rem; font-weight: 700; margin: 1.8rem 0 .2rem;}
.grupp span {opacity: .6; font-weight: 400; font-size: .9rem; margin-left: .4rem;}
</style>
""", unsafe_allow_html=True)

ss = st.session_state
ss.setdefault("bev", None)       # aktuell bevakning
ss.setdefault("version", 0)      # byts när en ny bevakning laddas, så att fälten fylls om
ss.setdefault("resultat", None)


def ladda_bevakning(b):
    ss.bev = b
    ss.start = copy.deepcopy(b)  # fälten startar från den här
    ss.version += 1
    ss.resultat = None


# =================== Startsida ===================
if ss.bev is None:
    st.title("Vad vill du bevaka?")
    st.write("Börja från en färdig mall och ändra den som du vill, eller bygg din egen från grunden.")
    st.write("")

    kolumner = st.columns(len(MALLAR) + 1, gap="medium")
    for kol, m in zip(kolumner, MALLAR):
        with kol, st.container(border=True, height=250):
            st.markdown(f"#### {m['ikon']} {m['titel']}")
            st.write(m["text"])
            b = m["bevakning"]
            st.caption(f"{antal(len(b['kallor']), 'källa', 'källor')}, {antal(len(b['nyckelord']), 'nyckelord', 'nyckelord')}")
            if st.button("Använd mallen", key=f"mall_{m['titel']}", width="stretch"):
                ladda_bevakning(normalisera(copy.deepcopy(b)))
                st.rerun()
    with kolumner[-1], st.container(border=True, height=250):
        st.markdown("#### ✏️ Egen bevakning")
        st.write("Lägg in dina egna källor och nyckelord.")
        st.caption("Helt blank")
        if st.button("Börja från tomt", type="primary", width="stretch"):
            ladda_bevakning(tom_bevakning())
            st.rerun()

    st.write("")
    fil = st.file_uploader("Har du sparat en bevakning tidigare? Öppna den här.", type="json")
    if fil:
        try:
            ladda_bevakning(normalisera(json.load(fil)))
            st.rerun()
        except Exception:
            st.error("Filen gick inte att läsa. Välj en fil som sparats med Spara bevakningen.")
    st.stop()


# =================== Arbetsyta ===================
b, start, v = ss.bev, ss.start, ss.version

with st.sidebar:
    st.subheader("Din bevakning")
    st.write("Appen minns inte din bevakning till nästa gång. Spara den som fil och öppna den när du kommer tillbaka.")
    namn_fil = re.sub(r"[^\w]+", "_", b["namn"] or "bevakning").strip("_")
    st.download_button("💾 Spara bevakningen", json.dumps(b, ensure_ascii=False, indent=2),
                       file_name=f"{namn_fil}.json", mime="application/json", width="stretch")
    if st.button("↩ Välj en annan bevakning", width="stretch"):
        ss.bev = None
        st.rerun()

vanster, hoger = st.columns([5, 7], gap="large")

with vanster:
    b["namn"] = st.text_input("Namn på bevakningen", value=start["namn"], key=f"namn_{v}").strip()

    # ----- Källor -----
    with st.container(border=True):
        st.subheader("Källor")
        st.caption("Klicka på en tom rad längst ner för att lägga till en källa. Bocka i **Filtrera** för breda "
                   "nyhetssajter, och lämna den tom för källor som redan handlar om ditt ämne.")
        tabell = pd.DataFrame(start["kallor"] or [], columns=["namn", "url", "filtrera"])
        redigerad = st.data_editor(
            tabell, key=f"kallor_{v}", num_rows="dynamic", hide_index=True, width="stretch",
            column_order=["namn", "filtrera", "url"],
            column_config={
                "namn": st.column_config.TextColumn("Namn", help="Valfritt. Blir sajtens adress om du lämnar tomt."),
                "url": st.column_config.TextColumn("RSS-länk", required=True),
                "filtrera": st.column_config.CheckboxColumn("Filtrera", default=True, width="small",
                                                            help="Bara artiklar som matchar dina nyckelord"),
            })
        kallor, ogiltiga = [], []
        for rad in redigerad.to_dict("records"):
            url = str(rad.get("url") or "").strip()
            if not url:
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

    # ----- Nyckelord -----
    with st.container(border=True):
        st.subheader("Nyckelord")
        st.caption("Skriv ett ord och tryck **Enter**. Skriv `ränt*` för att få med räntan, räntor och räntehöjning.")

        def ordfalt(falt, etikett, platshallare, help=None):
            b[falt] = rensa_ord(st.multiselect(
                etikett, options=start[falt], default=start[falt], key=f"{falt}_{v}",
                accept_new_options=True, placeholder=platshallare, help=help))

        ordfalt("nyckelord", "Räcker ensamma för en träff", "Skriv ett nyckelord…")
        with st.expander("Avancerat"):
            ordfalt("tvetydiga_ord", "Tvetydiga ord", "T.ex. hammarby",
                    "Ger bara träff om ett kontextord också finns. Bra för namn som kan betyda flera saker.")
            ordfalt("kontextord", "Kontextord", "T.ex. tränare",
                    "Bekräftar att ett tvetydigt ord handlar om rätt sak.")
            ordfalt("kategoriord", "Kategoriord", "T.ex. fotboll",
                    "Matchas mot kategorierna som källan själv sätter på sina artiklar.")

    kor = st.button("▶ Kör bevakningen", type="primary", width="stretch", disabled=not b["kallor"])
    if not b["kallor"]:
        st.caption("Lägg till minst en källa för att kunna köra.")

if kor:
    with hoger, st.spinner(f"Hämtar {antal(len(b['kallor']), 'källa', 'källor')}…"):
        ss.resultat = hamta_nyheter(b)

# ----- Resultat -----
with hoger:
    if ss.resultat is None:
        st.subheader("Redo när du är")
        har_kallor = bool(b["kallor"])
        har_ord = bool(b["nyckelord"]) or (har_kallor and not any(k["filtrera"] for k in b["kallor"]))
        st.markdown(
            f"{'✅' if har_kallor else '1️⃣'} Lägg till källor, alltså RSS-länkar till sajter du vill bevaka.\n\n"
            f"{'✅' if har_ord else '2️⃣'} Skriv in nyckelorden som ska ge träff.\n\n"
            "3️⃣ Tryck på **Kör bevakningen**. Sedan kan du ladda ner allt som Excel eller Word.")
        st.stop()

    df, statistik = ss.resultat
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
            k2.download_button("Word", skapa_word(df, statistik, b["namn"] or "Omvärldsbevakning"),
                               f"{namn_fil}.docx", width="stretch", icon="📄")

    with st.expander("Så gick det per källa", expanded=fel > 0):
        st.dataframe(statistik, hide_index=True, width="stretch")

    if len(df):
        s1, s2 = st.columns([3, 2], vertical_alignment="bottom")
        sok = s1.text_input("Sök bland träffarna", placeholder="Sök bland träffarna", label_visibility="collapsed")
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
