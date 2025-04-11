import streamlit as st
import pandas as pd
import openpyxl
from io import BytesIO

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

# ➕ Dodawanie nowego ryzyka
st.subheader("➕ Dodaj nowe zagrożenie")
with st.form("add_risk_form"):
    name = st.text_input("Opis zagrożenia")
    prob = st.slider("Prawdopodobieństwo (1-5)", 1, 5, 3)
    impact = st.slider("Wpływ (1-5)", 1, 5, 3)
    submitted = st.form_submit_button("Dodaj")

    if submitted and name.strip() != "":
        new_row = {"Zagrożenie": name, "Prawdopodobieństwo": prob, "Wpływ": impact}
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
edited_df["Poziom ryzyka"] = edited_df["Prawdopodobieństwo"] * edited_df["Wpływ"]
edited_df["Klasyfikacja"] = edited_df["Poziom ryzyka"].apply(klasyfikuj_ryzyko)

# 📋 Filtrowanie
st.subheader("📋 Filtruj według poziomu ryzyka")
filt = st.radio("Pokaż:", ["Wszystkie", "Niskie", "Średnie", "Wysokie"], horizontal=True)

if filt != "Wszystkie":
    df_filtered = edited_df[edited_df["Klasyfikacja"] == filt]
else:
    df_filtered = edited_df

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
styled_df = df_filtered.style.applymap(koloruj, subset=["Klasyfikacja"])
st.dataframe(
    styled_df,
    use_container_width=True
)

# Export do Excela
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, sheet_name='Macierz Ryzyka', index=False)
    writer.close()
    processed_data = output.getvalue()
    return processed_data

excel_file = to_excel(df_filtered)

st.download_button(
    label="💾 Pobierz macierz ryzyka jako XLSX",
    data=excel_file,
    file_name="macierz_ryzyka.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
