#!/usr/bin/env python3
"""
Genera public/index.html a partir de guia/index.html.

guia/index.html es un FRAGMENTO: no lleva doctype ni <head>, porque se publica
como Artifact y la plataforma lo envuelve. Servido tal cual por Vercel, ese
fragmento se renderiza en quirks mode y —al no haber <meta name="viewport">—
el móvil lo compone a 980 px virtuales y luego reduce, que es lo que hace que
se vea diminuto. Este script lo envuelve en un documento completo.
"""
import pathlib
import re

SRC = pathlib.Path("guia/index.html")
OUT = pathlib.Path("public/index.html")

fragment = SRC.read_text(encoding="utf-8")

title_match = re.search(r"<title>(.*?)</title>", fragment)
title = title_match.group(1) if title_match else "Loki de Cero a Query"

DESC = ("Guía de campo para montar un stack Grafana + Loki + Promtail desde cero: "
        "configuración explicada término por término, varios proyectos en un mismo "
        "Loki y LogQL desde cero.")

head_extra = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{DESC}">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{DESC}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#129717;</text></svg>">
"""

doc = f"""<!doctype html>
<html lang="es">
<head>
{head_extra}{fragment.split("</style>")[0].split("<title>")[0]}<title>{title}</title>
{fragment.split("<title>")[1].split("</title>")[1].split("<style>")[0]}<style>
{fragment.split("<style>")[1].split("</style>")[0]}</style>
</head>
<body>
{fragment.split("</style>", 1)[1].lstrip()}
</body>
</html>
"""

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(doc, encoding="utf-8")
print(f"{OUT} generado — {len(doc):,} bytes")
