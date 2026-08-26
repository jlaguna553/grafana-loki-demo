import os
import random
from datetime import datetime, timedelta

methods = ["GET", "POST", "PUT", "DELETE"]
statuses = [200, 200, 200, 200, 404, 500, 301]
endpoints = ["/api/v1/users", "/login", "/dashboard", "/checkout", "/products"]

# Ajusta el volumen aqui. 200k lineas ya dan una demo rica y se ingieren
# en segundos; 5M tardan bastante y no aportan nada a la demo.
TOTAL_LINES = 200_000
DAYS_BACK = 30
OUT = "./logs/access.log"

print(f"Generando {TOTAL_LINES:,} logs ORDENADOS cronologicamente...")

end_date = datetime.now()
start_date = end_date - timedelta(days=DAYS_BACK)
date_range_seconds = int((end_date - start_date).total_seconds())

# CLAVE: los timestamps se ordenan antes de escribir.
# Promtail envia en orden de archivo; si el archivo esta barajado, el stream
# de Loki avanza a "ahora" en las primeras lineas y luego rechaza todo lo
# viejo con "entry too far behind".
offsets = sorted(random.randint(0, date_range_seconds) for _ in range(TOTAL_LINES))

os.makedirs("./logs", exist_ok=True)
with open(OUT, "w") as f:  # 'w', no 'a': no acumular entre corridas
    for offset in offsets:
        ip = f"192.168.1.{random.randint(1, 255)}"
        method = random.choice(methods)
        endpoint = random.choice(endpoints)
        status = random.choice(statuses)
        bytes_sent = random.randint(200, 5000)

        log_date = start_date + timedelta(seconds=offset)
        log_date_text = log_date.strftime("%d/%b/%Y:%H:%M:%S +0000")
        f.write(
            f'{ip} - - [{log_date_text}] "{method} {endpoint} HTTP/1.1" '
            f'{status} {bytes_sent}\n'
        )

print(f"Listo: {OUT}")
