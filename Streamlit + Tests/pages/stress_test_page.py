import time
import httpx
import asyncio
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Listas para armazenar os resultados
group_durations = []  # Tempo total gasto por grupo de requisições
success_counts_per_group = []  # Contador de requisições bem-sucedidas por grupo
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
        #st.write(f"Erro na requisição: {e}")
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
        success_rate = success_count / total_requests
        error_rate = error_count / total_requests

        # Armazenar a taxa de sucesso
        response_rates.append(success_rate)

        # Armazenar o número de requisições bem-sucedidas neste grupo
        success_counts_per_group.append(success_count)

        # Armazenar o tempo de cada requisição individual
        individual_durations.extend(duration for _, duration in results if duration is not None)

        # Armazenar os resultados de tempo gasto
        group_durations.append(total_time)

        # Condição de parada baseada na taxa de erro
        if error_rate > 0.50:
            st.write("Taxa de erro maior que 50%. Encerrando o teste.")
            break

        # Incrementar o número de requisições
        num_requests += increment

        # Esperar antes do próximo grupo
        if delay_in_seconds: await asyncio.sleep(delay_in_seconds)

# Plotar o tempo gasto por grupo de requisições
def plot_group_durations():
    plt.figure(figsize=(10, 5))
    plt.plot(group_durations, marker='o', linestyle='-', color='b')
    plt.title('Tempo Gasto por Grupo de Requisições')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Tempo (segundos)')
    plt.grid(True)
    st.pyplot(plt)

# Plotar o número de requisições bem-sucedidas por grupo (gráfico de barras)
def plot_success_counts_per_group():
    plt.figure(figsize=(10, 5))
    plt.bar(range(1, len(success_counts_per_group) + 1), success_counts_per_group, color='g')
    plt.title('Requisições Bem-Sucedidas por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Quantidade de Requisições Bem-Sucedidas')
    plt.grid(True)
    st.pyplot(plt)

# Plotar a taxa de sucesso por grupo
def plot_response_rates():
    plt.figure(figsize=(10, 5))
    plt.plot(response_rates, marker='o', linestyle='-', color='r')
    plt.title('Taxa de Sucesso por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Taxa de Sucesso')
    plt.grid(True)
    st.pyplot(plt)

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
            plot_group_durations()
            plot_success_counts_per_group()
            plot_response_rates()
        else:
            st.warning("Por favor, informe uma URL válida.")

