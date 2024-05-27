import streamlit as st
import os

col_logo, col_title = st.columns([0.25, 0.75])
col_logo.image(
    "https://www.itps.org.br/imagens/itps.svg", 
    width=150
)
col_title.title("Hub")

st.divider()

col_central_arbo, col_central_respat = st.columns(2)

col_central_arbo.link_button(
    ":mosquito: Arbo", "arbo", use_container_width = True
)
col_central_respat.link_button(
    ":lungs: Respat", "respat", use_container_width = True
)
