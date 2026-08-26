#!/usr/bin/env python3
"""
Genera guia/index.html a partir de src/guia.src.html.

src/guia.src.html es un FRAGMENTO: no lleva doctype ni <head>, porque se publica
como Artifact y la plataforma lo envuelve. Servido tal cual por Vercel, ese
fragmento se renderiza en quirks mode y —al no haber <meta name="viewport">—
el móvil lo compone a 980 px virtuales y luego reduce: todo se ve diminuto.

El fuente vive fuera de guia/ a propósito. Cuando el fragmento ERA guia/index.html,
cualquier despliegue que apuntara a esa carpeta servía la versión sin <head>.
Ahora guia/index.html solo puede ser el documento completo que produce este script.
"""
import pathlib
import re

SRC = pathlib.Path("src/guia.src.html")
OUT = pathlib.Path("guia/index.html")

fragment = SRC.read_text(encoding="utf-8")

m = re.search(r"<title>(.*?)</title>", fragment)
title = m.group(1) if m else "Loki de Cero a Query"

DESC = ("Guía de campo para montar un stack Grafana + Loki + Promtail desde cero: "
        "configuración explicada término por término, varios proyectos en un mismo "
        "Loki y LogQL desde cero.")

head = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{DESC}">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{DESC}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#129717;</text></svg>">
"""

before_title = fragment.split("<title>")[0]
between = fragment.split("</title>", 1)[1].split("<style>")[0]
styles = fragment.split("<style>", 1)[1].split("</style>", 1)[0]
body = fragment.split("</style>", 1)[1].lstrip()

doc = (f"<!doctype html>\n<html lang=\"es\">\n<head>\n{head}{before_title}"
       f"<title>{title}</title>\n{between}<style>\n{styles}</style>\n</head>\n"
       f"<body>\n{body}\n</body>\n</html>\n")

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(doc, encoding="utf-8")
print(f"{OUT} generado — {len(doc):,} bytes")
