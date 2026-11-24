# Análisis rápido — content-analytics-dashboard (24-nov-2026)

Diagnóstico, sin cambios al código. Repo público de portafolio (datos 100 % sintéticos).

## 1. Salud técnica (verificado)

- `pip install -r requirements.txt` y `pytest -q`: **19 pasan** (5 s, sin red).
- `python main.py` con semilla 42 y fechas por omisión: las cifras del README **siguen coincidiendo**:
  Año 1 629,562,607 · Año 2 951,242,545 (+51.1 %) · Año 3 1,271,699,339 (+33.7 %, +102 % vs. Año 1).
  Horarios 18:00 y 21:00 al frente; género más eficiente Reality ($0.0413 por vista de episodio).
- Se generan las 6 gráficas sin error. CI definido para Python 3.11 y 3.12.

## 2. Revisión con Nemotron

No se obtuvo. `opencode_status` responde en línea, pero `opencode_run` falla con
`Unrecognized flag: --dir in command opencode run`: el envoltorio MCP pasa un flag que el CLI
instalado no acepta (el mismo fallo quedó registrado hoy en Qdrant para otro repo). Es un arreglo del
conector, no de este proyecto. **Qué acertó Nemotron: nada que evaluar.** La revisión de abajo es mía.

## 3. Hallazgos propios

Sin errores de lógica. Lo que sí vale la pena corregir, de mayor a menor:

1. **README sin imágenes.** Es un tablero y el README no muestra ninguna gráfica; `output/` está
   ignorado y no hay capturas. Es la mayor pérdida como pieza de portafolio.
2. **Dos escalas incompatibles.** `generate_platform_metrics` produce 25–50 mil espectadores
   mensuales; `generate_daily_ratings` produce 8 mil–220 mil *por horario × género y por día*. Las
   gráficas 01–04 y la 06 no se pueden leer juntas.
3. **"Total audience" suma horarios y géneros** (49 filas por día): son vistas-franja, no alcance
   único. El README advierte esto para el costo pero no para la audiencia (falta una línea en
   "Limitations").
4. **Meses parciales:** con fechas que no empiezan el día 1 o no terminan fin de mes, `monthly_trend`
   mezcla meses incompletos y la tendencia mensual parece caer.
5. Menores: el pastel de 7 géneros casi iguales (por diseño son ruido), sin insignia de CI en el
   README, `analyzer.py` sin type hints.

## 4. ¿Agrupar los 5 repos en una organización?

Opinión: **todavía no una organización; sí una página índice.** Con 5 repos y un solo autor, la
organización añade administración y cambia las URL (GitHub redirige, pero los README enlazan a
`github.com/Neckr0ik`). Más barato y casi igual de efectivo: README de perfil en `Neckr0ik/Neckr0ik`
con una tabla de 5 filas (qué problema, captura, enlace), repos fijados y un tema común
(`hybrid-intelligence`). Pasar a organización cuando haya un segundo colaborador o una marca
comercial. Riesgo calculado, bajo: el README dice "Inspirado en trabajo de analítica de audiencia en
una televisora mexicana"; mientras no cite datos, cifras ni nombre, es defendible, pero conviene
revisarlo contra cualquier cláusula de confidencialidad antes de promocionar el portafolio.

## 5. Conectores (sin activar)

- **Vercel (recomendado):** galería estática con las 6 PNG y el resumen de consola, desplegada desde
  una carpeta aparte (no se compromete `output/`). Plan gratuito; es el "demo en vivo" más barato.
  Replit solo si se quiere ejecutar el CLI con parámetros en línea, pero no conviene pagar Vercel y
  Replit a la vez.
- **Canva:** imagen de portada 1280×640 para la vista previa social de GitHub, con la gráfica 01 y
  el título.

## 6. Próximos pasos (orden sugerido)

1. Añadir 2–3 PNG a `docs/img/` y mostrarlas en el README (decisión de Giovanni: es la excepción a
   "no comprometer salidas").
2. Línea en "Limitations" sobre vistas-franja y sobre la escala de plataformas.
3. README de perfil con tabla de los 5 repos.
4. Arreglar `--dir` en el conector OpenCode y repetir la revisión con Nemotron.
