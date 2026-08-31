#!/usr/bin/env python3
"""
Generador de logs de ejemplo para la guía Loki de Cero a Query.

Este script genera un archivo access.log con líneas de ejemplo que puedes
usar para probar la ingesta en Loki. Útil para el quickstart.

Uso:
    python3 generate_logs.py
    python3 generate_logs.py --count 100  # genera 100 líneas
    python3 generate_logs.py --output ./logs/custom.log
"""

import random
import datetime
import argparse
from pathlib import Path

# IPs de clientes típicas
IPS = [f"192.168.1.{100+i}" for i in range(10)] + [
    "10.0.0.5", "10.0.0.15", "172.16.0.20"
]

# Endpoints de una API típica
ENDPOINTS = [
    "/", "/api/v1/login", "/api/v1/logout", "/api/v1/users",
    "/api/v1/products", "/api/v1/orders", "/checkout",
    "/checkout/confirm", "/product/widget-blue", "/search?q=loki",
    "/admin/dashboard", "/health",
]

# Métodos HTTP
METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

# Códigos HTTP con frecuencia
STATUS_CODES = [
    (200, 60), (201, 10), (204, 5), (301, 5), (302, 5),
    (400, 5), (401, 3), (403, 2), (404, 10), (500, 2),
    (502, 1), (503, 1),
]

def weighted_choice(choices):
    items, weights = zip(*choices)
    total = sum(weights)
    r = random.uniform(0, total)
    current = 0
    for item, weight in choices:
        current += weight
        if r <= current:
            return item
    return items[-1]

def generate_log_line(timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now()
    ip = random.choice(IPS)
    method = random.choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status = weighted_choice(STATUS_CODES)
    bytes_sent = random.randint(100, 50000) if status != 204 else 0
    ts_str = timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")
    return f'{ip} - - [{ts_str}] "{method} {endpoint} HTTP/1.1" {status} {bytes_sent}\n'

def main():
    parser = argparse.ArgumentParser(description="Genera logs para Loki")
    parser.add_argument("--count", "-c", type=int, default=50, help="Líneas a generar")
    parser.add_argument("--output", "-o", default="./logs/access.log", help="Archivo de salida")
    parser.add_argument("--minutes", "-m", type=int, default=1, help="Rango de tiempo")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now()
    with open(args.output, 'w') as f:
        for i in range(args.count):
            minutes_ago = (args.minutes * i) // args.count
            seconds_ago = random.randint(0, 59)
            ts = now - datetime.timedelta(minutes=minutes_ago, seconds=seconds_ago)
            line = generate_log_line(ts)
            f.write(line)

    print(f"✓ Generados {args.count} logs en {args.output}")

if __name__ == "__main__":
    main()
