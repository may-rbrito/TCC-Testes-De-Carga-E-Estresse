import time
import httpx
import asyncio
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Armazenar os resultados
group_durations = []
success_counts_per_group = []
group_means = []
group_std_devs = []

# Realizar as requisições
async def req_get_async(client, url):
    try:
        start = time.time()
        response = await client.get(url)
        end = time.time()
        duration = end - start
        return response, duration
    except httpx.RequestError:
        return None, None

async def do_load_test(url, num_requests):
    async with httpx.AsyncClient() as client:
        tasks = [req_get_async(client, url) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

async def run_load_test(url, delay_in_seconds, num_requests, qtty_of_groups):
    for _ in range(qtty_of_groups):
        results = await do_load_test(url, num_requests)

        success_count = sum(1 for response, _ in results if response and response.status_code == 200)
        success_counts_per_group.append(success_count)

        durations_per_group = [duration for _, duration in results if duration is not None]
        
        total_time = sum(durations_per_group)
        group_durations.append(total_time)

        if durations_per_group:
            group_mean = total_time / len(durations_per_group)
            group_std_dev = np.std(durations_per_group)
        else:
            group_mean = 0
            group_std_dev = 0

        group_means.append(group_mean)
        group_std_devs.append(group_std_dev)

        if delay_in_seconds:
            await asyncio.sleep(delay_in_seconds)

    return group_durations, success_counts_per_group, group_means, group_std_devs

# Exibir os resultados
def plot_mean_and_std_dev(group_means, group_std_devs):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(1, len(group_means) + 1)),
        y=group_means,
        error_y=dict(type='data', array=group_std_devs),
        mode='lines+markers',
        name='Média com Desvio Padrão'
    ))

    fig.update_layout(
        xaxis_title="Número do Grupo",
        yaxis_title="Tempo (s)",
    )

    st.plotly_chart(fig)

def plot_total_time_per_group(group_durations):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(1, len(group_durations) + 1)),
        y=group_durations,
        mode='lines+markers',
        name="Tempo Total por Grupo",
    ))

    fig.update_layout(
        xaxis_title="Número do Grupo",
        yaxis_title="Tempo Total (s)",
    )

    st.plotly_chart(fig)

def plot_success_counts_per_group(success_counts_per_group, qtty_of_groups, num_requests):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=list(range(1, qtty_of_groups + 1)),
        y=[num_requests] * qtty_of_groups,
        name="Requisições Solicitadas",
        marker=dict(color='lightblue')
    ))

    fig.add_trace(go.Bar(
        x=list(range(1, qtty_of_groups + 1)),
        y=success_counts_per_group,
        name="Requisições Bem-Sucedidas",
    ))

    fig.update_layout(
        xaxis_title="Número do Grupo",
        yaxis_title="Quantidade de Requisições",
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig)

def show_results_table(group_means, group_std_devs, group_durations, success_counts_per_group):
    data = {
        'Média (s)': group_means,
        'Desvio Padrão (s)': group_std_devs,
        'Tempo Total (s)': group_durations,
        'Requisições Bem-Sucedidas': success_counts_per_group
    }
    df = pd.DataFrame(data)
    st.dataframe(df,use_container_width=True)

# Interface da página 
def run_load_test_page():
    st.set_page_config(page_title="Teste de Carga", page_icon="🔃", layout="centered")

    st.title("Teste de Carga")
    
    url = st.text_input("Informe a URL para o teste:", "")
    num_requests = st.number_input("Número de requisições por grupo:", min_value=1)
    qtty_of_groups = st.number_input("Quantidade de grupos:", min_value=1)
    delay_in_seconds = st.number_input("Delay entre grupos (segundos):", min_value=1)
    

    if st.button("Iniciar Teste de Carga"):
        if url:
            with st.spinner("Executando o teste de carga..."):
                group_durations, success_counts_per_group, group_means, group_std_devs = asyncio.run(run_load_test(url, delay_in_seconds, num_requests, qtty_of_groups))

            st.success('Teste concluído!')
            
            st.subheader("Tempo médio de resposta com desvio padrão por grupo")	
            st.write("O gráfico abaixo mostra o tempo médio de resposta com desvio padrão por grupo.")
            plot_mean_and_std_dev(group_means, group_std_devs)

            st.subheader("Tempo total por grupo")
            st.write("O gráfico abaixo mostra o tempo total por grupo.")
            plot_total_time_per_group(group_durations)
            
            st.subheader("Requisições solicitadas e bem-sucedidas por grupo")
            st.write("O gráfico abaixo mostra a quantidade de requisições solicitadas e bem-sucedidas por grupo.")
            plot_success_counts_per_group(success_counts_per_group, qtty_of_groups, num_requests)

            st.subheader("Tabela de resultados do Teste de Carga")
            st.write("A tabela abaixo mostra os resultados do teste de carga.")
            show_results_table(group_means, group_std_devs, group_durations, success_counts_per_group)

        else:
            st.warning("Por favor, informe uma URL válida.")

# Executar a página 
if __name__ == "__main__":
    run_load_test_page()
    