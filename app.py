import os
import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# Ustawienia bazy danych
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Model danych dla zagrożeń
class Risk(Base):
    __tablename__ = 'risks'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    probability = Column(Integer)
    impact = Column(Integer)

# Utwórz tabelę, jeśli nie istnieje
Base.metadata.create_all(engine)

st.set_page_config(page_title="Analiza ryzyka", layout="wide")
st.title("🔐 Analiza ryzyka systemów teleinformatycznych")

# Funkcja klasyfikująca poziom ryzyka
def klasyfikuj_ryzyko(poziom):
    if poziom <= 6:
        return "Niskie"
    elif poziom <= 14:
        return "Średnie"
    else:
        return "Wysokie"

# Wyciągnięcie danych z bazy
def fetch_risks():
    return pd.read_sql(session.query(Risk).statement, session.bind)

# Zapis danych do bazy
def save_risk(description, probability, impact):
    new_risk = Risk(description=description, probability=probability, impact=impact)
    session.add(new_risk)
    session.commit()

# Domyślna lista zagrożeń
if "df" not in st.session_state:
    st.session_state.df = fetch_risks()

# ➕ Dodawanie nowego ryzyka
st.subheader("➕ Dodaj nowe zagrożenie")
with st.form("add_risk_form"):
    name = st.text_input("Opis zagrożenia")
    prob = st.slider("Prawdopodobieństwo (1-5)", 1, 5, 3)
    impact = st.slider("Wpływ (1-5)", 1, 5, 3)
    submitted = st.form_submit_button("Dodaj")

    if submitted and name.strip() != "":
        save_risk(name, prob, impact)
        st.session_state.df = fetch_risks()
        st.success("Zagrożenie dodane.")

# ✏️ Edytuj ryzyka w interaktywnej tabeli
st.subheader("✏️ Edytuj macierz ryzyka")
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    key="risk_editor"
)

st.session_state.df = edited_df.copy()

# Oblicz poziom ryzyka i klasyfikację
st.session_state.df["Poziom ryzyka"] = st.session_state.df["Prawdopodobieństwo"] * st.session_state.df["Wpływ"]
st.session_state.df["Klasyfikacja"] = st.session_state.df["Poziom ryzyka"].apply(klasyfikuj_ryzyko)

# 📋 Filtrowanie
st.subheader("📋 Filtruj według poziomu ryzyka")
filt = st.radio("Pokaż:", ["Wszystkie", "Niskie", "Średnie", "Wysokie"], horizontal=True)

if filt != "Wszystkie":
    df_filtered = st.session_state.df[st.session_state.df["Klasyfikacja"] == filt]
else:
    df_filtered = st.session_state.df

# 🎨 Kolorowanie
def koloruj(val):
    if val == "Niskie":
        return "background-color: #d4edda"
    elif val == "Średnie":
        return "background-color: #fff3cd"
    elif val == "Wysokie":
        return "background-color: #f8d7da"
    return ""

# 📊 Wyświetlenie
st.subheader("📊 Macierz ryzyka")
st.dataframe(
    df_filtered.style.applymap(koloruj, subset=["Klasyfikacja"]),
    use_container_width=True
)

# 📥 Eksport do CSV
st.subheader("📥 Eksportuj dane")
if st.button("Eksportuj do CSV"):
    df_export = st.session_state.df.copy()
    csv = df_export.to_csv(index=False, encoding='utf-8', sep=';')
    st.download_button(
        label="Pobierz plik CSV",
        data=csv,
        file_name='zagrozenia.csv',
        mime='text/csv',
    )