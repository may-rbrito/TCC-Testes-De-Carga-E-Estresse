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

# Mensagens sobre a url
def performance(response_time):
    if response_time < 0.2:
        return st.success('Excelente: Tempo de resposta < 200 ms (Tempo médio de resposta: {:.2f} ms)'.format(response_time * 1000))
    elif 0.2 <= response_time < 0.5:
        return st.info('Boa: Tempo de resposta entre 200 ms e 500 ms (Tempo médio de resposta: {:.2f} ms)'.format(response_time * 1000))
    elif 0.5 <= response_time < 1:
        return st.warning('Regular: Tempo de resposta entre 500 ms e 1 segundo (Tempo médio de resposta: {:.2f} ms)'.format(response_time * 1000))
    else:
        return st.error('Ruim: Tempo de resposta > 1 segundo (Tempo médio de resposta: {:.2f} ms)'.format(response_time * 1000))

def consistency(std_dev):
    if std_dev< 0.1:
        return st.success('Estável: Os tempos de resposta as requisições são regulares (Desvio padrão: {:.2f})'.format(std_dev))
    else:
        return st.error('Instável: Os tempos de resposta as requisições são irregulares (Desvio padrão: {:.2f})'.format(std_dev))

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
    for i in range(qtty_of_groups):
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
        error_y=dict(color='lightblue', type='data', array=group_std_devs),
        mode='lines+markers',
        name='Média com Desvio Padrão',
        marker=dict(color='lightblue', size=5),
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
        marker=dict(color='lightblue', size=8),
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
        marker=dict(color='blue'),
        width=0.2 
    ))

    fig.add_trace(go.Bar(
        x=list(range(1, qtty_of_groups + 1)),
        y=success_counts_per_group,
        name="Requisições Bem-Sucedidas",
        marker=dict(color='lightblue'),
        width=0.2
    ))

    fig.update_layout(
        xaxis_title="Número do Grupo",
        yaxis_title="Quantidade de Requisições",
        barmode='overlay',
        bargap=0.2,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig)

def show_results_table(group_means, group_std_devs, group_durations, success_counts_per_group, num_requests):
    data = {
        'Média (s)': group_means,
        'Desvio Padrão (s)': group_std_devs,
        'Tempo Total (s)': group_durations,
        'Requisições Bem-Sucedidas': success_counts_per_group,
        'Requisições Solicitadas': num_requests
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

# Interface da página 
def run_load_test_page():
    st.set_page_config(page_title="Teste de Carga", page_icon="🔃", layout="centered")

    st.title("Teste de Carga")
    
    url = st.text_input("Informe a URL para o teste:", "")
    num_requests = st.number_input("Número de requisições por grupo:", min_value=1)
    qtty_of_groups = st.number_input("Quantidade de grupos:", min_value=1)
    delay_in_seconds = st.number_input("Delay entre grupos (segundos):", min_value=1)

    start_button = st.button("Iniciar Teste de Carga", disabled=not url)

    if start_button:
        with st.spinner("Executando o teste de carga..."):
            group_durations, success_counts_per_group, group_means, group_std_devs = asyncio.run(run_load_test(url, delay_in_seconds, num_requests, qtty_of_groups))
            
            response_time_geral = np.mean(group_means)
            std_dev_geral = np.mean(group_std_devs)
            performance(response_time_geral)
            consistency(std_dev_geral)

            st.subheader("Tempo médio de resposta com desvio padrão por grupo")	
            st.write("Este gráfico mostra o tempo médio de resposta e a variação (desvio padrão) em cada grupo.")
            plot_mean_and_std_dev(group_means, group_std_devs)

            st.subheader("Tempo total por grupo")
            st.write("O gráfico exibe o tempo total gasto pelo servidor para processar todas as requisições de cada grupo, refletindo o esforço do servidor.")
            plot_total_time_per_group(group_durations)
            
            st.subheader("Requisições solicitadas e bem-sucedidas por grupo")
            st.write("Este gráfico compara o número de requisições solicitadas com as bem-sucedidas em cada grupo, destacando a taxa de sucesso do servidor.")
            plot_success_counts_per_group(success_counts_per_group, qtty_of_groups, num_requests)

            st.subheader("Tabela de resultados do Teste de Carga")
            st.write("A tabela resume os resultados por grupo, incluindo tempos médios, variação, tempo total e requisições bem-sucedidas, para avaliar o desempenho do servidor.")
            show_results_table(group_means, group_std_devs, group_durations, success_counts_per_group, num_requests)

if __name__ == "__main__":
    run_load_test_page()
