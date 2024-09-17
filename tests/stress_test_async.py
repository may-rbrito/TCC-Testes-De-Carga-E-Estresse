import time
import httpx
import asyncio
import matplotlib.pyplot as plt


url = 'https://pitrol.dev/aouerj/reportError'

# Configurações para o teste
initial_num_requests = 10  # Número inicial de requisições
increment = 10  # Incremento de requisições a cada intervalo
delay_in_seconds = 1  # Tempo de espera em segundos entre cada conjunto de requisições

# Listas para armazenar os resultados
group_durations = []  # Tempo total gasto por grupo de requisições
success_counts_per_group = []  # Contador de requisições bem-sucedidas por grupo
individual_durations = []  # Lista para armazenar o tempo gasto em cada requisição
response_rates = []  # Lista para armazenar a taxa de sucesso de cada grupo

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

async def do_stress_test(num_requests):
    async with httpx.AsyncClient() as client:
        tasks = [req_get_async(client) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

async def run_stress_test():
    num_requests = initial_num_requests

    while True:
        start_time = time.time()

        # Executar o teste de carga assíncrono
        results = await do_stress_test(num_requests)

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

        # Imprimir informações de sucesso e erro
        #print(f"Grupo: {len(group_durations)}, Requisições: {num_requests}, Sucessos: {success_count}, Erros: {error_count}, Taxa de erro: {error_rate:.2%}")

        # Condição de parada baseada na taxa de erro
        if error_rate > 0.50:
            print("Taxa de erro maior que 50%. Encerrando o teste.")
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
    plt.show()

# Plotar o número de requisições bem-sucedidas por grupo (gráfico de barras)
def plot_success_counts_per_group():
    plt.figure(figsize=(10, 5))
    plt.bar(range(1, len(success_counts_per_group) + 1), success_counts_per_group, color='g')
    plt.title('Requisições Bem-Sucedidas por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Quantidade de Requisições Bem-Sucedidas')
    plt.grid(True)
    plt.show()

# Plotar a taxa de sucesso por grupo
def plot_response_rates():
    plt.figure(figsize=(10, 5))
    plt.plot(response_rates, marker='o', linestyle='-', color='r')
    plt.title('Taxa de Sucesso por Grupo')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Taxa de Sucesso')
    plt.grid(True)
    plt.show()

# Iniciar o teste de carga
asyncio.run(run_stress_test())
plot_group_durations()
plot_success_counts_per_group()
plot_response_rates()
