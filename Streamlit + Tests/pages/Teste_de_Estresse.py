import time
import httpx
import asyncio
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Armazenar os resultados
group_durations = []
success_counts_per_group = []
total_requests_per_group = []
individual_durations = []
response_rates = []

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
    num_requests = initial_num_requests

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

        if success_rate < 0.50:
            break

        num_requests += increment

        if delay_in_seconds:
            await asyncio.sleep(delay_in_seconds)

def plot_time_per_group():
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

def plot_success_requests():
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
        yaxis_title="Número de Requisições",
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
        "Tempo Gasto (s)": group_durations,
        "Requisições Bem-Sucedidas": success_counts_per_group,
        "Total de Requisições": total_requests_per_group,
        "Taxa de Sucesso": response_rates
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

# Interface da página 
def run_stress_test_page():
    st.set_page_config(page_title="Teste de Estresse", page_icon="🚩", layout="centered")

    st.title("Teste de Estresse")

    url = st.text_input("Informe a URL para o teste:", "")
    initial_num_requests = st.number_input("Número inicial de requisições:", min_value=1)
    increment = st.number_input("Incremento de requisições:", min_value=1)
    delay_in_seconds = st.number_input("Delay entre grupos (segundos):", min_value=1)

    if st.button("Iniciar Teste de Estresse"):
        if url:
            asyncio.run(run_stress_test(url, initial_num_requests, increment, delay_in_seconds))

            st.subheader("Tempo Gasto por Grupo")
            st.write("Tempo gasto em segundos para cada grupo.")
            plot_time_per_group()

            st.subheader("Requisições Bem-Sucedidas e Totais por Grupo")
            st.write("Número de requisições bem-sucedidas e totais para cada grupo.")
            plot_success_requests()

            st.subheader("Taxa de Sucesso por Grupo")
            st.write("Taxa de sucesso para cada grupo.")
            plot_success_rate()

            st.subheader("Tabela de Resultados")
            st.write("Tabela com os resultados obtidos.")
            show_results_table()

if __name__ == "__main__":
    run_stress_test_page()
