import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

st.set_page_config(page_title="Top Talent Analysis", layout="wide")
st.title("Top Talent Analysis")
st.markdown('Аналіз впливу команди( акторів та режисера) на успішність фільму.')

# --- Завантаження даних ---
@st.cache_data
def load_data():
    return pd.read_csv("movie_metadata.csv")

df = load_data()

with st.expander("Фільтри:"):
    min_year = int(df['title_year'].min())
    max_year = int(df['title_year'].max())
    selected_year_range = st.slider(
        "Вибери проміжок років",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )
    # 🔘 Чекбокс для запуску обробки
    run_analysis = st.checkbox("✅ Запустити аналіз")

if run_analysis:
    filtered_df = df[
        df['title_year'].between(selected_year_range[0], selected_year_range[1])
    ]

    # --- Прогресбар ---
    progress_container = st.container()
    with progress_container:
        st.write('Spúšťam výpočty…')
        progress_text = st.empty()
        progress_bar = st.progress(0)

    for i in range(3):
        time.sleep(0.5)
        with progress_container:
            progress_text.write(f'Крок {i+1}/3 завершено')
            progress_bar.progress((i+1) / 3)

    # --- Показ результатів після чекбоксу ---
    st.subheader("Загальна інформація про датасет")
    col1, col2 = st.columns(2)
    col1.metric("Середній IMDb", f"{df['imdb_score'].mean():.2f}")
    col2.metric("Кількість фільмів", f"{df.shape[0]}")


        

    # --- Очищення ---
    df = df.dropna(subset=['actor_1_name', 'director_name', 'imdb_score'])

    # --- Створюємо subplot ---
    actor_counts = pd.concat([
        df['actor_1_name'], df['actor_2_name'], df['actor_3_name']
    ]).value_counts().head(10)

    director_rating = df.groupby('director_name')['imdb_score'].agg(['mean', 'count'])
    top_directors = director_rating[director_rating['count'] >= 3].sort_values(by='mean', ascending=False).head(10)


    st.subheader("Найпопулярніші актори та найрейтинговіші режисери")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))


    sns.barplot(x=actor_counts.values, y=actor_counts.index, palette="Set2", ax=ax1)
    ax1.set_title("Топ-10 акторів за кількістю фільмів")
    ax1.set_xlabel("Кількість фільмів")
    ax1.set_ylabel("")


    sns.barplot(x=top_directors['mean'], y=top_directors.index, palette="muted", ax=ax2)
    ax2.set_title("Топ-10 режисерів за IMDb рейтингом")
    ax2.set_xlabel("Середній рейтинг")
    ax2.set_ylabel("")

    st.pyplot(fig)


    st.subheader("Зв’язок між актором і рейтингами його фільмів на IMDb")

    # Збираємо акторів у один список + IMDb + color
    actors_combined = pd.concat([
        df[['actor_1_name', 'imdb_score', 'color']].rename(columns={'actor_1_name': 'actor'}),
        df[['actor_2_name', 'imdb_score', 'color']].rename(columns={'actor_2_name': 'actor'}),
        df[['actor_3_name', 'imdb_score', 'color']].rename(columns={'actor_3_name': 'actor'}),
    ])

    # Топ-10 за кількістю появ
    top_actors = (
        actors_combined['actor']
        .value_counts()
        .head(10)
        .index
    )

    custom_palette = ["#808080","#db7093"]
    # Фільтруємо лише топ-10 акторів
    filtered_actors = actors_combined[actors_combined['actor'].isin(top_actors)].dropna()

    # Ensure 'color' column is a proper categorical
    filtered_actors["color"] = filtered_actors["color"].astype("category")

    # Create FacetGrid with hue defined at the grid level
    g = sns.FacetGrid(
        filtered_actors,
        col="actor",
        col_wrap=5,
        height=3.5,
        sharex=True            
        
    )

    # Now plot the histogram
    g.map_dataframe(
        sns.histplot,
        x="imdb_score",
        multiple="dodge",  
        bins=8, 
        hue="color",
        palette=custom_palette,
        edgecolor="black"
    )
    g.set_titles("{col_name}")
    g.set_axis_labels("IMDb", "Кількість")
    g.add_legend()
    st.pyplot(g.figure)


    # Фільтруємо, щоб не було пропущених
    df_clean = df.dropna(subset=['director_name', 'imdb_score'])

    # Додаємо колонку: фільм успішний чи ні
    df_clean['successful'] = df_clean['imdb_score'] > 7.0

    # Групуємо по режисерах
    director_stats = df_clean.groupby('director_name')['successful'].agg(['sum', 'count'])
    director_stats['success_rate'] = director_stats['sum'] / director_stats['count']

    # Фільтруємо: тільки ті, хто зняв мінімум 3 фільми
    filtered_directors = director_stats[director_stats['count'] >= 3]

    # Топ-10 за відсотком успішних
    top_success = filtered_directors.sort_values(by='success_rate', ascending=False).head(10)

    st.subheader("Режисери з найвищим відсотком успішних фільмів")
    fig, ax = plt.subplots()
    sns.barplot(x=top_success['success_rate'], y=top_success.index, palette="Greens_r", ax=ax)
    ax.set_xlabel("Частка успішних фільмів (> 7 IMDb)")
    st.pyplot(fig)

