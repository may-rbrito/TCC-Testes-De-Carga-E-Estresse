import requests
import concurrent.futures
import time

url = 'https://www.google.com/'

def req_get(url):
    r = requests.get(url)
    return r

# Solicitar ao usuário a quantidade de requisições que deseja
num_threads = int(input("Digite a quantidade de requisições que deseja: "))
start_time = time.time()  # Início da contagem de tempo

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    responses = list(executor.map(req_get, [url] * num_threads))

end_time = time.time()  # Fim da contagem de tempo
total_time = end_time - start_time  # Tempo total gasto

"""
for response in responses:
    if response.status_code == 200:
        print("Requisição bem sucedida!")
    else:
        print("Erro na requisição:", response.status_code)
"""       
print(f"Tempo total para {num_threads} requisições: {total_time:.2f} segundos")
