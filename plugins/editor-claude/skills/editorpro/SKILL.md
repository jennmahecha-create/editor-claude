---
name: editorpro
description: «EditorPRO» — prepara el computador de una persona sin conocimientos técnicos para editar videos con Claude. Úsala SIEMPRE que la persona escriba «EditorPRO», «/editorpro», «editor pro», «prepara mi equipo», «configura mi computador», «instala lo necesario» o «qué me falta para editar». Revisa qué tiene, explica en palabras sencillas qué falta y para qué sirve, lo instala con permiso (Mac Intel, Mac Apple Silicon o Windows), resuelve los errores típicos y crea la carpeta «Mis videos» con el Pack de marca y la plantilla de cada video.
---

# EditorPRO · Preparar mi equipo

La persona que te habla probablemente es mayor o nunca ha usado nada técnico. Reglas de trato:
- **Español sencillo, sin jerga.** Si una palabra técnica es inevitable, explícala en 5 palabras («FFmpeg: el programa que corta el video»).
- **Una cosa a la vez.** Antes de cada paso, di en una frase qué vas a hacer.
- **Nunca le pidas que escriba comandos.** Los ejecutas tú. Si algo necesita su contraseña o un clic suyo, díselo con el paso exacto («escribe tu contraseña del computador; no verás las letras, es normal»).
- **Pide permiso antes de instalar**, con la herramienta de preguntas (AskUserQuestion): qué es, para qué sirve, cuánto pesa y de dónde viene. Una sola pregunta para todo el lote, con «Instalar todo (recomendado)» como primera opción.
- **Nunca pidas ni aceptes contraseñas, tokens ni claves en el chat.**
- **Al empezar**, saluda en una línea: «¡Hola! Soy EditorPRO. Voy a dejar tu computador listo para editar videos. Tú solo respondes; yo hago el resto.»
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
# Python moderno (uv) en un entorno propio
curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
uv venv --python 3.11 ~/.local/video-venv && ln -sf ~/.local/video-venv/bin/python ~/.local/bin/python
# FFmpeg y ffprobe modernos (versión 7 u 8; los motores de efectos NO funcionan con ffprobe 4)
uv pip install --python ~/.local/video-venv/bin/python static-ffmpeg
~/.local/video-venv/bin/python -c "import static_ffmpeg.run as r; print(*r.get_or_fetch_platform_executables_else_raise())"
mkdir -p ~/.local/ffmpeg && cp ~/.local/video-venv/lib/python3.11/site-packages/static_ffmpeg/bin/darwin/{ffmpeg,ffprobe} ~/.local/ffmpeg/
ln -sf ~/.local/ffmpeg/ffmpeg ~/.local/bin/ffmpeg && ln -sf ~/.local/ffmpeg/ffprobe ~/.local/bin/ffprobe
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
winget install -e --id Git.Git
```
Git trae «Git Bash», que necesitan los motores de efectos y subtítulos de Converzzo.
Después: «cierra Claude y vuelve a abrirlo» para que los vea. Si winget no existe, pídele que instale «Instalador de aplicaciones» desde Microsoft Store.

### Herramientas opcionales (instálalas si la persona va a usar ese nivel)
- **yt-dlp y gallery-dl** (descargar referencias de YouTube, Instagram y Pinterest; Niveles 2 y 6): Mac `uv tool install yt-dlp && uv tool install gallery-dl` (o `python -m pip install --user yt-dlp gallery-dl`); Windows `winget install -e --id yt-dlp.yt-dlp` y `py -m pip install gallery-dl`.
- **Bun** (lo necesita el plugin de Telegram; Nivel 5): Mac `curl -fsSL https://bun.sh/install | bash`; Windows `powershell -c "irm bun.sh/install.ps1 | iex"`. Después: cerrar y abrir Claude.

### Al terminar
Vuelve a ejecutar el paso 1. Repite hasta que todo esté ✅. Si algo sigue fallando, mira «Errores típicos».

## Paso 3 · Crear la carpeta «Mis videos»
Pregunta (AskUserQuestion) el nombre de su marca o de su cuenta. **Dónde:** si la carpeta abierta en esta sesión se llama «Mis videos» o está vacía, créala ahí mismo sin preguntar (es lo que pide el workshop). Si no, pregunta dónde (recomienda Documentos › Mis videos). Luego:
```bash
python3 "{SKILL}/scripts/crear_carpetas.py" --dest "<Documentos>/Mis videos" --marca "<nombre>"
```
Crea: `00_PACK_DE_MARCA/` (logos, tipografias, referencias, estilos, colores.txt, diccionario.txt), `000_PLANTILLA/` (01_CLIPS_ORIGINALES … 07_SOLO_CORTES, _TRABAJO), un `CLAUDE.md` con las reglas del método y, si hay Google Drive para escritorio, `Mi unidad/EDICION/<marca>/`.

Explícale en 4 líneas qué va en cada carpeta y que **a partir de ahora abra Claude siempre en «Mis videos»**.

## Paso 3b · Biblioteca stock (buscar gastando poco)
`crear_carpetas.py` también crea `_BIBLIOTECA_STOCK/` con 3 bibliotecas: `videos/` (y `brolls/`), `imagenes/` y `sonidos/` (`musica/`, `efectos/`, `meta-sound-collection/`): en Google Drive › EDICION si existe, o dentro de Mis videos. Explícale: «aquí guardas tomas, fotos y música para reutilizar; yo busco en una lista de texto, así casi no gasto».
Cada audio o archivo de banco lleva al lado `<archivo>.licencia.txt` (Fuente, Licencia, Uso comercial, Publicidad); el índice lo lee solo y avisa de los audios sin licencia, que no se usan.
Cuando agregue archivos o diga «actualiza mi biblioteca stock» (ejecútalo en cada una de las 3):
```bash
python3 "{SKILL}/scripts/indexar_biblioteca.py" --dir "<biblioteca>"
```
Luego: videos e imágenes → mira cada hoja de `.hojas/` **una sola vez**; audios → describe por el nombre y la licencia (escucha 10 s solo si hace falta). Escribe en `indice.tsv` la descripción (1 línea) y 5 etiquetas.
**Biblioteca de sonidos de Meta:** Claude no puede descargarla (requiere la sesión de Facebook de la persona). La persona entra a facebook.com/sound/collection, descarga los audios y los pone en `sonidos/meta-sound-collection/` con su `.licencia.txt` («Fuente: Meta Sound Collection · Uso comercial: sí · Publicidad: sí · Solo Facebook e Instagram»). Para buscar después, lee solo `indice.tsv`.

## Paso 3b2 · Stock gratis (Pixabay y Pexels, cuando lo pida)
1. Crea `~/.config/editorpro/claves.env` con `PIXABAY_KEY=` y `PEXELS_KEY=` vacíos (permisos 600) y ábrelo para que la persona pegue su clave ella misma (`open -e` en Mac, `notepad` en Windows). Nunca le pidas la clave en el chat.
2. Explícale cómo sacarla: cuenta gratis en pixabay.com → pixabay.com/api/docs/ (la clave aparece con la sesión iniciada); en Pexels: pexels.com/api.
3. Prueba con `python3 "{SKILL}/scripts/stock_gratis.py" buscar --tipo video --q "manos" --n 3`.

## Paso 3c · Primer uso de los efectos Converzzo
La primera vez que use un comando de Converzzo, el plugin prepara su motor (en un Mac Intel tarda unos 3 a 4 minutos por plugin). Para que el alumno no espere en su primera edición, al final de EditorPRO ofrécele dejarlos listos: ejecuta el `preparar.sh` de cada plugin si encuentras su carpeta, o pídele que escriba `/cortar-silencios` una vez sin video. Si falla al bajar Chrome o el modelo de voz, usa el Chrome ya instalado y revisa la sección «Si algo falla» del README del plugin. Si el seguimiento de objetos (/etiqueta-sigue, /foco, /lupa, /pixelar) no se pudo instalar, avísale antes de usarlos.

## Paso 3d · Telegram en modo Terminal (Nivel 5, cuando lo pida)
La app de escritorio envía mensajes por Telegram pero NO entrega a la conversación los que la persona escribe. Para recibirlos, Claude se abre en modo canal desde la Terminal:
1. Instalar Claude Code para Terminal (pide permiso): Mac `curl -fsSL https://claude.ai/install.sh | bash`; Windows `irm https://claude.ai/install.ps1 | iex`.
2. `claude plugin marketplace add anthropics/claude-plugins-official` y `claude plugin install telegram@claude-plugins-official`.
3. Bun accesible para la app: si `bun` está en ~/.bun/bin, que la persona ejecute `sudo ln -sf ~/.bun/bin/bun /usr/local/bin/bun`.
4. Atajo `editor` en ~/.zshrc (Mac): `alias editor='cd "<carpeta de videos>" && env -u ANTHROPIC_BASE_URL -u ANTHROPIC_API_KEY caffeinate -i claude --channels plugin:telegram@claude-plugins-official'`.
5. Explícale: abrir la app **Terminal** del sistema (no la integrada en Claude), escribir `editor`, y en el primer inicio elegir **cuenta de Claude con suscripción**, nunca «API» (cobra aparte). Antes, cerrar la app de escritorio con Cmd + Q para que no compitan por el bot.
6. Prueba: escribir «hola» al bot desde el celular → debe responder.

## Paso 4 · Cierre
- Muéstrale el ✅ final con lo que quedó instalado y dónde está su carpeta.
- Dile el siguiente paso del workshop: «Ahora mete tu primer video en 000_PLANTILLA… o pídeme: crea el video 001».
- Si no tiene Google Drive para escritorio, menciónalo como opcional para el Nivel 3.

## Errores típicos
| Síntoma | Qué hacer |
|---|---|
| «Homebrew on macOS is only supported on Apple Silicon» | Es un Mac Intel: usa la ruta Mac Intel. |
| `command not found` justo después de instalar | `export PATH=...` en esta sesión; para Claude: cerrar y abrir la app. |
| `curl: (56) ... 410` al bajar FFmpeg | Ese sitio cambió: usa `static-ffmpeg` (pip). |
| `No match for section 'stream_side_data'` al editar | ffprobe demasiado viejo (versión 4). Instala el moderno con `static-ffmpeg` (ruta Mac Intel). |
| Error compilando `llvmlite` o `numba` | Fija `numba==0.60.0 llvmlite==0.43.0` (ruedas precompiladas). |
| `pip` instala en Python 3.9 del sistema | Usa el entorno `~/.local/video-venv` (Mac) o `py -3.12` (Windows). |
| «No hay espacio» | Menos de 15 GB libres: pídele que libere espacio antes de seguir. |
| El instalador pide contraseña y la persona se asusta | Explica que es la misma con la que enciende el computador y que no se verán las letras. |
| Windows: `winget` no reconocido | Instalar «Instalador de aplicaciones» desde Microsoft Store. |
| Telegram no arranca: «Executable not found: bun» | Si Bun no está, instálalo. Si ya está (en ~/.bun/bin), la app no lo ve: pide a la persona que ejecute en la Terminal `sudo ln -sf ~/.bun/bin/bun /usr/local/bin/bun` (pide su contraseña del Mac) y que cierre (Cmd + Q) y abra Claude. |
| El bot muestra «escribiendo…» pero no responde | La app de escritorio no entrega los mensajes entrantes: usar el modo Terminal (Paso 3d). |
| El bot de Telegram no responde | Solo una conversación a la vez recibe Telegram. Cerrar la app con Cmd + Q, abrirla y dejar solo la conversación de su carpeta de videos. |
| Un comando se borra por la seguridad de Claude | No lo fuerces: busca otra forma sin borrar, o pide a la persona que lo haga. |
