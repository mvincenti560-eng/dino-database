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
    
    # Selezione pulita del dinosauro senza filtri geografici ingannevoli
    dino_list = sorted(df['name'].dropna().unique())
    selected_dino = st.selectbox("Cerca o seleziona un dinosauro:", dino_list)
    
    if selected_dino:
        dino_data = df[df['name'] == selected_dino].iloc[0]
        
        st.subheader(f"Scheda Informativa: {selected_dino}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Gruppo:** {dino_data.get('early_interval', 'Non specificato')}")
            country = dino_data.get('country', 'N/D')
            if pd.isna(country) or country == '':
                country = "Non registrato nel database"
            st.write(f"🌍 **Nazione del ritrovamento:** {country}")
            st.write(f"📍 **Località:** {dino_data.get('locality', 'N/D')}")
            
        with col2:
            st.write(f"⏳ **Intervallo temporale:** {dino_data.get('interval', 'N/D')}")
            lat = dino_data.get('lat', 'N/D')
            lng = dino_data.get('lng', 'N/D')
            st.write(f"🧭 **Coordinate:** Lat: {lat}, Lng: {lng}")

        # Link diretto a The Dinosaur Database
        query_encoded = urllib.parse.quote(selected_dino)
        dino_db_url = f"https://dinosaurpictures.org/{query_encoded}"
        
        st.markdown("---")
        st.markdown(f"👉 [Cerca **{selected_dino}** su The Dinosaur Database]({dino_db_url})", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🎲 Pescane uno a caso!"):
        random_dino = random.choice(dino_list)
        st.info(f"Abbiamo estratto: **{random_dino}**! Cercalo nel menu a tendina sopra.")
    
