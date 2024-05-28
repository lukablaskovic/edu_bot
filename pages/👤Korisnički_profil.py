import streamlit as st
from auth import load_config, get_authenticator, login

st.set_page_config(
    page_title="Korisnički profil",
    page_icon="👤",
)

config = load_config()
authenticator = get_authenticator(config)

name, authentication_status, username = login(authenticator)


if authentication_status:
    st.title('👤Korisnički profil')
    st.sidebar.markdown("# Korisnički profil")
else:
    st.error("Moraš biti prijavljen za ovo!")
