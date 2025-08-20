import streamlit as st 

sauny_page = st.Page("sauny/sauny.py", title="Ofertownik Sauny", icon=":material/add_circle:")
domki_page = st.Page("domki/domki.py", title="Ofertownik Domki", icon=":material/add_circle:")

pg = st.navigation([sauny_page, domki_page])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()