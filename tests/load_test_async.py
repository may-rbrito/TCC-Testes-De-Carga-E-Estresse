import time
import httpx
import asyncio
import matplotlib.pyplot as plt


url = 'https://pitrol.dev/aouerj/reportError'

# Configurações para o teste
delay_in_seconds = 1  # Tempo de espera em segundos entre cada conjunto de requisições
num_requests = 100  # Número de requisições a serem feitas a cada intervalo
qtty_of_groups = 30

# Listas para armazenar os resultados
group_durations = []  # Tempo total gasto por grupo de 100 requisições
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
    

async def do_load_test():
    async with httpx.AsyncClient() as client:
        tasks = [req_get_async(client) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

async def run_load_test():
    global total_success

    for _ in range(qtty_of_groups):
        start_time = time.time()
       #print(f"Realizando {num_requests} requisições...")

        # Executar o teste de carga assíncrono
        results = await do_load_test()

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

        #print(f"Requisições realizadas em {total_time:.2f} segundos")
        
        if delay_in_seconds: await asyncio.sleep(delay_in_seconds)  # Esperar antes do próximo grupo


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
asyncio.run(run_load_test())
plot_group_durations()
plot_total_success_counts()