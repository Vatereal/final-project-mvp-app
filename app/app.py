import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path

st.set_page_config('Динамика зарплат и инфляции', layout='wide')
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

@st.cache_data
def load_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / f'{name}.csv', index_col=0)
    df.columns = df.columns.astype(int)
    return df

nominal     = load_csv('nominal')
real        = load_csv('real')
growth_nom  = load_csv('growth_nom')
growth_real = load_csv('growth_real')

YEARS   = nominal.columns.tolist()
SECTORS = nominal.index.tolist()

st.sidebar.header('Параметры')
selected_sectors = st.sidebar.multiselect(
    'Отрасли', SECTORS, default=SECTORS[:3]
)
year_from, year_to = st.sidebar.slider(
    'Диапазон лет', YEARS[0], YEARS[-1], (YEARS[0], YEARS[-1]), step=1
)

def subset(df: pd.DataFrame, value_name: str) -> pd.DataFrame:
    df2 = df.loc[selected_sectors, [y for y in YEARS if year_from <= y <= year_to]]
    return (
        df2.reset_index()
           .melt('sector', var_name='year', value_name=value_name)
    )

tab_nom, tab_real, tab_growth = st.tabs(['Номинальные', 'Реальные', 'Темпы роста'])

with tab_nom:
    st.subheader('Номинальная зарплата, ₽')
    data = subset(nominal, 'salary')
    chart = (
        alt.Chart(data)
           .mark_line(point=True)
           .encode(
               x='year:O',
               y='salary:Q',
               color='sector:N',
               tooltip=['sector','year',alt.Tooltip('salary',format=',.0f')]
           )
           .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

with tab_real:
    st.subheader('Реальная зарплата (цены 2000 г.)')
    data = subset(real, 'salary_real')
    chart = (
        alt.Chart(data)
           .mark_line(point=True)
           .encode(
               x='year:O',
               y='salary_real:Q',
               color='sector:N',
               tooltip=['sector','year',alt.Tooltip('salary_real',format=',.0f')]
           )
           .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

with tab_growth:
    st.subheader('Темпы роста, % к предыдущему году')
    dn = subset(growth_nom, 'growth');  dn['type']='номинальная'
    dr = subset(growth_real,'growth');  dr['type']='реальная'
    data = pd.concat([dn, dr])
    chart = (
        alt.Chart(data)
           .mark_line(point=True)
           .encode(
               x='year:O',
               y='growth:Q',
               color='sector:N',
               strokeDash='type:N',
               tooltip=['sector','type','year',alt.Tooltip('growth',format='.1f')]
           )
           .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

st.caption('Данные: Росстат')
