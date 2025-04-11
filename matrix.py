import streamlit as st
import pandas as pd

# Ustawienia strony
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

# Domyślna lista zagrożeń
default_risks = [
    {"Zagrożenie": "Awaria serwera", "Prawdopodobieństwo": 4, "Wpływ": 5},
    {"Zagrożenie": "Atak DDoS", "Prawdopodobieństwo": 3, "Wpływ": 4},
    {"Zagrożenie": "Błąd ludzki", "Prawdopodobieństwo": 5, "Wpływ": 3},
    {"Zagrożenie": "Utrata zasilania", "Prawdopodobieństwo": 2, "Wpływ": 2}
]

# Wczytanie danych do sesji
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(default_risks)

# Dodawanie zagrożeń sieciowych
st.subheader("🔗 Analiza ryzyka systemów sieciowych")
with st.form("add_network_security_risk"):
    name = st.text_input("Opis zagrożenia sieciowego")
    prob = st.slider("Prawdopodobieństwo (1-5)", 1, 5, 3)
    impact = st.slider("Wpływ (1-5)", 1, 5, 3)
    submitted = st.form_submit_button("Dodaj zagrożenie sieciowe")

if submitted and name.strip() != "":
    new_row = {"Zagrożenie": name, "Prawdopodobieństwo": prob, "Wpływ": impact}
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
    st.success("Zagrożenie sieciowe dodane.")

# Wyświetlanie listy dodanych zagrożeń sieciowych
st.subheader("📊 Dodane zagrożenia sieciowe")
st.dataframe(st.session_state.df)

# Obliczanie poziomu ryzyka i klasyfikacji
st.session_state.df["Poziom ryzyka"] = st.session_state.df["Prawdopodobieństwo"] * st.session_state.df["Wpływ"]
st.session_state.df["Klasyfikacja"] = st.session_state.df["Poziom ryzyka"].apply(klasyfikuj_ryzyko)

# Filtrowanie
st.subheader("📋 Filtruj według poziomu ryzyka")
filt = st.radio("Pokaż:", ["Wszystkie", "Niskie", "Średnie", "Wysokie"], horizontal=True)

if filt != "Wszystkie":
    df_filtered = st.session_state.df[st.session_state.df["Klasyfikacja"] == filt]
else:
    df_filtered = st.session_state.df

# Kolorowanie
def koloruj(val):
    if val == "Niskie":
        return "background-color: #d4edda"
    elif val == "Średnie":
        return "background-color: #fff3cd"
    elif val == "Wysokie":
        return "background-color: #f8d7da"
    return ""

# Wyświetlenie macierzy ryzyka
st.subheader("📊 Macierz ryzyka")
st.dataframe(
    df_filtered.style.applymap(koloruj, subset=["Klasyfikacja"]),
    use_container_width=True
)

# Dodatkowe informacje o zabezpieczeniach sieciowych
st.subheader("💼 Zalecenia dotyczące zabezpieczeń sieciowych")
st.write("""
- **Zapory ogniowe (firewall)**: Użyj zapory, aby monitorować i kontrolować ruch wchodzący i wychodzący.
- **Autoryzacja i uwierzytelnianie**: Stosuj autoryzację dwuskładnikową dla kont administratorów i innych krytycznych zasobów.
- **Szyfrowanie**: Zastosuj szyfrowanie danych przesyłanych przez sieć oraz przechowywanych danych.
- **Edukacja użytkowników**: Przeprowadzaj regularne szkolenia z zakresu cyberbezpieczeństwa dla pracowników.
- **Regularne aktualizacje**: Utrzymuj aktualność systemów operacyjnych i oprogramowania zabezpieczającego.
""")
