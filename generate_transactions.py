"""
Genera logs nginx con TIEMPO DE RESPUESTA ($request_time / $upstream_response_time).

El access.log original usa el "common log format", que no incluye ningun campo
temporal por peticion. Para medir latencia nginx necesita un log_format como:

  log_format timed '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" "$http_user_agent" '
                   '$request_time $upstream_response_time $request_id';

Este script emite exactamente ese formato.
"""
import math
import os
import random
from datetime import datetime, timedelta

TOTAL_LINES = 200_000
DAYS_BACK = 30
OUT = "./logs/transactions.log"

METHODS = ["GET", "POST", "PUT", "DELETE"]
AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "curl/8.4.0",
    "PostmanRuntime/7.36.0",
]

# Latencia MEDIANA por endpoint, en segundos. /checkout es el lento
# (pasarela de pago), /api/v1/users el rapido (lectura cacheada).
BASE_LATENCY = {
    "/api/v1/users": 0.045,
    "/products":     0.080,
    "/login":        0.120,
    "/dashboard":    0.230,
    "/checkout":     0.650,
}
ENDPOINTS = list(BASE_LATENCY)

print(f"Generando {TOTAL_LINES:,} transacciones ORDENADAS con request_time...")

end_date = datetime.now()
start_date = end_date - timedelta(days=DAYS_BACK)
range_s = int((end_date - start_date).total_seconds())

# Ventana de incidente: 5 horas hacia el dia 12, /checkout degradado x8.
# Sirve para tener algo real que investigar en Grafana en vez de una linea plana.
incident_start = start_date + timedelta(days=12)
incident_end = incident_start + timedelta(hours=5)

# Ordenados: si el archivo va barajado, Loki rechaza con "entry too far behind".
offsets = sorted(random.randint(0, range_s) for _ in range(TOTAL_LINES))

os.makedirs("./logs", exist_ok=True)
with open(OUT, "w") as f:
    for offset in offsets:
        ts = start_date + timedelta(seconds=offset)
        endpoint = random.choice(ENDPOINTS)
        method = random.choice(METHODS)

        # Los 500 suelen ser timeouts (lentos); los 404 ni tocan el backend.
        roll = random.random()
        if roll < 0.030:
            status = 500
        elif roll < 0.065:
            status = 404
        elif roll < 0.090:
            status = 301
        else:
            status = 200

        # Log-normal: cola larga a la derecha, como la latencia real.
        rt = random.lognormvariate(math.log(BASE_LATENCY[endpoint]), 0.55)

        if status == 500:
            rt *= random.uniform(3.0, 12.0)
        elif status == 404:
            rt *= 0.15
        elif status == 301:
            rt *= 0.30

        if endpoint == "/checkout" and incident_start <= ts < incident_end:
            rt *= random.uniform(6.0, 10.0)

        rt = min(rt, 30.0)
        # upstream siempre algo menor que request_time (el resto es red/nginx)
        urt = rt * random.uniform(0.82, 0.98)

        ip = f"192.168.1.{random.randint(1, 255)}"
        bytes_sent = random.randint(200, 5000)
        referer = random.choice(["-", "https://demo.local/", "https://demo.local/products"])
        agent = random.choice(AGENTS)
        txn = f"txn_{random.getrandbits(48):012x}"

        f.write(
            f'{ip} - - [{ts.strftime("%d/%b/%Y:%H:%M:%S +0000")}] '
            f'"{method} {endpoint} HTTP/1.1" {status} {bytes_sent} '
            f'"{referer}" "{agent}" {rt:.3f} {urt:.3f} {txn}\n'
        )

print(f"Listo: {OUT}")
print(f"Incidente inyectado en /checkout: {incident_start:%Y-%m-%d %H:%M} -> {incident_end:%H:%M}")
