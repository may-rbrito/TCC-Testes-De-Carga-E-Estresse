import streamlit as st

def home():
    st.set_page_config(page_title="Página Inicial", page_icon="🏠", layout="centered")
    st.title("Página Inicial")

    st.write("Este aplicativo foi desenvolvido como parte do meu Trabalho de Conclusão de Curso (TCC) para o curso de Engenharia Elétrica da Universidade do Estado do Rio de Janeiro.")
    st.info("Na barra lateral, você pode acessar as opções para realizar os **Testes de Carga e de Estresse**. Para executar os testes, será necessário ter uma **API pública** que possa ser acessada. Certifique-se de que a URL fornecida esteja disponível e que você tenha permissão para realizar os testes.")

    st.write("## Teste de Carga 🔄️")
    st.write("Um teste de carga tem como objetivo medir como um sistema (como um servidor ou aplicativo) se comporta sob uma carga específica. Para realizar um teste de carga, os requisitos são os seguintes:")
    
    st.write("- **URL**: A URL da API que você deseja testar.")
    st.write("- **Número de requisições por grupo**: Quantas requisições serão enviadas em cada grupo.")
    st.write("- **Número de grupos**: Quantos grupos de requisições você deseja enviar durante o teste.")
    st.write("- **Delay entre grupos**: O tempo de espera (em segundos) entre o envio de cada grupo de requisições.")

    st.markdown("---")

    st.write("## Teste de Estresse 🚩")
    st.write("Um teste de estresse é projetado para avaliar os limites do sistema. Para realizar um teste de estresse, os requisitos são:")
    
    st.write("- **URL**: A URL da API que você deseja testar.")
    st.write("- **Número de requisições inicial**: O número de requisições a serem enviadas no primeiro grupo.")
    st.write("- **Quantidade de incremento**: O número de requisições a serem adicionadas em cada grupo subsequente.")
    st.write("- **Delay entre grupos**: O tempo de espera (em segundos) entre o envio de cada grupo de requisições.")

# Executa a home_page como a página principal
if __name__ == "__main__":
    home()
