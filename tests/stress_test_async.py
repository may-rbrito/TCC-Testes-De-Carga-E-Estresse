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
total_success_counts = []  # Contador acumulado de requisições bem-sucedidas
individual_durations = []  # Lista para armazenar o tempo gasto em cada requisição

total_success = 0  # Contador total de requisições bem-sucedidas

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
    global total_success
    num_requests = initial_num_requests

    while True:
        start_time = time.time()
        #print(f"Realizando {num_requests} requisições...")

        # Executar o teste de carga assíncrono
        results = await do_stress_test(num_requests)

        # Processar os resultados
        success_count = sum(1 for response, _ in results if response and response.status_code == 200)
        total_time = time.time() - start_time

        # Atualizar o contador total de requisições bem-sucedidas
        total_success += success_count

        # Armazenar o tempo de cada requisição individual
        individual_durations.extend(duration for _, duration in results if duration is not None)

        # Armazenar os resultados
        group_durations.append(total_time)
        total_success_counts.append(total_success)

        # Incrementar o número de requisições
        num_requests += increment

        # Esperar antes do próximo grupo
        if delay_in_seconds: await asyncio.sleep(delay_in_seconds)  

        # Condição de parada simples, baseada em erros na requisição
        if any(response is None for response, _ in results):
            #print("O sistema não conseguiu processar todas as requisições. /nEncerrando o teste.")
            print(f"Total de requisições bem-sucedidas: {total_success}")
            break

# Plotar o tempo gasto por grupo de requisições
def plot_group_durations():
    plt.figure(figsize=(10, 5))
    plt.plot(group_durations, marker='o', linestyle='-', color='b')
    plt.title('Tempo Gasto por Grupo de Requisições')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Tempo (segundos)')
    plt.grid(True)
    plt.show()

# Plotar o total acumulado de requisições bem-sucedidas
def plot_total_success_counts():
    plt.figure(figsize=(10, 5))
    plt.plot(total_success_counts, marker='o', linestyle='-', color='g')
    plt.title('Total Acumulado de Requisições Bem-Sucedidas')
    plt.xlabel('Número do Grupo')
    plt.ylabel('Total Acumulado de Requisições Bem-Sucedidas')
    plt.grid(True)
    plt.show()

# Iniciar o teste de carga
asyncio.run(run_stress_test())
plot_group_durations()
plot_total_success_counts()