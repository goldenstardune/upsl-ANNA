import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Float

# Konfiguracja połączenia z bazą danych
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://user:password@host:port/database"  # Zastąp danymi lokalnymi

engine = create_engine(DATABASE_URL, pool_pre_ping=True) # Dodano pool_pre_ping
Base = declarative_base()

# Definicja modelu danych dla zagrożeń
class Zagrozenie(Base):
    __tablename__ = "zagrozenia"

    id = Column(Integer, primary_key=True)
    zagrozenie = Column(String)
    prawdopodobienstwo = Column(Integer)
    wplyw = Column(Integer)
    poziom_ryzyka = Column(Integer)
    klasyfikacja = Column(String)

# Definicja modelu danych dla ISO 9126
class ISO9126Ocena(Base):
    __tablename__ = "iso9126_oceny"

    id = Column(Integer, primary_key=True)
    funkcjonalnosc = Column(Integer)
    niezawodnosc = Column(Integer)
    uzytecznosc = Column(Integer)
    efektywnosc = Column(Integer)
    utrzymywalnosc = Column(Integer)
    przenosnosc = Column(Integer)

# Definicja modelu danych dla ISO 27001
class ISO27001Ocena(Base):
    __tablename__ = "iso27001_oceny"

    id = Column(Integer, primary_key=True)
    obszar = Column(String)
    polityka_bezpieczenstwa_informacji = Column(Integer)
    organizacja_bezpieczenstwa_informacji = Column(Integer)
    zarzadzanie_zasobami = Column(Integer)
    bezpieczenstwo_zasobow_ludzkich = Column(Integer)

# Utworzenie tabel w bazie danych
Base.metadata.create_all(engine)

# Inicjalizacja sesji
Session = sessionmaker(bind=engine)
session = Session()

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

# Pobranie danych z bazy danych lub domyślne
def get_zagrozenia_from_db():
    try:
        zagrozenia = session.query(Zagrozenie).all()
        if zagrozenia:
            return pd.DataFrame([{
                'Zagrożenie': z.zagrozenie,
                'Prawdopodobieństwo': z.prawdopodobienstwo,
                'Wpływ': z.wplyw,
                'Poziom ryzyka': z.poziom_ryzyka,
                'Klasyfikacja': z.klasyfikacja
            } for z in zagrozenia])
        else:
            return pd.DataFrame(default_risks)
    except Exception as e:
        st.error(f"Błąd połączenia z bazą danych: {e}")
        return pd.DataFrame(default_risks)

# Domyślna lista zagrożeń
default_risks = [
    {"Zagrożenie": "Awaria serwera", "Prawdopodobieństwo": 4, "Wpływ": 5, "Poziom ryzyka": 20, "Klasyfikacja": "Wysokie"},
    {"Zagrożenie": "Atak DDoS", "Prawdopodobieństwo": 3, "Wpływ": 4, "Poziom ryzyka": 12, "Klasyfikacja": "Średnie"},
    {"Zagrożenie": "Błąd ludzki", "Prawdopodobieństwo": 5, "Wpływ": 3, "Poziom ryzyka": 15, "Klasyfikacja": "Wysokie"},
    {"Zagrożenie": "Utrata zasilania", "Prawdopodobieństwo": 2, "Wpływ": 2, "Poziom ryzyka": 4, "Klasyfikacja": "Niskie"}
]

# Wczytanie danych do sesji
if "df" not in st.session_state:
    st.session_state.df = get_zagrozenia_from_db()

# Zapisywanie danych do bazy danych
def save_zagrozenia_to_db(df):
    try:
        session.query(Zagrozenie).delete()  # Usuń istniejące dane
        for index, row in df.iterrows():
            zagrozenie = Zagrozenie(
                zagrozenie=row['Zagrożenie'],
                prawdopodobienstwo=row['Prawdopodobieństwo'],
                wplyw=row['Wpływ'],
                poziom_ryzyka=row['Poziom ryzyka'],
                klasyfikacja=row['Klasyfikacja']
            )
            session.add(zagrozenie)
        session.commit()
        st.success("Dane zagrożeń zapisane do bazy danych.")
    except Exception as e:
        session.rollback()
        st.error(f"Błąd zapisu do bazy danych: {e}")

# ➕ Dodawanie nowego ryzyka
st.subheader("➕ Dodaj nowe zagrożenie")
with st.form("add_risk_form"):
    name = st.text_input("Opis zagrożenia")
    prob = st.slider("Prawdopodobieństwo (1-5)", 1, 5, 3)
    impact = st.slider("Wpływ (1-5)", 1, 5, 3)
    submitted = st.form_submit_button("Dodaj")

    if submitted and name.strip() != "":
        new_row = {"Zagrożenie": name, "Prawdopodobieństwo": prob, "Wpływ": impact}
        new_row["Poziom ryzyka"] = new_row["Prawdopodobieństwo"] * new_row["Wpływ"]
        new_row["Klasyfikacja"] = klasyfikuj_ryzyko(new_row["Poziom ryzyka"])
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Zagrożenie dodane.")

# ✏️ Edytuj ryzyka w interaktywnej tabeli
st.subheader("✏️ Edytuj macierz ryzyka")
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    key="risk_editor"
)

# Zapisz zmodyfikowaną tabelę do sesji
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
    # Przygotowanie DataFrame do eksportu
    df_export = st.session_state.df.copy()
    
    csv = df_export.to_csv(index=False, encoding='utf-8', sep=';')
    st.download_button(
        label="Pobierz plik CSV",
        data=csv,
        file_name='zagrozenia.csv',
        mime='text/csv',
    )

# Zapisz zmiany w bazie danych
if st.button("Zapisz zmiany w bazie danych"):
    save_zagrozenia_to_db(st.session_state.df)

# ---------------------------------------------------------------------
# Moduł ISO/IEC 9126 - Ankieta
# ---------------------------------------------------------------------
st.header("📊 Moduł ISO/IEC 9126 - Ocena Jakości Oprogramowania")

cechy_jakosci = {
    "Funkcjonalność": "Stopień, w jakim oprogramowanie spełnia określone potrzeby użytkownika.",
    "Niezawodność": "Zdolność oprogramowania do utrzymania określonego poziomu wydajności.",
    "Użyteczność": "Łatwość używania oprogramowania przez użytkowników.",
    "Efektywność": "Zasoby (czas, energia), jakie oprogramowanie zużywa podczas wykonywania zadań.",
    "Utrzymywalność": "Łatwość modyfikowania, naprawiania i ulepszania oprogramowania.",
    "Przenośność": "Zdolność oprogramowania do działania w różnych środowiskach."
}

# Inicjalizacja stanu sesji dla ocen
if "oceny" not in st.session_state:
    # Spróbuj pobrać z bazy danych, jeśli nie ma, ustaw domyślne
    try:
        ocena_z_bazy = session.query(ISO9126Ocena).first()
        if ocena_z_bazy:
                st.session_state.oceny = {
                "Funkcjonalność": ocena_z_bazy.funkcjonalnosc,
                "Niezawodność": ocena_z_bazy.niezawodnosc,
                "Użyteczność": ocena_z_bazy.uzytecznosc,
                "Efektywność": ocena_z_bazy.efektywnosc,
                "Utrzymywalność": ocena_z_bazy.utrzymywalnosc,
                "Przenośność": ocena_z_bazy.przenosnosc,
            }
        else:
            st.session_state.oceny = {cecha: 3 for cecha in cechy_jakosci}
    except:
        st.session_state.oceny = {cecha: 3 for cecha in cechy_jakosci}

st.subheader("Oceń system (1-5) dla każdej cechy:")
for cecha, opis in cechy_jakosci.items():
    st.write(f"**{cecha}**: {opis}")
    st.session_state.oceny[cecha] = st.slider(f"Ocena {cecha} (1-5)", 1, 5, st.session_state.oceny[cecha])

# Obliczenie średnich
srednie_oceny = {cecha: st.session_state.oceny[cecha] for cecha in cechy_jakosci}
df_oceny = pd.DataFrame([srednie_oceny])

st.subheader("Wyniki oceny:")
st.dataframe(df_oceny)
# ---------------------------------------------------------------------
# Moduł ISO/IEC 9126 - Ankieta
# ---------------------------------------------------------------------
st.header("📊 Moduł ISO/IEC 9126 - Ocena Jakości Oprogramowania")

cechy_jakosci = {
    "Funkcjonalność": "Stopień, w jakim oprogramowanie spełnia określone potrzeby użytkownika.",
    "Niezawodność": "Zdolność oprogramowania do utrzymania określonego poziomu wydajności.",
    "Użyteczność": "Łatwość używania oprogramowania przez użytkowników.",
    "Efektywność": "Zasoby (czas, energia), jakie oprogramowanie zużywa podczas wykonywania zadań.",
    "Utrzymywalność": "Łatwość modyfikowania, naprawiania i ulepszania oprogramowania.",
    "Przenośność": "Zdolność oprogramowania do działania w różnych środowiskach."
}

# Inicjalizacja stanu sesji dla ocen
if "oceny" not in st.session_state:
    # Spróbuj pobrać z bazy danych, jeśli nie ma, ustaw domyślne
    try:
        ocena_z_bazy = session.query(ISO9126Ocena).first()
        if ocena_z_bazy:
            st.session_state.oceny = {
                "Funkcjonalność": ocena_z_bazy.funkcjonalnosc,
                "Niezawodność": ocena_z_bazy.niezawodnosc,
                "Użyteczność": ocena_z_bazy.uzytecznosc,
                "Efektywność": ocena_z_bazy.efektywnosc,
                "Utrzymywalność": ocena_z_bazy.utrzymywalnosc,
                "Przenośność": ocena_z_bazy.przenosnosc,
            }
        else:
            st.session_state.oceny = {cecha: 3 for cecha in cechy_jakosci}
    except Exception as e:
        st.error(
            f"Błąd pobierania ocen ISO9126 z bazy danych: {e}, ustawiam wartości domyślne.")  # Obsługa błędu
        st.session_state.oceny = {cecha: 3 for cecha in cechy_jakosci}

st.subheader("Oceń system (1-5) dla każdej cechy:")
for cecha, opis in cechy_jakosci.items():
    st.write(f"**{cecha}**: {opis}")
    st.session_state.oceny[cecha] = st.slider(f"Ocena {cecha} (1-5)", 1, 5,
                                                st.session_state.oceny[cecha])

# Obliczenie średnich
srednie_oceny = {cecha: st.session_state.oceny[cecha] for cecha in cechy_jakosci}
df_oceny = pd.DataFrame([srednie_oceny])

st.subheader("Wyniki oceny:")
st.dataframe(df_oceny)

# Interpretacja wyników
st.subheader("Interpretacja:")
interpretacje = {
    "Funkcjonalność": {
        1: "Funkcjonalność wymaga znacznych poprawek.",
        3: "Funkcjonalność jest zadowalająca, ale jest miejsce na ulepszenia.",
        5: "Funkcjonalność jest na bardzo wysokim poziomie."
    },
    "Niezawodność": {
        1: "Niezawodność jest bardzo niska.",
        3: "Niezawodność jest na średnim poziomie.",
        5: "Niezawodność jest bardzo wysoka."
    },
    "Użyteczność": {
        1: "Użyteczność wymaga znacznych poprawek.",
        3: "Użyteczność jest zadowalająca.",
        5: "Użyteczność jest bardzo wysoka."
    },
    "Efektywność": {
        1: "Efektywność jest bardzo niska.",
        3: "Efektywność jest na średnim poziomie.",
        5: "Efektywność jest bardzo wysoka."
    },
    "Utrzymywalność": {
        1: "Utrzymywalność jest bardzo niska.",
        3: "Utrzymywalność jest na średnim poziomie.",
        5: "Utrzymywalność jest bardzo wysoka."
    },
    "Przenośność": {
        1: "Przenośność jest bardzo niska.",
        3: "Przenośność jest na średnim poziomie.",
        5: "Przenośność jest bardzo wysoka."
    }
}

for cecha, ocena in st.session_state.oceny.items():
    if ocena <= 2:
        st.warning(f"{cecha}: {interpretacje[cecha][1]}")
    elif ocena <= 4:
        st.info(f"{cecha}: {interpretacje[cecha][3]}")
    else:
        st.success(f"{cecha}: {interpretacje[cecha][5]}")
