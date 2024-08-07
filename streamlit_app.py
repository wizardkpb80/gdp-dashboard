from pathlib import Path
import altair as alt
import pandas as pd
import streamlit as st
import ast
from datetime import datetime

st.set_page_config(page_title="Фильмы", page_icon="Ф")
# Оглавление
st.title("Фильмы")
# Описание
st.write(
    """
    Данные: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
    """
)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://img.freepik.com/free-photo/blue-wall-background_53876-88663.jpg?size=626&ext=jpg");
background-size: cover;
background-position: center center;
background-repeat: no-repeat;
background-attachment: local;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
</style>
"""

# Кнопка
if st.button('Оформление') is True:
       st.markdown(page_bg_img, unsafe_allow_html=True)

def load_movies():
    #df = pd.read_csv(Path(__file__).parent/"data/movies_genres_summary.csv")
    df = pd.read_csv(Path(__file__).parent / "data/tmdb_5000_movies.csv")
    return df

def load_credits():
    #df = pd.read_csv(Path(__file__).parent/"data/movies_genres_summary.csv")
    df = pd.read_csv(Path(__file__).parent / "data/tmdb_5000_credits.csv")
    return df

def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L

def strconvert(text):
    L = str()
    for i in ast.literal_eval(text):
        L = i['name']
        break
    return L

def collapse(L):
    L1 = []
    for i in L:
        L1.append(i.replace(" ",""))
    return L1

def fetch_director(text):
    L = []
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L

def is_year(release_date: str) -> str:
    return datetime.strptime(release_date, "%Y-%m-%d").date().year

movies = load_movies()
credits = load_credits()
movies = movies.merge(credits,on='title')
movies.dropna(inplace=True)
movies['Жанры'] = movies['genres'].apply(strconvert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert)
movies['cast'] = movies['cast'].apply(lambda x:x[0:3])
movies['crew'] = movies['crew'].apply(fetch_director)
movies['cast'] = movies['cast'].apply(collapse)
movies['crew'] = movies['crew'].apply(collapse)
#movies['genres'] = movies['genres'].apply(collapse)
movies['keywords'] = movies['keywords'].apply(collapse)
movies['year'] = movies['release_date'].apply(is_year)
# Таблица
st.write(movies)

# Жанр
genres = st.multiselect(
    "Жанр",
    movies.Жанры.unique(),
 #   ["Adventure", "Fantasy", "Action", "Crime"],
)
# Какие жанры выбраны
st.write("Выбраны:", genres)

# Фильтр
titles = st.multiselect(
    "Поиск по названию",
    movies.title.unique()
)

# Фильтр
years = st.slider("Года", 1980, 2009, (2010, 2024))

movies = movies[['Жанры','title','year','budget','keywords','cast','crew']]


# Реализация фильтров
df_filtered = movies[(movies["Жанры"].str.contains('|'.join(genres))) & (movies["year"].between(years[0], years[1]))]
df_filtered_by_name = movies[(movies["title"].isin(titles)) & (movies["year"].between(years[0], years[1]))]

# Отображение данных
st.write(df_filtered_by_name)
#df_filtered = movies[(movies["title"].isin(titles)) & (movies["genres"].str.contains('|'.join(genres))) & (movies["year"].between(years[0], years[1]))]
df_reshaped = df_filtered.pivot_table(
    index="year", columns="Жанры", values="budget", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="year", ascending=False)

st.dataframe(
    df_reshaped,
    use_container_width=True,
    column_config={"year": st.column_config.TextColumn("Год")},
)

df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="year", var_name="Жанры", value_name="budget"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("year:N", title="Год"),
        y=alt.Y("budget:Q", title="Бюджет ($)"),
        color="Жанры:N",
    )
    .properties(height=320)
)
# График
st.altair_chart(chart, use_container_width=True)

# Данные
st.dataframe(df_filtered)
