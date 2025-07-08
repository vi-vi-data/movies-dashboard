import streamlit as st
import pandas as pd

st.set_page_config(page_title="Movies Dashboard", layout="wide")
@st.cache_data
def load_data():
    return pd.read_csv("movie_metadata.csv")

df = load_data()

# --- Заголовок ---
st.title("Аналіз фільмів IMDb")
st.markdown("""
Цей дашборд досліджує динаміку виробництва та вплив команди на успішність
""")

# --- Основна інформація ---
st.header("Навігація по сторінках")
st.markdown("""
- **Dynamic Analysis** — загальні тренди: країни, жанри, динаміка за роками.
- **Top Talent Analysis** — аналіз акторів і режисерів та їхнього впливу на IMDb-рейтинг.
""")

st.header("Мета проєкту")
st.markdown("""
Проаналізувати дані про фільми IMDb, щоб:
- Визначити найпопулярніші фільми та жанри за певний період
- Визначити як змінювалась кількість фільмів 
- Визначити різницю між IMDb-рейтинг та рейтингом поулярності жанрів
- Визначити режисерів, які мають найвищий середній IMDb-рейтинг (за умови ≥3 фільмів)
- Визначити чи впливає команда на успішність фільму
""")

st.header(" Джерело даних")
st.markdown("Використано датасет [IMDb Movie Metadata](https://www.kaggle.com/datasets/carolzhangdc/imdb-5000-movie-dataset) з Kaggle.")


with st.expander("🔍 Продивитись датасет"):
    st.dataframe(df.head())
