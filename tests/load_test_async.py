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

# Função para realizar requisições assíncronas
async def req_get_async(client):
    try:
        start = time.time()
        response = await client.get(url)
        end = time.time()
        duration = end - start  # Calcula o tempo de cada requisição
        return response, duration
    except httpx.RequestError as e:
        print(f"Erro na requisição: {e}")
        return None, None

# Função para executar o teste de carga
async def do_load_test():
    async with httpx.AsyncClient() as client:
        tasks = [req_get_async(client) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

# Função principal do teste de carga
async def run_load_test():
    for _ in range(qtty_of_groups):
        start_time = time.time()  # Marca o início do grupo

        # Executa o grupo de requisições
        results = await do_load_test()

        # Conta as requisições bem-sucedidas (status 200)
        success_count = sum(1 for response, _ in results if response and response.status_code == 200)
        success_counts_per_group.append(success_count)

        # Calcula o tempo total gasto pelo grupo de requisições
        total_time = time.time() - start_time
        group_durations.append(total_time)

        # Armazena os tempos de cada requisição dentro deste grupo
        durations_per_group = [duration for _, duration in results if duration is not None]
        individual_durations.extend(durations_per_group)

        # Calcula a média e o desvio padrão dos tempos de resposta no grupo
        if durations_per_group:
            group_mean = np.mean(durations_per_group)
            group_std_dev = np.std(durations_per_group)
        else:
            group_mean = 0
            group_std_dev = 0

        group_means.append(group_mean)
        group_std_devs.append(group_std_dev)

        # Aguarda um intervalo antes de começar o próximo grupo, se necessário
        if delay_in_seconds:
            await asyncio.sleep(delay_in_seconds)

# Plotar a média dos tempos de resposta por grupo com o desvio padrão sobreposto e o tempo total por grupo
def plot_mean_std_dev_and_total_time():
    plt.figure(figsize=(10, 5))

    group_indexes = range(len(group_means))

    # Plotar a média dos tempos de resposta por grupo (linha sólida)
    plt.plot(group_indexes, group_means, marker='o', linestyle='-', color='b', label='Média dos Tempos de Resposta')

    # Plotar o desvio padrão dos tempos de resposta em cor diferente (somente barras de erro)
    plt.errorbar(group_indexes, group_means, yerr=group_std_devs, fmt='none', ecolor='r', capsize=5, label='Desvio Padrão')

    # Plotar o tempo total de duração por grupo (linha sólida sobreposta)
    plt.plot(group_indexes, group_durations, marker='x', linestyle='-', color='g', label='Tempo Total por Grupo')

    # Personalizar o gráfico
    plt.title('Média, Desvio Padrão e Tempo Total por Grupo (Sobrepostos)')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Tempo (segundos)')
    plt.legend()
    plt.grid(True)
    plt.show()

# Plotar o número de requisições bem-sucedidas por grupo
def plot_success_counts_per_group():
    plt.figure(figsize=(10, 5))

    # Plotar o número de sucessos por grupo (gráfico de barras)
    plt.bar(range(1, qtty_of_groups + 1), success_counts_per_group, color='g')

    # Personalizar o gráfico
    plt.title('Requisições Bem-Sucedidas por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Quantidade de Requisições Bem-Sucedidas')
    plt.grid(True)
    plt.show()

# Iniciar o teste de carga
asyncio.run(run_load_test())

# Gerar os gráficos
plot_mean_std_dev_and_total_time()
plot_success_counts_per_group()
