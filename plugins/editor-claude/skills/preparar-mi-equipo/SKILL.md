---
name: preparar-mi-equipo
description: Prepara el computador de una persona sin conocimientos técnicos para editar videos con Claude. Revisa qué tiene, explica en palabras sencillas qué falta y para qué sirve, lo instala con permiso (en Mac Intel, Mac Apple Silicon o Windows), resuelve los errores típicos y crea la carpeta «Mis videos» con el Pack de marca y la plantilla de cada video. Úsala cuando la persona diga «prepara mi equipo», «configura mi computador», «instala lo necesario», «qué me falta para editar», o al empezar el workshop de edición con Claude.
---

# Preparar mi equipo

La persona que te habla probablemente es mayor o nunca ha usado nada técnico. Reglas de trato:
- **Español sencillo, sin jerga.** Si una palabra técnica es inevitable, explícala en 5 palabras («FFmpeg: el programa que corta el video»).
- **Una cosa a la vez.** Antes de cada paso, di en una frase qué vas a hacer.
- **Nunca le pidas que escriba comandos.** Los ejecutas tú. Si algo necesita su contraseña o un clic suyo, díselo con el paso exacto («escribe tu contraseña del computador; no verás las letras, es normal»).
- **Pide permiso antes de instalar**, con la herramienta de preguntas (AskUserQuestion): qué es, para qué sirve, cuánto pesa y de dónde viene. Una sola pregunta para todo el lote, con «Instalar todo (recomendado)» como primera opción.
- **Nunca pidas ni aceptes contraseñas, tokens ni claves en el chat.**
- **Celebra al final**: «✅ Tu equipo está listo. Ya puedes editar tu primer video».

`{SKILL}` es la carpeta de esta skill (la que contiene este archivo).

## Paso 1 · Revisar el equipo
```bash
python3 "{SKILL}/scripts/revisar_equipo.py"     # Mac
py "{SKILL}\scripts\revisar_equipo.py"          # Windows (o python)
```
Si no hay Python en Windows, instálalo primero con `winget install -e --id Python.Python.3.12` (pide permiso) y abre una sesión nueva.

El script imprime una tabla y, al final, una línea `JSON:` con el detalle. Léela y explícale el resultado así:

| Componente | Para qué sirve (dilo así) |
|---|---|
| FFmpeg | «corta, une y exporta el video» |
| Node.js 20+ | «hace los gráficos animados y la música» |
| Python 3.10+ | «transcribe tu voz y hace los subtítulos» |
| Chrome | «dibuja los gráficos del video» |
| Espacio libre | «cada video ocupa varios GB mientras se edita» |
| Google Drive para escritorio (opcional) | «guarda tus B-rolls y tus videos en la nube» |

Si todo está ✅, salta al paso 3.

## Paso 2 · Instalar lo que falta (con permiso)

Elige la ruta según `sistema` del JSON. Instala todo lo que falte en un solo bloque y en segundo plano si tarda (avisa: «esto tarda entre 5 y 20 minutos; puedes ir por un café»).

### Mac con Apple Silicon (`mac-arm`)
Si no hay Homebrew, NO lo instales tú: pide su contraseña. Ábrele la Terminal con el instalador y dile que escriba su contraseña ahí:
`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
Luego: `brew install ffmpeg node python@3.12`.
Si prefiere no usar contraseña, usa la ruta «sin contraseña» de abajo, que también funciona en Apple Silicon (cambia `x64` por `arm64`).

### Mac con Intel (`mac-intel`) — Homebrew ya no funciona aquí
Instala todo en la carpeta del usuario, sin contraseña:
```bash
mkdir -p ~/.local/bin ~/.local/node
# Node (LTS oficial)
V=$(curl -fsSL https://nodejs.org/dist/index.json | python3 -c "import json,sys;print([r['version'] for r in json.load(sys.stdin) if r['lts']][0])")
curl -fsSL https://nodejs.org/dist/$V/node-$V-darwin-x64.tar.gz | tar -xz -C ~/.local/node --strip-components=1
export PATH="$HOME/.local/node/bin:$HOME/.local/bin:$PATH"
# FFmpeg y ffprobe (binarios estáticos vía npm)
npm i --prefix ~/.local/ffm ffmpeg-static ffprobe-static
ln -sf ~/.local/ffm/node_modules/ffmpeg-static/ffmpeg ~/.local/bin/ffmpeg
ln -sf ~/.local/ffm/node_modules/ffprobe-static/bin/darwin/x64/ffprobe ~/.local/bin/ffprobe
# Python moderno (uv) en un entorno propio
curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
uv venv --python 3.11 ~/.local/video-venv && ln -sf ~/.local/video-venv/bin/python ~/.local/bin/python
# Dejar el PATH para siempre
grep -q '.local/node/bin' ~/.zshrc 2>/dev/null || echo 'export PATH="$HOME/.local/node/bin:$HOME/.local/bin:$PATH"' >> ~/.zshrc
```
Notas de Mac Intel: PyTorch para Intel solo llega hasta 2.2.2 → si una skill de edición pide torch, instala `"torch==2.2.2" "numpy<2" "numba==0.60.0" "llvmlite==0.43.0"` con `uv pip install --python ~/.local/video-venv/bin/python`.

### Windows (`windows`)
```powershell
winget install -e --id Gyan.FFmpeg
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Python.Python.3.12
winget install -e --id Google.Chrome
```
Después: «cierra Claude y vuelve a abrirlo» para que los vea. Si winget no existe, pídele que instale «Instalador de aplicaciones» desde Microsoft Store.

### Al terminar
Vuelve a ejecutar el paso 1. Repite hasta que todo esté ✅. Si algo sigue fallando, mira «Errores típicos».

## Paso 3 · Crear la carpeta «Mis videos»
Pregunta (AskUserQuestion) el nombre de su marca o de su cuenta. **Dónde:** si la carpeta abierta en esta sesión se llama «Mis videos» o está vacía, créala ahí mismo sin preguntar (es lo que pide el workshop). Si no, pregunta dónde (recomienda Documentos › Mis videos). Luego:
```bash
python3 "{SKILL}/scripts/crear_carpetas.py" --dest "<Documentos>/Mis videos" --marca "<nombre>"
```
Crea: `00_PACK_DE_MARCA/` (logos, tipografias, referencias, estilos, colores.txt, diccionario.txt), `000_PLANTILLA/` (01_CLIPS_ORIGINALES … 07_SOLO_CORTES, _TRABAJO), un `CLAUDE.md` con las reglas del método y, si hay Google Drive para escritorio, `Mi unidad/EDICION/<marca>/`.

Explícale en 4 líneas qué va en cada carpeta y que **a partir de ahora abra Claude siempre en «Mis videos»**.

## Paso 4 · Cierre
- Muéstrale el ✅ final con lo que quedó instalado y dónde está su carpeta.
- Dile el siguiente paso del workshop: «Ahora mete tu primer video en 000_PLANTILLA… o pídeme: crea el video 001».
- Si no tiene Google Drive para escritorio, menciónalo como opcional para el Nivel 3.

## Errores típicos
| Síntoma | Qué hacer |
|---|---|
| «Homebrew on macOS is only supported on Apple Silicon» | Es un Mac Intel: usa la ruta Mac Intel. |
| `command not found` justo después de instalar | `export PATH=...` en esta sesión; para Claude: cerrar y abrir la app. |
| `curl: (56) ... 410` al bajar FFmpeg | Ese sitio cambió: usa la ruta de npm (`ffmpeg-static`). |
| Error compilando `llvmlite` o `numba` | Fija `numba==0.60.0 llvmlite==0.43.0` (ruedas precompiladas). |
| `pip` instala en Python 3.9 del sistema | Usa el entorno `~/.local/video-venv` (Mac) o `py -3.12` (Windows). |
| «No hay espacio» | Menos de 15 GB libres: pídele que libere espacio antes de seguir. |
| El instalador pide contraseña y la persona se asusta | Explica que es la misma con la que enciende el computador y que no se verán las letras. |
| Windows: `winget` no reconocido | Instalar «Instalador de aplicaciones» desde Microsoft Store. |
| Un comando se borra por la seguridad de Claude | No lo fuerces: busca otra forma sin borrar, o pide a la persona que lo haga. |
