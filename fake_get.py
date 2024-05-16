from time import sleep
import time
import requests

url = "http://127.0.0.1:8000/simulator_home"

delay = 0.1
check_every = 20
buffer_status_sum = 0
counter = 0

while True:
    counter += 1
    response = requests.get(url)

    buffer_status_sum += response.status_code

    if counter % check_every == 0:
        curr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if buffer_status_sum == check_every * 200:
            print(f"{curr_time:20s} | Cumulative status code: {response.status_code}")
        else:
            print(f"{curr_time:20s} | Cumulative status code: {response.status_code} | ERROR")
        buffer_status_sum = 0
    
    sleep(delay)
