import time
import httpx
import asyncio
import matplotlib.pyplot as plt
import numpy as np

url = 'https://pitrol.dev/aouerj/reportError'

# Configurações para o teste
delay_in_seconds = 1  # Tempo de espera em segundos entre cada conjunto de requisições
num_requests = 100  # Número de requisições a serem feitas a cada intervalo
qtty_of_groups = 30  # Quantidade de grupos

# Listas para armazenar os resultados
group_durations = []  # Tempo total gasto por grupo de requisições
success_counts_per_group = []  # Contador de requisições bem-sucedidas por grupo
individual_durations = []  # Lista para armazenar o tempo gasto em cada requisição
group_means = []  # Médias dos tempos de resposta por grupo
group_std_devs = []  # Desvios padrão dos tempos de resposta por grupo

async def req_get_async(client):
    try:
        start = time.time()
        response = await client.get(url)
        end = time.time()
        duration = end - start
        return response, duration

    except httpx.RequestError as e:
        print(f"Erro na requisição: {e}")
        return None, None

async def do_load_test():
    async with httpx.AsyncClient() as client:
        tasks = [req_get_async(client) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

async def run_load_test():
    for _ in range(qtty_of_groups):
        start_time = time.time()

        # Executar o teste de carga assíncrono
        results = await do_load_test()

        # Processar os resultados
        success_count = sum(1 for response, _ in results if response and response.status_code == 200)
        total_time = time.time() - start_time

        # Armazenar o número de requisições bem-sucedidas neste grupo
        success_counts_per_group.append(success_count)

        # Armazenar os tempos individuais das requisições deste grupo
        group_durations_per_group = [duration for _, duration in results if duration is not None]
        individual_durations.extend(group_durations_per_group)

        # Armazenar o tempo total do grupo
        group_durations.append(total_time)

        # Calcular e armazenar a média e o desvio padrão dos tempos de resposta deste grupo
        if group_durations_per_group:
            group_mean = np.mean(group_durations_per_group)
            group_std_dev = np.std(group_durations_per_group)
        else:
            group_mean = 0
            group_std_dev = 0

        group_means.append(group_mean)
        group_std_devs.append(group_std_dev)

        # Esperar antes do próximo grupo, se necessário
        if delay_in_seconds: await asyncio.sleep(delay_in_seconds)

# Plotar o tempo gasto por grupo de requisições com a média e o desvio padrão sobrepostos
def plot_group_durations():
    plt.figure(figsize=(10, 5))

    group_indexes = range(len(group_durations))

    # Plotar o tempo total gasto por grupo
    plt.plot(group_indexes, group_durations, marker='o', linestyle='-', color='b', label='Tempo Total por Grupo')

    # Plotar a média dos tempos de resposta por grupo
    plt.plot(group_indexes, group_means, marker='x', linestyle='--', color='g', label='Média dos Tempos de Resposta')

    # Plotar o desvio padrão dos tempos de resposta por grupo
    plt.errorbar(group_indexes, group_means, yerr=group_std_devs, fmt='s', color='r', label='Desvio Padrão')

    # Personalizar o gráfico
    plt.title('Tempo Total, Média e Desvio Padrão dos Tempos de Resposta por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Tempo (segundos)')
    plt.legend()
    plt.grid(True)
    plt.show()

# Plotar o número de requisições bem-sucedidas por grupo (gráfico de barras)
def plot_success_counts_per_group():
    plt.figure(figsize=(10, 5))
    plt.bar(range(1, qtty_of_groups + 1), success_counts_per_group, color='g')
    plt.title('Requisições Bem-Sucedidas por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Quantidade de Requisições Bem-Sucedidas')
    plt.grid(True)
    plt.show()

# Iniciar o teste de carga
asyncio.run(run_load_test())
plot_group_durations()
plot_success_counts_per_group()
