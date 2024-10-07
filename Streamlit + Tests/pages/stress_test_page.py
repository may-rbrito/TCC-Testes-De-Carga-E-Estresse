import time
import httpx
import asyncio
import streamlit as st
import pandas as pd  
import plotly.graph_objects as go

# Listas para armazenar os resultados
group_durations = []  # Tempo total gasto por grupo de requisições
success_counts_per_group = []  # Contador de requisições bem-sucedidas por grupo
total_requests_per_group = []  # Total de requisições feitas por grupo
individual_durations = []  # Lista para armazenar o tempo gasto em cada requisição
response_rates = []  # Lista para armazenar a taxa de sucesso de cada grupo

async def req_get_async(client, url):
    try:
        start = time.time()
        response = await client.get(url)
        end = time.time()
        duration = end - start
        return response, duration
    except httpx.RequestError as e:
        return None, None

async def do_stress_test(url, num_requests):
    async with httpx.AsyncClient() as client:
        tasks = [req_get_async(client, url) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

async def run_stress_test(url, initial_num_requests, increment, delay_in_seconds):
    num_requests = initial_num_requests

    while True:
        start_time = time.time()

        # Executar o teste de estresse assíncrono
        results = await do_stress_test(url, num_requests)

        # Processar os resultados
        success_count = sum(1 for response, _ in results if response and response.status_code == 200)
        total_time = time.time() - start_time
        total_requests = len(results)
        error_count = total_requests - success_count

        # Calcular a taxa de sucesso e erro
        success_rate = success_count / total_requests if total_requests > 0 else 0
        error_rate = error_count / total_requests if total_requests > 0 else 0

        # Armazenar a taxa de sucesso
        response_rates.append(success_rate)

        # Armazenar o número de requisições bem-sucedidas e totais
        success_counts_per_group.append(success_count)
        total_requests_per_group.append(total_requests)

        # Armazenar o tempo de cada requisição individual
        individual_durations.extend(duration for _, duration in results if duration is not None)

        # Armazenar os resultados de tempo gasto
        group_durations.append(total_time)

        # Condição de parada baseada na taxa de sucesso
        if success_rate < 0.50:
            #st.write("Taxa de sucesso menor que 50%. Encerrando o teste.")
            break

        # Incrementar o número de requisições
        num_requests += increment

        # Esperar antes do próximo grupo
        if delay_in_seconds: await asyncio.sleep(delay_in_seconds)

# Função que gera a interface do Streamlit para a página de Teste de Estresse
def run_stress_test_page():
    st.title("Teste de Estresse")

    url = st.text_input("Informe a URL para o teste:", "")
    initial_num_requests = st.number_input("Número inicial de requisições:", min_value=1)
    increment = st.number_input("Incremento de requisições:", min_value=1)
    delay_in_seconds = st.number_input("Delay entre grupos (segundos):", min_value=1)

    if st.button("Iniciar Teste de Estresse"):
        if url:  # Verifica se a URL foi fornecida
            asyncio.run(run_stress_test(url, initial_num_requests, increment, delay_in_seconds))

            # Criar DataFrame com os resultados
            results_df = pd.DataFrame({
                "Grupo": range(1, len(group_durations) + 1),
                "Tempo Gasto (s)": group_durations,
                "Requisições Bem-Sucedidas": success_counts_per_group,
                "Total de Requisições": total_requests_per_group,
                "Taxa de Sucesso": response_rates
            })

            # Estilizar a tabela
            styled_table = results_df.style \
                .set_table_attributes('style="width:100%; text-align: center;"') \
                .set_caption("Resultados do Teste de Estresse") \
                .set_table_styles(
                    [ 
                        {"selector": "th", "props": [("background-color", "#4CAF50"), 
                                                       ("color", "white"), 
                                                       ("font-weight", "bold"), 
                                                       ("text-align", "center")]} 
                    ]
                )

            st.subheader("Resultados do Teste de Estresse")
            st.write(styled_table)

            # Gráfico do tempo gasto por grupo
            fig_time = go.Figure()
            fig_time.add_trace(go.Scatter(x=list(range(1, len(group_durations) + 1)), 
                                            y=group_durations,
                                            mode='lines+markers', 
                                            name='Tempo Gasto (s)',
                                            marker=dict(size=8)))  # Adiciona marcadores
            fig_time.update_layout(title='Tempo Gasto por Grupo',
                                   xaxis_title='Grupo',
                                   yaxis_title='Tempo Gasto (s)',
                                   xaxis=dict(tickmode='linear', dtick=1))  # Define escala de 1 em 1
            st.plotly_chart(fig_time)

            # Gráfico de requisições bem-sucedidas e totais por grupo
            requests_data = pd.DataFrame({
                "Requisições Bem-Sucedidas": success_counts_per_group,
                "Total de Requisições": total_requests_per_group
            })
            fig_requests = go.Figure()
            fig_requests.add_trace(go.Bar(x=list(range(1, len(success_counts_per_group) + 1)), 
                                           y=success_counts_per_group, 
                                           name='Requisições Bem-Sucedidas'))
            fig_requests.add_trace(go.Bar(x=list(range(1, len(total_requests_per_group) + 1)), 
                                           y=total_requests_per_group, 
                                           name='Total de Requisições'))
            fig_requests.update_layout(title='Requisições Bem-Sucedidas e Totais por Grupo',
                                       xaxis_title='Grupo',
                                       yaxis_title='Número de Requisições')
            st.plotly_chart(fig_requests)

            # Gráfico da taxa de sucesso por grupo
            fig_response = go.Figure()
            fig_response.add_trace(go.Scatter(x=list(range(1, len(response_rates) + 1)), 
                                                y=response_rates,
                                                mode='lines+markers', 
                                                name='Taxa de Sucesso',
                                                marker=dict(size=8)))  # Adiciona marcadores
            fig_response.update_layout(title='Taxa de Sucesso por Grupo',
                                       xaxis_title='Grupo',
                                       yaxis_title='Taxa de Sucesso',
                                       xaxis=dict(tickmode='linear'))  # Define escala de 1 em 1
            st.plotly_chart(fig_response)


            #csv = results_df.to_csv(index=False).encode('utf-8')
            #st.download_button("Baixar Resultados em CSV", csv, "resultados.csv", "text/csv")
        else:
            st.warning("Por favor, informe uma URL válida.")

# Executar a página do teste de estresse
if __name__ == "__main__":
    run_stress_test_page()
