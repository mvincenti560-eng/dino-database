import streamlit as st
import pandas as pd
import random
import urllib.parse

st.set_page_config(page_title="Dino Database Interattivo", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("pbdb_data (1).csv", skiprows=16)
        
        if 'accepted_name' in df.columns:
            df = df.dropna(subset=['accepted_name'])
            df['name'] = df['accepted_name']
        elif 'identified_name' in df.columns:
            df = df.dropna(subset=['identified_name'])
            df['name'] = df['identified_name']
        else:
            return pd.DataFrame()
            
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Il database è vuoto o il file CSV non è stato letto correttamente.")
else:
    st.title("🦖 Database interattivo dei Dinosauri")
    
    # --- FILTRI GEOGRAFICI A CASCATA ---
    df_filtered = df.copy()
    
    col_regione = 'region' if 'region' in df.columns else 'continent' if 'continent' in df.columns else None
    col_paese = 'country' if 'country' in df.columns else 'cc' if 'cc' in df.columns else None
    
    st.subheader("🔍 Filtri Geografici")
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        if col_regione:
            regioni = sorted(df_filtered[col_regione].dropna().astype(str).unique())
            seleziona_regione = st.selectbox("🌍 Filtra per Regione/Continente:", ["Tutte"] + list(regioni))
            if seleziona_regione != "Tutte":
                df_filtered = df_filtered[df_filtered[col_regione] == seleziona_regione]
                
    with f_col2:
        if col_paese:
            paesi = sorted(df_filtered[col_paese].dropna().astype(str).unique())
            seleziona_paese = st.selectbox("🏳️ Filtra per Paese:", ["Tutti"] + list(paesi))
            if seleziona_paese != "Tutti":
                df_filtered = df_filtered[df_filtered[col_paese] == seleziona_paese]

    st.markdown("---")
    
    # --- TABELLA RISULTATI FILTRATI ---
    st.subheader(f"📊 Tabella Dinosauri Trovati ({len(df_filtered)})")
    
    cols_to_display = ['name']
    if col_regione and col_regione in df_filtered.columns:
        cols_to_display.append(col_regione)
    if col_paese and col_paese in df_filtered.columns:
        cols_to_display.append(col_paese)
    if 'locality' in df_filtered.columns:
        cols_to_display.append('locality')
        
    st.dataframe(df_filtered[cols_to_display], use_container_width=True)
    
    # --- SCHEDA DETTAGLIATA CON VALORI MULTIPLI ---
    dino_list = sorted(df_filtered['name'].dropna().unique())
    
    if dino_list:
        st.markdown("---")
        selected_dino = st.selectbox("🦕 Seleziona un dinosauro per la scheda dettagliata:", dino_list)
        
        if selected_dino:
            # Raccogliamo TUTTI i record di questo dinosauro nel database
            all_dino_rows = df[df['name'] == selected_dino]
            
            st.subheader(f"Scheda Informativa Completa: {selected_dino}")
            
            # 1. Estrazione di tutti i Continenti/Regioni unici
            if col_regione and col_regione in all_dino_rows.columns:
                regioni_unisc = all_dino_rows[col_regione].dropna().astype(str).unique()
                regioni_str = ", ".join(regioni_unisc) if len(regioni_unisc) > 0 else "Non registrato"
            else:
                regioni_str = "N/D"

            # 2. Estrazione di tutti i Paesi unici
            if col_paese and col_paese in all_dino_rows.columns:
                paesi_unici = all_dino_rows[col_paese].dropna().astype(str).unique()
                paesi_str = ", ".join(paesi_unici) if len(paesi_unici) > 0 else "Non registrato"
            else:
                paesi_str = "N/D"

            # 3. Estrazione degli intervalli temporali unici
            intervalli_unici = all_dino_rows['interval'].dropna().astype(str).unique() if 'interval' in all_dino_rows.columns else []
            intervallo_str = ", ".join(intervalli_unici) if len(intervalli_unici) > 0 else "N/D"

            # 4. Estrazione delle località (mostra le prime 5 se ce ne sono tante)
            localita_uniche = all_dino_rows['locality'].dropna().astype(str).unique() if 'locality' in all_dino_rows.columns else []
            if len(localita_uniche) > 5:
                localita_str = ", ".join(localita_uniche[:5]) + f" (e altre {len(localita_uniche)-5} località...)"
            elif len(localita_uniche) > 0:
                localita_str = ", ".join(localita_uniche)
            else:
                localita_str = "N/D"

            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.write(f"🗺️ **Continente/i - Regione/i:** {regioni_str}")
                st.write(f"🌍 **Paese/i del ritrovamento:** {paesi_str}")
                st.write(f"📍 **Località note:** {localita_str}")
                
            with info_col2:
                st.write(f"⏳ **Intervallo/i temporale/i:** {intervallo_str}")
                st.write(f"🦴 **Numero totale di fossili/ritrovamenti registrati:** {len(all_dino_rows)}")

            # Link di reindirizzamento a The Dinosaur Database
            query_encoded = urllib.parse.quote(selected_dino)
            dino_db_url = f"https://dinosaurpictures.org/{query_encoded}"
            
            st.markdown("---")
            st.markdown(f"👉 [**Cerca {selected_dino} su The Dinosaur Database**]({dino_db_url})", unsafe_allow_html=True)

    # --- BOTTONE CASUALE ---
    st.markdown("---")
    if st.button("🎲 Pescane uno a caso!"):
        all_dinos = sorted(df['name'].dropna().unique())
        random_dino = random.choice(all_dinos)
        st.info(f"Abbiamo estratto: **{random_dino}**!")
    
