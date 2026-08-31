#!/usr/bin/env python3
"""
Generador de logs en tiempo real para la guía Loki.

Este script genera logs continuamente, escribiendo líneas en tiempo real
al archivo access.log. Úsalo en otra terminal mientras tienes Grafana abierto
para ver los logs aparecer en vivo.

Uso:
    python3 generate_logs_realtime.py
    python3 generate_logs_realtime.py --interval 0.2  # más rápido
    python3 generate_logs_realtime.py --file ./logs/custom.log
"""

import random
import datetime
import time
import argparse
from pathlib import Path

IPS = [f"192.168.1.{100+i}" for i in range(10)] + ["10.0.0.5", "10.0.0.15"]
ENDPOINTS = [
    "/", "/api/v1/login", "/api/v1/logout", "/api/v1/users",
    "/api/v1/products", "/api/v1/orders", "/checkout",
    "/checkout/confirm", "/product/widget-blue", "/search?q=loki",
]
METHODS = ["GET", "POST", "PUT", "DELETE"]
STATUS_CODES = [200, 200, 200, 201, 400, 404, 500]

def generate_log_line():
    ip = random.choice(IPS)
    method = random.choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status = random.choice(STATUS_CODES)
    bytes_sent = random.randint(100, 50000)
    ts = datetime.datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
    return f'{ip} - - [{ts}] "{method} {endpoint} HTTP/1.1" {status} {bytes_sent}\n'

def main():
    parser = argparse.ArgumentParser(description="Genera logs en tiempo real")
    parser.add_argument("--interval", "-i", type=float, default=0.5, 
                       help="Intervalo en segundos entre logs (default: 0.5)")
    parser.add_argument("--file", "-f", default="./logs/access.log",
                       help="Archivo de salida (default: ./logs/access.log)")
    args = parser.parse_args()

    output_path = Path(args.file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📝 Generando logs en {args.file} (intervalo: {args.interval}s)")
    print("   Presiona Ctrl+C para detener\n")

    try:
        with open(args.file, 'a') as f:
            count = 0
            while True:
                line = generate_log_line()
                f.write(line)
                f.flush()
                count += 1
                print(f"   [{count}] {line.strip()}")
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\n✓ Detenido. Total: {count} líneas generadas")

if __name__ == "__main__":
    main()
