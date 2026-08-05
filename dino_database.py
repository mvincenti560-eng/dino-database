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
    
    # Rilevamento automatico colonne geografiche
    col_regione = 'region' if 'region' in df.columns else 'continent' if 'continent' in df.columns else None
    col_paese = 'country' if 'country' in df.columns else 'cc' if 'cc' in df.columns else None
    
    df_filtered = df.copy()
    
    # Filtri geografici collegati
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

    # Lista dinosauri filtrati
    dino_list = sorted(df_filtered['name'].dropna().unique())
    
    if len(dino_list) == 0:
        st.warning("Nessun dinosauro trovato con i filtri selezionati.")
    else:
        # Gestione estrazione casuale diretta
        if 'selected_dino' not in st.session_state or st.session_state.selected_dino not in dino_list:
            st.session_state.selected_dino = dino_list[0]

        # Layout Selezione + Tasto Casuale
        col_select, col_btn = st.columns([3, 1])
        
        with col_btn:
            st.write("") # Spaziatore verticale per allineare al menu
            st.write("")
            if st.button("🎲 Pescane uno a caso!"):
                st.session_state.selected_dino = random.choice(dino_list)

        with col_select:
            selected_dino = st.selectbox(
                "Cerca o seleziona un dinosauro:", 
                dino_list, 
                index=dino_list.index(st.session_state.selected_dino) if st.session_state.selected_dino in dino_list else 0,
                key="dino_select"
            )
            # Aggiorna lo stato se l'utente cambia manualmente la selezione
            st.session_state.selected_dino = selected_dino

        # Scheda del dinosauro selezionato
        if selected_dino:
            dino_data = df_filtered[df_filtered['name'] == selected_dino].iloc[0]
            
            st.subheader(f"Scheda Informativa: {selected_dino}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                country_val = dino_data.get(col_paese, 'N/D') if col_paese else 'N/D'
                if pd.isna(country_val) or str(country_val).strip() == '':
                    country_val = "Non registrato"
                st.write(f"🌍 **Nazione del ritrovamento:** {country_val}")
                st.write(f"📍 **Località:** {dino_data.get('locality', 'N/D')}")
                
            with col2:
                st.write(f"⏳ **Intervallo temporale:** {dino_data.get('interval', 'N/D')}")
                lat = dino_data.get('lat', 'N/D')
                lng = dino_data.get('lng', 'N/D')
                st.write(f"🧭 **Coordinate geografiche:** Lat: {lat}, Lng: {lng}")

            # Reindirizzamento diretto a The Dinosaur Database
            query_encoded = urllib.parse.quote(selected_dino)
            dino_db_url = f"https://dinosaurpictures.org/{query_encoded}"
            
            st.markdown("---")
            st.markdown(f"👉 [**Cerca {selected_dino} su The Dinosaur Database**]({dino_db_url})", unsafe_allow_html=True)
        
