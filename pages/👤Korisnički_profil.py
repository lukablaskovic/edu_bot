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
    st.markdown(f'Hej {name} 👋')
    st.markdown('Ovdje možeš ažurirati svoje korisničke podatke. Ali please, nemoj unijeti lažne podatke. 🙏')
    st.sidebar.markdown("# Korisnički profil")
    st.sidebar.markdown(f"👤 {name}")
    
    with st.form(key="profile_form"):
        st.text_input("Korisničko ime", key="username", value=username)
        st.text_input("Ime i prezime", key="name", value=name)
        st.selectbox("Godina studija", ["1. prijediplomski", "2. prijediplomski", "3. prijediplomski", "1. diplomski", "2. diplomski"], key="study_year")

        st.form_submit_button("Ažuriraj")
        
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"], fields={"Form name":"Resetiraj lozinku", "Current password":"Trenutna lozinka", "New password":"Nova lozinka", "Repeat password": "Ponovi lozinku", "Reset": "Resetiraj"}):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)

else:
    st.error("Moraš biti prijavljen za ovo!")
