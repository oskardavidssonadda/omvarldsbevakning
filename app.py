import json
from datetime import date

import streamlit as st

from bevakning import (hamta_nyheter, kallor_till_text, las_kallor, las_ord,
                       skapa_excel, skapa_word)

st.set_page_config(page_title="Omvärldsbevakning", page_icon="📰", layout="wide")

with open("exempel_fotboll.json", encoding="utf-8") as f:
    EXEMPEL = json.load(f)

# ---------- Sidopanel: spara och ladda bevakningar ----------
st.sidebar.header("Din bevakning")
st.sidebar.write("Ladda upp en bevakning du sparat tidigare, eller börja från exemplet.")
uppladdad = st.sidebar.file_uploader("Sparad bevakning (.json)", type="json")
inst = json.load(uppladdad) if uppladdad else EXEMPEL
v = f"{uppladdad.name}_{uppladdad.size}" if uppladdad else "exempel"  # nya fält vid ny fil

# ---------- Inställningar ----------
st.title("Omvärldsbevakning")
rubrik = st.text_input("Namn på bevakningen", inst.get("rubrik", ""), key=f"rubrik_{v}")

vanster, hoger = st.columns(2)
with vanster:
    st.subheader("Källor")
    st.caption("En källa per rad i formatet: Namn | RSS-länk")
    rena = st.text_area("Ta med alla artiklar från",
                        kallor_till_text(inst["rena_kallor"]), height=180, key=f"rena_{v}")
    blandade = st.text_area("Ta bara med artiklar som matchar nyckelorden",
                            kallor_till_text(inst["blandade_kallor"]), height=180, key=f"bland_{v}")

with hoger:
    st.subheader("Nyckelord")
    st.caption("Ett ord eller en fras per rad. Stora och små bokstäver spelar ingen roll.")
    nyckelord = st.text_area("Räcker ensamma för en träff",
                             "\n".join(inst["nyckelord"]), height=180, key=f"nyck_{v}")
    with st.expander("Avancerat: tvetydiga ord och kategorier"):
        tvetydiga = st.text_area("Tvetydiga ord (ger träff bara tillsammans med ett kontextord)",
                                 "\n".join(inst["tvetydiga_ord"]), key=f"tvet_{v}")
        kontextord = st.text_area("Kontextord",
                                  "\n".join(inst["kontextord"]), key=f"kont_{v}")
        kategoriord = st.text_area("Kategoriord (matchas mot RSS-flödets egna kategorier)",
                                   "\n".join(inst["kategoriord"]), key=f"kat_{v}")

aktuell = {
    "rubrik": rubrik,
    "rena_kallor": las_kallor(rena),
    "blandade_kallor": las_kallor(blandade),
    "nyckelord": las_ord(nyckelord),
    "tvetydiga_ord": las_ord(tvetydiga),
    "kontextord": las_ord(kontextord),
    "kategoriord": las_ord(kategoriord),
}

st.sidebar.download_button(
    "Spara bevakningen",
    json.dumps(aktuell, ensure_ascii=False, indent=2),
    file_name=f"bevakning_{rubrik or 'ny'}.json".replace(" ", "_"),
    mime="application/json",
)

# ---------- Kör ----------
if st.button("Kör bevakningen", type="primary"):
    if not aktuell["rena_kallor"] and not aktuell["blandade_kallor"]:
        st.warning("Lägg till minst en källa i formatet Namn | RSS-länk.")
    else:
        with st.spinner("Hämtar och filtrerar artiklar..."):
            st.session_state["resultat"] = hamta_nyheter(aktuell)
            st.session_state["rubrik"] = rubrik or "Omvärldsbevakning"

# Resultatet ligger i session_state så att det inte försvinner när man klickar på en nedladdning
if "resultat" in st.session_state:
    df, statistik = st.session_state["resultat"]

    with st.expander("Träffar per källa", expanded=df.empty):
        st.dataframe(statistik, hide_index=True, use_container_width=True)

    if df.empty:
        st.info("Inga träffar just nu. Prova fler nyckelord eller fler källor.")
    else:
        st.success(f"{len(df)} träffar")
        idag = date.today()
        k1, k2 = st.columns(2)
        k1.download_button("Ladda ner Excel", skapa_excel(df),
                           f"omvarldsbevakning_{idag}.xlsx", use_container_width=True)
        k2.download_button("Ladda ner Word", skapa_word(df, statistik, st.session_state["rubrik"]),
                           f"sammanfattning_{idag}.docx", use_container_width=True)
        st.dataframe(df, hide_index=True, use_container_width=True,
                     column_config={"Länk": st.column_config.LinkColumn("Länk")})
