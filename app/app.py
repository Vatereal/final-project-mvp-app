import pandas as pd
import altair as alt
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config('Динамика зарплат и инфляции (Neon)', layout='wide')

engine = create_engine(st.secrets["db_url"], pool_pre_ping=True)

@st.cache_data(ttl=3600)
def fetch(table: str) -> pd.DataFrame:
    return pd.read_sql(text(f"SELECT * FROM {table}"), engine)

salary_nom  = fetch('salaries')
salary_real = fetch('salaries_real')
growth_nom  = fetch('growth_nom')
growth_real = fetch('growth_real')

YEARS   = sorted(salary_nom.year.unique())
SECTORS = sorted(salary_nom.sector.unique())

sel_sectors = st.sidebar.multiselect('Отрасли', SECTORS, default=SECTORS[:3])
y1, y2      = st.sidebar.slider('Диапазон лет', YEARS[0], YEARS[-1], (YEARS[0], YEARS[-1]))

def prep(df, col):
    df2 = df[df.sector.isin(sel_sectors) & df.year.between(y1, y2)].copy()
    return df2.rename(columns={col: 'value'})

tabs = st.tabs(['Номинальные', 'Реальные', 'Темпы роста'])

with tabs[0]:
    st.subheader('Номинальная зарплата, ₽')
    df = prep(salary_nom, 'salary_nom')
    st.altair_chart(
        alt.Chart(df).mark_line(point=True)
           .encode(
               x='year:O', y=alt.Y('value:Q', title='₽'),
               color='sector:N',
               tooltip=['sector','year',alt.Tooltip('value:Q',format=',.0f')]
           )
           .interactive(),
        use_container_width=True
    )

with tabs[1]:
    st.subheader('Реальная зарплата (цены 2000 г.)')
    df = prep(salary_real, 'salary_real')
    st.altair_chart(
        alt.Chart(df).mark_line(point=True)
           .encode(
               x='year:O', y=alt.Y('value:Q', title='₽ 2000 г.'),
               color='sector:N',
               tooltip=['sector','year',alt.Tooltip('value:Q',format=',.0f')]
           )
           .interactive(),
        use_container_width=True
    )

with tabs[2]:
    st.subheader('Темпы роста, % к предыдущему году')
    nom = prep(growth_nom, 'growth_nom'); nom['type'] = 'номинальная'
    rea = prep(growth_real,'growth_real'); rea['type'] = 'реальная'
    df = pd.concat([nom, rea])
    st.altair_chart(
        alt.Chart(df).mark_line(point=True)
           .encode(
               x='year:O', y=alt.Y('value:Q', title='%'),
               color='sector:N', strokeDash='type:N',
               tooltip=['sector','type','year',alt.Tooltip('value:Q',format='.1f')]
           )
           .interactive(),
        use_container_width=True
    )

st.caption('Источник: Росстат • Хранилище: Neon PostgreSQL')
