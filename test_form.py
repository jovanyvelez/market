#!/usr/bin/env python3
import urllib.request
import json
import time

# Esperar un poco para que el servidor se inicie
time.sleep(2)

url = 'http://localhost:8000/api/procesar-carrito'
data = 'lista=[{"id":1,"name":"Producto Test","price":10.99,"quantity":2}]'

try:
    req = urllib.request.Request(url, data=data.encode('utf-8'), headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as response:
        print(f'Status: {response.getcode()}')
        print('Response preview:')
        content = response.read().decode()
        print(content[:500] + '...' if len(content) > 500 else content)
except Exception as e:
    print(f'Error: {e}')