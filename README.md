# grafana-loki-demo

Stack completo de observabilidad de logs con **Loki + Promtail + Grafana**, levantado con Docker
Compose, con datos de ejemplo de nginx y dos dashboards ya provisionados.

Incluye una **[guía de campo](#guía)** que explica la configuración término por término y enseña
LogQL desde cero.

---

## Arrancar

```bash
git clone https://github.com/jlaguna553/grafana-loki-demo.git
cd grafana-loki-demo

# 1. Generar los logs de ejemplo (no vienen en el repo: pesan cientos de MB)
python3 generate_logs.py          # 200k líneas de access log
python3 generate_transactions.py  # 200k transacciones CON tiempo de respuesta

# 2. Preparar el volumen de Loki (corre como uid 10001, no root)
docker compose up -d loki 2>/dev/null || true
docker compose down
docker volume create grafana-loki-demo_loki-data
docker run --rm -v grafana-loki-demo_loki-data:/data alpine:3 \
  sh -c 'mkdir -p /data/chunks /data/rules /data/wal && chown -R 10001:10001 /data'

# 3. Levantar
docker compose up -d
```

Grafana queda en **http://localhost:3000** (`admin` / `admin`).

> **Importante:** los logs de ejemplo abarcan los últimos 30 días. Al abrir un dashboard,
> pon el rango de tiempo en **Last 30 days** o no verás nada.

## Qué hay dentro

| Fichero | Para qué |
|---|---|
| `docker-compose.yml` | Los tres servicios, con healthcheck en Loki |
| `loki-config.yml` | Almacenamiento, esquema, límites de ingesta y consulta |
| `promtail-config.yml` | Qué ficheros leer y cómo parsearlos |
| `generate_logs.py` | Genera `logs/access.log` — nginx common log format |
| `generate_transactions.py` | Genera `logs/transactions.log` — con `$request_time` |
| `grafana/provisioning/` | Datasource y proveedor de dashboards |
| `grafana/dashboards/` | Los dos dashboards en JSON |
| `guia/index.html` | La guía (es lo que se despliega en Vercel) |

## Dashboards

**Nginx Access Logs** — `/d/nginx-loki-demo`
Tasa de peticiones por status, bytes medios por método, p95 por endpoint, distribución,
y tres paneles de logs en crudo.

**Latencia de Transacciones** — `/d/latencia-transacciones`
Tiempo medio de respuesta por endpoint, p50/p90/p99, latencia por status, overhead de nginx
(`request_time` menos `upstream_response_time`), Apdex y transacciones lentas.

`generate_transactions.py` inyecta un **incidente**: `/checkout` degradado entre 6 y 10 veces
durante 5 horas, hacia el día 12 del rango. El script imprime las fechas exactas al terminar.
Es el sitio interesante al que llevar el rango de tiempo.

## Dos detalles que cuestan tiempo

**`entry too far behind`** — no lo arregla `reject_old_samples: false`. Ese ajuste desactiva
la validación del *distributor*; el error viene del *ingester*, que solo acepta líneas
atrasadas hasta `max_chunk_age / 2` por detrás de la línea más reciente del stream (con el
valor por defecto de 2h, eso es **una hora**). Por eso los generadores escriben los
timestamps **ordenados**.

**Cardinalidad** — `status` y `endpoint` son labels (20 streams). `request_time`, la IP y el
id de transacción **no**: serían un stream por línea. Se extraen al consultar con `| pattern`.

## Guía

La guía es un documento autocontenido con once capítulos y diez diagramas:
las tres piezas del stack, cómo levantar el proyecto, la configuración de Loki y Promtail
término por término, el modelo de labels y streams, **cómo servir varios proyectos desde
un mismo Loki**, **LogQL desde cero en ocho niveles**, el error de los timestamps, cómo
medir latencia, **cómo llevar los logs de un WAF de Cloudflare a tus dashboards**, y una
chuleta de diagnóstico.

Es un único fichero HTML sin dependencias: se abre en el navegador tal cual.

## Despliegue en Vercel

Solo se despliega la guía. El stack de Loki no puede correr en Vercel —son tres contenedores
de larga duración con almacenamiento persistente, y Vercel ejecuta estáticos y funciones
serverless efímeras.

El fuente de la guía es `src/guia.src.html`, y es un **fragmento** sin `<head>`: se
publica como Artifact y la plataforma lo envuelve. Servido tal cual, el navegador lo abre
en quirks mode y —al no haber `<meta name="viewport">`— el móvil lo compone a 980 px y
luego reduce, que es lo que hace que se vea diminuto en el teléfono.

`build-guia.py` lo envuelve en un documento completo (charset, viewport, metadatos) y
escribe **`guia/index.html`**, que es lo que sirve Vercel.

El fuente vive fuera de `guia/` a propósito: mientras el fragmento *era* `guia/index.html`,
cualquier despliegue que apuntara a esa carpeta servía la versión sin `<head>`. Ahora
`guia/index.html` solo puede ser el documento generado.

**Si editas `src/guia.src.html`, regenera antes de subir:**

```bash
python3 build-guia.py
```

## Versiones

Loki 2.9.0 · Promtail 2.9.0 · Grafana 10.0.0

Las versiones están fijadas a propósito: el formato de configuración de Loki cambia entre
versiones mayores.
