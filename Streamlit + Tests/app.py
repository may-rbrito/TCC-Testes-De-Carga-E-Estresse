import streamlit as st
from pages import home_page, load_test_page, stress_test_page

st.sidebar.title("Navegação")
option = st.sidebar.selectbox("Escolha a página", ["Página Inicial 🏠", "Teste de Carga 🔄️", "Teste de Estresse 🚩"])

if option == "Página Inicial 🏠":
    home_page.home()
elif option == "Teste de Carga 🔄️":
    load_test_page.run_load_test_page()
elif option == "Teste de Estresse 🚩":
    stress_test_page.run_stress_test_page() 
