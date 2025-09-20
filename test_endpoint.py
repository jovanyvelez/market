#!/usr/bin/env python3
import urllib.request
import json

url = 'http://localhost:8000/api/procesar-carrito'
data = json.dumps({'lista': [{'id': 1, 'name': 'Producto Test', 'price': 10.99, 'quantity': 2}]}).encode('utf-8')

try:
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print(f'Status: {response.getcode()}')
        print('Response preview:')
        content = response.read().decode()
        print(content[:500] + '...' if len(content) > 500 else content)
except Exception as e:
    print(f'Error: {e}')