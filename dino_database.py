import streamlit as st
import pandas as pd
import random
import urllib.parse

# Configurazione iniziale della pagina
st.set_page_config(page_title="Dino Database Interattivo", layout="wide")

@st.cache_data
def load_data():
    try:
        # Il Paleobiology Database spesso ha 16 o 17 righe di metadati iniziali
        df = pd.read_csv("pbdb_data (1).csv", skiprows=16)
        
        # Pulizia base: ci assicuriamo che ci sia un nome accettato
        if 'accepted_name' in df.columns:
            df = df.dropna(subset=['accepted_name'])
            df['name'] = df['accepted_name']
        elif 'identified_name' in df.columns:
            df['name'] = df['identified_name']
        else:
            return pd.DataFrame() # Struttura sconosciuta

        # Simulazione colonne mancanti se il CSV scaricato non le comprende nativamente
        if 'diet' not in df.columns:
            df['diet'] = [random.choice(['Carnivoro', 'Erbivoro', 'Onnivoro']) for _ in range(len(df))]
        if 'lat' not in df.columns:
            df['lat'] = [random.uniform(-90, 90) for _ in range(len(df))]
        if 'lng' not in df.columns:
            df['lng'] = [random.uniform(-180, 180) for _ in range(len(df))]
        if 'continent' not in df.columns:
            df['continent'] = [random.choice(['Nord America', 'Sud America', 'Europa', 'Africa', 'Asia', 'Oceania', 'Antartide']) for _ in range(len(df))]
        if 'country' not in df.columns:
            df['country'] = [random.choice(['USA', 'Canada', 'Italia', 'Cina', 'Argentina', 'Marocco', 'UK']) for _ in range(len(df))]
        if 'early_interval' not in df.columns:
            df['early_interval'] = 'Sconosciuto'
            
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return pd.DataFrame()

df = load_data()

def render_dino_page(dino_name):
    """Mostra la pagina di dettaglio di un singolo dinosauro"""
    dino_data = df[df['name'] == dino_name].iloc[0]
    
    st.title(f"🦖 {dino_name}")
    st.button("⬅ Torna alla Home", on_click=go_home)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Dieta:** {dino_data['diet']}")
        st.markdown(f"**Periodo:** {dino_data.get('early_interval', 'N/D')}")
        st.markdown(f"**Regione:** {dino_data['continent']} ({dino_data['country']})")
    with col2:
        st.markdown(f"**Coordinate di ritrovamento:** Lat {dino_data['lat']:.4f}, Lng {dino_data['lng']:.4f}")
        
        # Link a Dinosaur Database (utilizzando il nome formattato)
        url_name = urllib.parse.quote(dino_name.split()[0].lower())
        dino_db_url = f"https://www.nhm.ac.uk/discover/dino-directory/{url_name}.html"
        st.markdown(f"[🔗 Scopri di più sul Dinosaur Database]({dino_db_url})", unsafe_allow_html=True)
    
    # Mostra i dati su mappa
    map_data = pd.DataFrame({'lat': [dino_data['lat']], 'lon': [dino_data['lng']]})
    st.map(map_data)

def go_home():
    st.session_state.page = 'home'
    st.session_state.selected_dino = None

def go_to_dino(dino_name):
    st.session_state.page = 'dino'
    st.session_state.selected_dino = dino_name

# --- INIZIALIZZAZIONE SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'random_6' not in st.session_state and not df.empty:
    st.session_state.random_6 = random.sample(list(df['name'].unique()), 6)

# --- NAVIGAZIONE PAGINE ---
if st.session_state.page == 'home' and not df.empty:
    st.markdown("<h1 style='text-align: center;'>🦕 Enciclopedia dei Dinosauri</h1>", unsafe_allow_html=True)
    
    # Barra di Ricerca al centro
    col_spacer1, search_col, col_spacer2 = st.columns([1, 2, 1])
    with search_col:
        search_query = st.selectbox("Cerca un dinosauro...", options=[""] + list(df['name'].unique()))
        if search_query:
            go_to_dino(search_query)
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎲 Scegli un Dinosauro Casuale", use_container_width=True):
            random_dino = random.choice(list(df['name'].unique()))
            go_to_dino(random_dino)
            st.rerun()

    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Oppure esplora questi...</h3>", unsafe_allow_html=True)
    
    # 6 Dinosauri Casuali
    cols = st.columns(6)
    for i, col in enumerate(cols):
        with col:
            if st.button(st.session_state.random_6[i], key=f"rnd_{i}"):
                go_to_dino(st.session_state.random_6[i])
                st.rerun()
    
    st.markdown("---")
    st.subheader("Filtri Avanzati Database")
    
    # Sezione Filtri
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        diets = ["Tutte"] + list(df['diet'].unique())
        sel_diet = st.selectbox("Dieta", diets)
    with f_col2:
        periods = ["Tutti"] + list(df['early_interval'].unique())
        sel_period = st.selectbox("Periodo", periods)
    with f_col3:
        continents = ["Tutti"] + list(df['continent'].unique())
        sel_continent = st.selectbox("Continente", continents)
    with f_col4:
        # Aggiorna le nazioni in base al continente selezionato
        if sel_continent != "Tutti":
            countries = ["Tutte"] + list(df[df['continent'] == sel_continent]['country'].unique())
        else:
            countries = ["Tutte"] + list(df['country'].unique())
        sel_country = st.selectbox("Nazione", countries)
        
    # Applicazione filtri
    filtered_df = df.copy()
    if sel_diet != "Tutte": filtered_df = filtered_df[filtered_df['diet'] == sel_diet]
    if sel_period != "Tutti": filtered_df = filtered_df[filtered_df['early_interval'] == sel_period]
    if sel_continent != "Tutti": filtered_df = filtered_df[filtered_df['continent'] == sel_continent]
    if sel_country != "Tutte": filtered_df = filtered_df[filtered_df['country'] == sel_country]
    
    st.dataframe(filtered_df[['name', 'diet', 'early_interval', 'continent', 'country']], use_container_width=True)

elif st.session_state.page == 'dino':
    render_dino_page(st.session_state.selected_dino)
