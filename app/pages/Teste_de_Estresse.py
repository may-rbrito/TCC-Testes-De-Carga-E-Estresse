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
total_requests_per_group = []
individual_durations = []
response_rates = []
group_means = []
group_std_devs = []
first_failure_group = None
failure_messages = []  # Armazena as mensagens de falha

# Mensagens sobre a url
def performance(response_time):
    if response_time < 0.5:
        return st.success('Latência Baixa: Tempo de resposta menor que 0.5 s (Tempo médio de resposta: {:.2f} s)'.format(response_time))
    elif 0.5 <= response_time < 1:
        return st.warning('Latência Moderada: Tempo de resposta entre 0.5 s e 1 s (Tempo médio de resposta: {:.2f} s)'.format(response_time))
    else:
        return st.error('Latência Alta: Tempo de resposta maior que 1 s (Tempo médio de resposta: {:.2f} s)'.format(response_time))

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

async def do_stress_test(url, num_requests):
    async with httpx.AsyncClient() as client:
        tasks = [req_get_async(client, url) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

async def run_stress_test(url, initial_num_requests, increment, delay_in_seconds):
    
    global first_failure_group, failure_messages
    num_requests = initial_num_requests
    group_number = 1

    while True:
        results = await do_stress_test(url, num_requests)

        success_count = sum(1 for response, _ in results if response and response.status_code == 200)

        durations_per_group = [duration for _, duration in results if duration is not None]

        total_time = sum(durations_per_group)
        total_requests = len(results)

        success_rate = success_count / total_requests if total_requests > 0 else 0
        response_rates.append(success_rate)

        success_counts_per_group.append(success_count)
        total_requests_per_group.append(total_requests)
        individual_durations.extend(durations_per_group)
        group_durations.append(total_time)

        if durations_per_group:
            group_mean = total_time / len(durations_per_group)
            group_std_dev = np.std(durations_per_group)
        else:
            group_mean = 0
            group_std_dev = 0

        group_means.append(group_mean)
        group_std_devs.append(group_std_dev)

        if first_failure_group is None and success_rate < 1.0:
            first_failure_group = group_number
            failure_messages.append(f"Grupo {group_number}: A taxa de sucesso de resposta neste grupo ficou abaixo de 100% pela primeira vez ({success_rate*100:.2f}%)")

        if success_rate < 0.50:
            failure_messages.append(f"Grupo {group_number}: A taxa de sucesso de resposta neste grupo ficou abaixo de 50% ({success_rate*100:.2f}%)")
            break

        num_requests += increment
        group_number += 1

        if delay_in_seconds:
            await asyncio.sleep(delay_in_seconds)

def plot_total_time_per_group():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(group_durations) + 1)),
        y=group_durations,
        mode='lines+markers',
        name='Tempo Gasto (s)',
        marker=dict(color='lightblue', size=10)
    ))

    fig.update_layout(
        xaxis_title="Grupo",
        yaxis_title="Tempo Gasto (s)",
        xaxis=dict(tickmode='linear', dtick=1)
    )

    st.plotly_chart(fig)

def plot_success_counts_per_group():
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=list(range(1, len(total_requests_per_group) + 1)),
        y=total_requests_per_group,
        name='Total de Requisições',
        marker=dict(color='blue'),
        width=0.2  
    ))

    fig.add_trace(go.Bar(
        x=list(range(1, len(success_counts_per_group) + 1)),
        y=success_counts_per_group,
        name='Requisições Bem-Sucedidas',
        marker=dict(color='lightblue'),
        width=0.2  
    ))

    fig.update_layout(
        xaxis_title="Grupo",
        yaxis_title="Quantidade de Requisições",
        barmode='overlay',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig)

def plot_success_rate():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(response_rates) + 1)),
        y=response_rates,
        mode='lines+markers',
        name='Taxa de Sucesso',
        marker=dict(color='lightblue', size=8)
    ))

    fig.update_layout(
        xaxis_title="Grupo",
        yaxis_title="Taxa de Sucesso",
        xaxis=dict(tickmode='linear')
    )

    st.plotly_chart(fig)

def show_results_table():
    data = {
        "Grupo": list(range(1, len(group_durations) + 1)),
        "Tempo Gasto (s)": group_durations,
        "Requisições Bem-Sucedidas": success_counts_per_group,
        "Requisições Solicitadas": total_requests_per_group,
        "Taxa de Sucesso": response_rates
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# Interface da página 
def run_stress_test_page():
    st.set_page_config(page_title="Teste de Estresse", page_icon="🚩", layout="centered")

    st.title("Teste de Estresse")

    url = st.text_input("Informe a URL para o teste:", "")
    initial_num_requests = st.number_input("Número inicial de requisições:", min_value=1)
    increment = st.number_input("Incremento de requisições:", min_value=1)
    delay_in_seconds = st.number_input("Delay entre grupos (segundos):", min_value=1)

    start_button = st.button("Iniciar Teste de Estresse", disabled=not url)

    if start_button:
        with st.spinner("Executando o teste de estresse..."):
            asyncio.run(run_stress_test(url, initial_num_requests, increment, delay_in_seconds))

        st.subheader("Resultados do Teste de Estresse")          
        for message in failure_messages:
            st.info(message)
        
        response_time_geral = np.mean(group_means)
        performance(response_time_geral) 

        st.subheader("Tempo gasto por grupo")
        st.write("O gráfico exibe o tempo total gasto pelo servidor para processar todas as requisições de cada grupo, refletindo o esforço do servidor.")
        plot_total_time_per_group()

        st.subheader("Requisições solicitadas e bem-sucedidas por grupo")
        st.write("Este gráfico compara o número de requisições solicitadas com as bem-sucedidas em cada grupo, destacando a taxa de sucesso do servidor.")
        plot_success_counts_per_group()

        st.subheader("Taxa de sucesso por grupo")
        st.write("O gráfico exibe a taxa de sucesso de resposta as requisições em cada grupo.")
        plot_success_rate()

        st.subheader("Tabela de resultados do Teste de Estresse")
        st.write("A tabela resume os resultados por grupo, incluindo tempo total, taxa de sucesso, requisições solicitadas e requisições bem-sucedidas, para avaliar o desempenho do servidor.")
        show_results_table()

if __name__ == "__main__":
    run_stress_test_page()
