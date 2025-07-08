import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time


st.set_page_config(page_title="Exploratory Analysis", layout="wide")

st.title("Dynamic Analysis")
st.markdown('Аналіз динаміки кіновиробництва та визначення, які країни та жанри переважали у різні періоди часу')

# --- Завантаження даних ---
@st.cache_data
def load_data():
    return pd.read_csv("movie_metadata.csv")

df = load_data()
with st.expander("Фільтри:"):
    # Проміжок років
    min_year = int(df['title_year'].min())
    max_year = int(df['title_year'].max())
    selected_year_range = st.slider(
        "Вибери проміжок років",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )

    country_options = ["All"] + sorted(df['country'].dropna().unique().tolist())
    selected_countries = st.multiselect(
        "Вибери країни",
        options=country_options,
        default=["All"]
    )

    # Якщо вибрано "Усі", підставляємо всі країни автоматично
    if "All" in selected_countries:
        selected_countries = df['country'].dropna().unique().tolist()

    # 🔘 Чекбокс для запуску обробки
    run_analysis = st.checkbox("✅ Запустити аналіз")

# --- Обробка починається тільки якщо чекбокс активний ---
if run_analysis:
    filtered_df = df[
        df['title_year'].between(selected_year_range[0], selected_year_range[1]) &
        df['country'].isin(selected_countries)
    ]

    # --- Прогресбар ---
    progress_container = st.container()
    with progress_container:
        st.write('Фільтрація')
        progress_text = st.empty()
        progress_bar = st.progress(0)

    for i in range(3):
        time.sleep(0.05)
        with progress_container:
            progress_text.write(f'Крок {i+1}/3 завершено')
            progress_bar.progress((i+1) / 3)

    # --- Показ результатів після чекбоксу ---
    st.subheader("Загальна інформація про датасет")

    col1, col2, col3 = st.columns(3)
    col1.metric("Кількість фільмів", filtered_df.shape[0])
    col2.metric("Кількість колонок", filtered_df.shape[1])
    col3.metric("Унікальних жанрів", filtered_df['genres'].nunique())

    with st.expander("Перші 5 рядків датасету"):
        st.dataframe(filtered_df.head(5))

        # --- Дані ---
    top_countries = filtered_df['country'].value_counts().nlargest(10)

    genre_series = filtered_df['genres'].dropna().str.split('|').explode()
    top_genres = genre_series.value_counts().nlargest(10)

    yearly_counts = filtered_df['title_year'].value_counts().sort_index()

    genre_ratings = (
        filtered_df.dropna(subset=['genres', 'imdb_score'])
        .assign(genres=filtered_df['genres'].str.split('|'))
        .explode('genres')
        .groupby('genres')['imdb_score'].mean()
        .sort_values(ascending=False)
        .head(10)
    )

    # --- Subplot 1: 📅 Роки + 🏳️ Країни ---
    st.subheader("Динаміка випуску фільмів і країни-лідери")

    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Графік 1 — 📅 Роки
    sns.lineplot(x=yearly_counts.index, y=yearly_counts.values, marker='o', ax=ax2)
    ax2.set_title("Кількість фільмів за роками")
    ax2.set_xlabel("Рік")
    ax2.set_ylabel("Кількість фільмів")

    # Графік 2 — 🏳️ Країни
    sns.barplot(x=top_countries.values, y=top_countries.index, ax=ax1, palette="Set2")
    ax1.set_title(" Топ-10 країн за кількістю фільмів")
    ax1.set_xlabel("Кількість фільмів")
    ax1.set_ylabel("")

    st.pyplot(fig1)

    # --- Subplot 2: ⭐ Рейтинг + 🎬 Жанри ---
    st.subheader("Жанровий аналіз: популярність і оцінки")

    fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))

    # Графік 3 — ⭐ IMDb рейтинг
    sns.barplot(x=genre_ratings.values, y=genre_ratings.index, ax=ax3, palette="coolwarm")
    ax3.set_title("Середній IMDb рейтинг (Топ-10 жанрів)")
    ax3.set_xlabel("Середній рейтинг")
    ax3.set_ylabel("")

    # Графік 4 — 🎬 Жанри
    sns.barplot(x=top_genres.values, y=top_genres.index, ax=ax4, palette="muted")
    ax4.set_title("Топ-10 жанрів за кількістю фільмів")
    ax4.set_xlabel("Кількість фільмів")
    ax4.set_ylabel("")

    st.pyplot(fig2)

    
