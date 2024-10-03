import time
import httpx
import asyncio
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Função para realizar uma requisição GET assíncrona
async def req_get_async(client, url):
    try:
        start = time.time()
        response = await client.get(url)
        end = time.time()
        duration = end - start
        return response, duration
    except httpx.RequestError as e:
        #st.write(f"Erro na requisição: {e}")
        return None, None

# Função para realizar o teste de carga com múltiplas requisições
async def do_load_test(url, num_requests):
    async with httpx.AsyncClient() as client:
        tasks = [req_get_async(client, url) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

# Função para executar o teste de carga
async def run_load_test(url, delay_in_seconds, num_requests, qtty_of_groups):
    group_durations = []
    success_counts_per_group = []
    group_means = []
    group_std_devs = []

    for _ in range(qtty_of_groups):
        start_time = time.time()
        results = await do_load_test(url, num_requests)

        success_count = sum(1 for response, _ in results if response and response.status_code == 200)
        success_counts_per_group.append(success_count)

        total_time = time.time() - start_time
        group_durations.append(total_time)

        durations_per_group = [duration for _, duration in results if duration is not None]
        if durations_per_group:
            group_mean = np.mean(durations_per_group)
            group_std_dev = np.std(durations_per_group)
        else:
            group_mean = 0
            group_std_dev = 0

        group_means.append(group_mean)
        group_std_devs.append(group_std_dev)

        if delay_in_seconds:
            await asyncio.sleep(delay_in_seconds)

    return group_durations, success_counts_per_group, group_means, group_std_devs

# Função para plotar a média, desvio padrão e tempo total por grupo
def plot_mean_std_dev_and_total_time(group_means, group_std_devs, group_durations):
    plt.figure(figsize=(10, 5))
    group_indexes = range(len(group_means))

    plt.plot(group_indexes, group_means, marker='o', linestyle='-', color='b', label='Média dos Tempos de Resposta')
    plt.errorbar(group_indexes, group_means, yerr=group_std_devs, fmt='none', ecolor='r', capsize=5, label='Desvio Padrão')
    plt.plot(group_indexes, group_durations, marker='x', linestyle='-', color='g', label='Tempo Total por Grupo')

    plt.title('Média, Desvio Padrão e Tempo Total por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Tempo (segundos)')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

# Função para plotar a contagem de sucessos por grupo
def plot_success_counts_per_group(success_counts_per_group, qtty_of_groups):
    plt.figure(figsize=(10, 5))
    plt.bar(range(1, qtty_of_groups + 1), success_counts_per_group, color='g')

    plt.title('Requisições Bem-Sucedidas por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Quantidade de Requisições Bem-Sucedidas')
    plt.grid(True)
    st.pyplot(plt)

# Função que gera a interface do Streamlit para a página de Teste de Carga
def run_load_test_page():
    st.title("Teste de Carga")
    
    url = st.text_input("Informe a URL para o teste:", "")
    num_requests = st.number_input("Número de requisições por grupo:", min_value=1)
    qtty_of_groups = st.number_input("Quantidade de grupos:", min_value=1)
    delay_in_seconds = st.number_input("Delay entre grupos (segundos):", min_value=1)

    if st.button("Iniciar Teste de Carga"):
        group_durations, success_counts_per_group, group_means, group_std_devs = asyncio.run(
            run_load_test(url, delay_in_seconds, num_requests, qtty_of_groups)
        )

        st.write(f"Resultados do teste para {url}:")
        plot_mean_std_dev_and_total_time(group_means, group_std_devs, group_durations)
        plot_success_counts_per_group(success_counts_per_group, qtty_of_groups)
