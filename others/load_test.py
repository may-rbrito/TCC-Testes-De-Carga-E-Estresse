import requests
import concurrent.futures
import time
import matplotlib.pyplot as plt

url = 'https://pitrol.dev/aouerj/docentes'

def req_get(url):
    try:
        start = time.time()  # Início da contagem de tempo para uma única requisição
        r = requests.get(url)
        end = time.time()  # Fim da contagem de tempo
        duration = end - start  # Tempo gasto na requisição
        return r, duration
    except requests.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None, None

# Configurações para o teste
delay = 1  # Tempo de espera em segundos entre cada conjunto de requisições
num_requests = 500  # Número de requisições a serem feitas a cada intervalo
test_duration = 1 * 60  # Duração total do teste em segundos (1 minuto)

# Listas para armazenar os resultados
group_durations = []  # Tempo total gasto por grupo de 10 requisições
total_success_counts = []  # Contador acumulado de requisições bem-sucedidas
individual_durations = []  # Lista para armazenar o tempo gasto em cada requisição

total_success = 0  # Contador total de requisições bem-sucedidas

end_time = time.time() + test_duration

while time.time() < end_time:
    start_time = time.time()  # Início da contagem de tempo para as 10 requisições

    # Fazer 10 requisições simultâneas usando ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        results = list(executor.map(req_get, [url] * num_requests))

    # Processar os resultados
    success_count = sum(1 for response, _ in results if response and response.status_code == 200)
    total_time = time.time() - start_time  # Tempo total gasto para as 10 requisições

    # Atualizar o contador total de requisições bem-sucedidas
    total_success += success_count

    # Armazenar o tempo de cada requisição individual
    individual_durations.extend(duration for _, duration in results if duration is not None)

    # Armazenar os resultados
    group_durations.append(total_time)
    total_success_counts.append(total_success)

    print(f"{num_requests} requisições:")
    print(f" - Requisições bem sucedidas: {success_count} (Total acumulado: {total_success})")
"""
    print(f" - Tempo total para as requisições: {total_time:.2f}s")
    print(f"Tempos individuais das requisições: {individual_durations}")
"""


# Aguardar 5 segundos antes de repetir as requisições
time.sleep(delay)

# Calcular a média do tempo de todas as requisições
average_duration = sum(individual_durations) / len(individual_durations) if individual_durations else 0

# Exibir a média do tempo de requisição
print(f"Média do tempo gasto por requisição: {average_duration:.4f}s")

# Plotar os resultados após o término do teste
plt.figure(figsize=(12, 6))

# Plotar o tempo gasto por grupo de requisições
plt.subplot(1, 2, 1)
plt.plot(group_durations, marker='o')
plt.title('Tempo Total por Grupo de Requisições')
plt.xlabel('Grupo de Requisições')
plt.ylabel('Tempo (s)')

# Plotar o total acumulado de requisições bem-sucedidas
plt.subplot(1, 2, 2)
plt.plot(total_success_counts, marker='o', color='green')
plt.title('Requisições Bem-Sucedidas Acumuladas')
plt.xlabel('Grupo de Requisições')
plt.ylabel('Total Acumulado de Sucesso')

plt.tight_layout()
plt.show()
