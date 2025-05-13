import streamlit as st
import pandas as pd

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
    
    csv = df_export.to_csv(index=False, encoding='utf-8', sep=';')  # Użyj `;` jako separatora
    st.download_button(
        label="Pobierz plik CSV",
        data=csv,
        file_name='zagrozenia.csv',  # Nazwa pliku
        mime='text/csv',
    )
    
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
    st.session_state.oceny = {cecha: 3 for cecha in cechy_jakosci}  # Domyślne wartości

st.subheader("Oceń system (1-5) dla każdej cechy:")
for cecha, opis in cechy_jakosci.items():
    st.write(f"**{cecha}**: {opis}")
    st.session_state.oceny[cecha] = st.slider(f"Ocena {cecha} (1-5)", 1, 5, st.session_state.oceny[cecha])

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

# ---------------------------------------------------------------------
# Moduł ISO/IEC 27001 - Ocena Zgodności
# ---------------------------------------------------------------------
st.header("🛡️ Moduł ISO/IEC 27001 - Ocena Zgodności")

# Kontrole bezpieczeństwa pogrupowane w obszary
kontrole_bezpieczenstwa = {
    "Organizacyjne (A.5)": [
        "Polityka bezpieczeństwa informacji",
        "Organizacja bezpieczeństwa informacji",
        "Zarządzanie zasobami",
        "Bezpieczeństwo zasobów ludzkich"
    ],
    "Ludzkie (A.6)": [
        "Zasady zatrudniania",
        "Szkolenia z zakresu bezpieczeństwa",
        "Zarządzanie dostępem użytkowników",
        "Reagowanie na incydenty bezpieczeństwa"
    ],
    "Fizyczne (A.7)": [
        "Bezpieczeństwo fizyczne obwodów bezpieczeństwa",
        "Kontrola dostępu fizycznego",
        "Ochrona przed zagrożeniami środowiskowymi",
        "Bezpieczeństwo sprzętu"
    ],
    "Techniczne (A.8)": [
        "Zarządzanie tożsamością i dostępem",
        "Szyfrowanie danych",
        "Monitoring i logowanie",
        "Ochrona przed złośliwym oprogramowaniem"
    ]
}

# Inicjalizacja stanu sesji dla ocen zgodności
if "oceny_zgodnosci" not in st.session_state:
    st.session_state.oceny_zgodnosci = {
        obszar: {kontrola: 3 for kontrola in kontrole_bezpieczenstwa[obszar]}
        for obszar in kontrole_bezpieczenstwa
    }

# Wybór obszaru
obszar = st.selectbox("Wybierz obszar zgodności z ISO/IEC 27001:", list(kontrole_bezpieczenstwa.keys()))

st.subheader(f"Oceń poziom wdrożenia kontroli w obszarze: {obszar}")

# Prezentacja i ocena kontroli
for kontrola in kontrole_bezpieczenstwa[obszar]:
    st.write(f"**Kontrola**: {kontrola}")
    st.session_state.oceny_zgodnosci[obszar][kontrola] = st.slider(
        f"Poziom wdrożenia (1-5) dla '{kontrola}'", 1, 5,
        st.session_state.oceny_zgodnosci[obszar][kontrola]
    )

# Obliczenie średniego poziomu dojrzałości
oceny_obszaru = list(st.session_state.oceny_zgodnosci[obszar].values())
sredni_poziom = np.mean(oceny_obszaru)

st.subheader("Podsumowanie:")
st.metric(label=f"Średni poziom dojrzałości w obszarze '{obszar}'", value=f"{sredni_poziom:.2f}")

# Interpretacja wyniku
st.subheader("Interpretacja:")
if sredni_poziom <= 2:
    st.error(f"Średni poziom dojrzałości w obszarze '{obszar}' jest niski. Wymagane są natychmiastowe działania naprawcze.")
elif sredni_poziom <= 4:
    st.warning(f"Średni poziom dojrzałości w obszarze '{obszar}' jest średni. Rozważ wdrożenie dodatkowych kontroli.")
else:
    st.success(f"Średni poziom dojrzałości w obszarze '{obszar}' jest wysoki. Dobra robota!")
