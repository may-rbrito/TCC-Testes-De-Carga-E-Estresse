import requests
import concurrent.futures
import time
import matplotlib.pyplot as plt

url = 'https://pt-br.facebook.com/'

def req_get(url):
    try:
        r = requests.get(url)
        return r
    except requests.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None

# Configurações para o loop de teste
max_requests = int(input("Digite a quantidade de máxima de requisições: "))
increment = int(input("Digite o incremento no número de requisições que deseja: "))
limit_time = int(input("Digite o limite de tempo em segundos que deseja: "))

# Listas para armazenar resultados
num_requests_list = []
success_count_list = []
total_time_list = []

# Iniciar loop para testar o limite de requisições
num_threads = increment
while num_threads <= max_requests:
    start_time = time.time()  # Início da contagem de tempo

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        responses = list(executor.map(req_get, [url] * num_threads))

    end_time = time.time()  # Fim da contagem de tempo
    total_time = end_time - start_time  # Tempo total gasto

    # Contar requisições bem-sucedidas
    success_count = sum(1 for response in responses if response and response.status_code == 200)

    # Armazenar resultados nas listas
    num_requests_list.append(num_threads)
    success_count_list.append(success_count)
    total_time_list.append(total_time)

    # Imprimir resultados
    print(f"{num_threads} requisições:")
    print(f" - Requisições bem sucedidas: {success_count}")
    print(f" - Tempo total: {total_time:.2f}s")

    # Verificar se o limite de tempo foi atingido
    if total_time > limit_time:
        print("Limite de tempo atingido, interrompendo o teste.")
        break

    # Incrementar o número de threads para a próxima iteração
    num_threads += increment

# Plotar os resultados
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(num_requests_list, success_count_list, marker='o', linestyle='-', color='b')
plt.xlabel('Número de Requisições')
plt.ylabel('Requisições Bem Sucedidas')
plt.title('Requisições Bem Sucedidas vs. Número de Requisições')

plt.subplot(1, 2, 2)
plt.plot(num_requests_list, total_time_list, marker='o', linestyle='-', color='r')
plt.xlabel('Número de Requisições')
plt.ylabel('Tempo Total (s)')
plt.title('Tempo Total vs. Número de Requisições')

plt.tight_layout()
plt.show()
