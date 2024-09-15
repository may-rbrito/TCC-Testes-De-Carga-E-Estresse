import requests
import concurrent.futures
import time

url = 'https://www.google.com/'

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

# Iniciar loop para testar o limite de requisições
num_threads = increment
while num_threads <= max_requests:
    start_time = time.time()  # Início da contagem de tempo

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        responses = list(executor.map(req_get, [url] * num_threads))

    end_time = time.time()  # Fim da contagem de tempo
    total_time = end_time - start_time  # Tempo total gasto

    # Imprimir resultados
    success_count = sum(1 for response in responses if response and response.status_code == 200)
    print(f"{num_threads} requisições:")
    print(f" - Requisições bem sucedidas: {success_count}")
    print(f" - Tempo total: {total_time:.2f}s")

    # Verificar se o limite de tempo foi atingido
    if total_time > limit_time:
        print("Limite de tempo atingido, interrompendo o teste.")
        break

    # Incrementar o número de threads para a próxima iteração
    num_threads += increment
