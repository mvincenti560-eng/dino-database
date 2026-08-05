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
    
    st.subheader("Filtri di ricerca")
    
    # --- RIPARAZIONE FILTRI GEOGRAFICI A CASCATA ---
    df_filtered = df.copy()
    
    # Rilevamento automatico delle colonne geografiche dal tuo CSV
    col_regione = 'region' if 'region' in df.columns else 'continent' if 'continent' in df.columns else 'state' if 'state' in df.columns else None
    col_paese = 'country' if 'country' in df.columns else 'cc' if 'cc' in df.columns else None
    
    col1, col2 = st.columns(2)
    
    with col1:
        if col_regione:
            regioni = sorted(df_filtered[col_regione].dropna().astype(str).unique())
            seleziona_regione = st.selectbox("🌍 Filtra per Regione:", ["Tutte"] + list(regioni))
            
            # Applica il filtro della regione
            if seleziona_regione != "Tutte":
                df_filtered = df_filtered[df_filtered[col_regione] == seleziona_regione]
                
    with col2:
        if col_paese:
            # La genialata è qui: calcoliamo i Paesi SOLO DOPO aver filtrato la Regione!
            paesi = sorted(df_filtered[col_paese].dropna().astype(str).unique())
            seleziona_paese = st.selectbox("🏳️ Filtra per Paese:", ["Tutti"] + list(paesi))
            
            # Applica il filtro del paese
            if seleziona_paese != "Tutti":
                df_filtered = df_filtered[df_filtered[col_paese] == seleziona_paese]
    
    st.markdown("---")
    
    # --- SELEZIONE E SCHEDA DINOSAURO ---
    dino_list = sorted(df_filtered['name'].dropna().unique())
    
    if len(dino_list) == 0:
        st.warning("Nessun dinosauro trovato in questa specifica area. Prova ad allargare i filtri!")
    else:
        selected_dino = st.selectbox("🦕 Seleziona un dinosauro:", dino_list)
        
        if selected_dino:
            dino_data = df_filtered[df_filtered['name'] == selected_dino].iloc[0]
            
            st.subheader(f"Scheda Informativa: {selected_dino}")
            
            # Informazioni (Senza Dieta)
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.write(f"**Gruppo/Epoca:** {dino_data.get('early_interval', 'Non specificato')}")
                country_str = dino_data.get(col_paese, 'N/D') if col_paese else 'N/D'
                if pd.isna(country_str) or str(country_str).strip() == '':
                    country_str = "Non registrato"
                st.write(f"🌍 **Nazione del ritrovamento:** {country_str}")
                st.write(f"📍 **Località:** {dino_data.get('locality', 'N/D')}")
                
            with info_col2:
                st.write(f"⏳ **Intervallo temporale:** {dino_data.get('interval', 'N/D')}")
                lat = dino_data.get('lat', 'N/D')
                lng = dino_data.get('lng', 'N/D')
                st.write(f"🧭 **Coordinate:** Lat: {lat}, Lng: {lng}")

            # --- REINDIRIZZAMENTO A THE DINOSAUR DATABASE ---
            query_encoded = urllib.parse.quote(selected_dino)
            dino_db_url = f"https://dinosaurpictures.org/{query_encoded}"
            
            st.markdown("---")
            st.markdown(f"👉 [**Cerca {selected_dino} su The Dinosaur Database**]({dino_db_url})", unsafe_allow_html=True)

    # --- ESTRAZIONE CASUALE TOTALE ---
    st.markdown("---")
    if st.button("🎲 Pescane uno a caso dal database totale!"):
        all_dinos = sorted(df['name'].dropna().unique())
        random_dino = random.choice(all_dinos)
        st.info(f"Abbiamo estratto: **{random_dino}**! (Imposta i filtri geografici su 'Tutte/i' per cercarlo nel menu)")
                
