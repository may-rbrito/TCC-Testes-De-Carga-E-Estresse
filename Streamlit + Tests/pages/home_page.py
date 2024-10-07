import streamlit as st
from pages import load_test_page, stress_test_page

def home():
    st.title("Página Inicial")
    st.write("Bem-vindo ao meu aplicativo. Explore as seções abaixo.")

    st.write("## Teste de Carga")
    st.write("Um teste de carga tem como objetivo medir como um sistema (como um servidor ou aplicativo) se comporta sob uma carga específica, ou seja, quantas requisições ele pode processar de forma eficaz. O foco é garantir que o sistema funcione adequadamente quando é submetido a uma quantidade esperada de tráfego.")

    if st.button("Teste de Carga"):
        load_test_page.run_load_test_page()

    st.markdown("---")

    st.write("## Teste de Estresse")
    st.write("Um teste de estresse é projetado para avaliar os limites do sistema, ou seja, até que ponto ele pode suportar uma carga antes de falhar. O foco é descobrir o ponto em que o sistema começa a apresentar falhas, como lentidão ou erros, quando submetido a uma carga muito alta.")

    if st.button("Teste de Estresse"):
       stress_test_page.run_stress_test_page()

    