#!/usr/bin/env python3
"""Crea la carpeta «Mis videos» del método: Pack de marca, plantilla de video y reglas.
Nunca borra ni sobrescribe: si algo ya existe, lo deja como está."""
import argparse, glob, os

SUB = ["01_CLIPS_ORIGINALES", "02_REEL_REFERENCIA", "03_REEL_EDITADO_FINAL", "04_PORTADA",
       "05_MATERIAL_ADICIONAL", "06_BROLLS", "07_SOLO_CORTES", "_TRABAJO"]

REGLAS = """# Mis videos · {marca}

Reglas para Claude cuando edite en esta carpeta (mandan sobre las de cualquier skill):
- `00_PACK_DE_MARCA/` es el estilo de la marca: logos/, tipografias/, referencias/, colores.txt, diccionario.txt y Reglas-de-estilo.md (si existe, úsalo siempre).
- Cada video es una carpeta `NNN_TEMA/` (001, 002…). Si no existe, copia `000_PLANTILLA/` con el siguiente número.
- **Video nuevo, sin complicaciones:** si la persona deja un video suelto en esta carpeta (o dice dónde está: Escritorio, Descargas…) y pide editarlo, crea tú la siguiente carpeta `NNN_TEMA/` desde la plantilla (el tema, en mayúsculas, sale de lo que dice el video o de lo que ella diga) y **mueve** el video a `01_CLIPS_ORIGINALES/`. Dile en una línea dónde quedó.
  - 01_CLIPS_ORIGINALES: lo grabado (nunca se modifica)
  - 02_REEL_REFERENCIA: videos de referencia + que-copiar.txt → copia SOLO eso
  - 03_REEL_EDITADO_FINAL: el video terminado
  - 04_PORTADA: la portada
  - 05_MATERIAL_ADICIONAL: lo que la persona quiere dentro del video
  - 06_BROLLS: escenas de 3-8 s reutilizables, sacadas de los originales, con indice.txt
  - 07_SOLO_CORTES: versión solo con cortes, sin subtítulos, gráficos ni música
  - _TRABAJO: intermedios; se puede borrar tras publicar
- `00_PACK_DE_MARCA/estilos/<nombre>/` guarda fichas de estilo reutilizables: `referencias/` (3 videos parecidos) y `ficha.md`. Para crear una, descarga los videos, analízalos y escribe con valores medibles el ritmo, la animación de los textos, las tipografías, las posiciones, los colores, los zooms, las transiciones, el sonido y la estructura; copia la forma, nunca el contenido. Para usarla («edita el 003 con el estilo X»), toma de la ficha el movimiento y el ritmo, y del Pack de marca los colores, el logo y las letras.
- Usa las palabras de diccionario.txt al hacer subtítulos.
- Antes de entregar, haz siempre la revisión de calidad: palabras cortadas, ortografía, zona segura, cara libre, volumen (−14 LUFS), inicio y final limpios, CTA legible. Corrige lo que falle y di en una línea qué revisaste.
- Si existe Google Drive para escritorio, copia 06_BROLLS y 07_SOLO_CORTES a «Mi unidad/EDICION/{marca}/NNN_TEMA/».
- Antes del video final, muestra 2 fotos de cómo va a quedar y espera un «dale». No inventes precios, cifras ni nombres: si faltan, pregunta. Si pide varios efectos en un mensaje, hazlos en un solo render.
- Datos sensibles: antes de entregar un video con pantalla, busca correos, teléfonos, direcciones, nombres de clientes, documentos, códigos y contraseñas; muéstralos con su segundo, espera el «dale» y difumínalos.
- No repitas preguntas: guarda en 00_PACK_DE_MARCA/respuestas.md lo que la persona conteste (calidad, estilo, música, red…) y úsalo la próxima vez sin preguntar. Pregunta solo lo imprescindible. Si la conversación viene de Telegram, pregunta por Telegram con opciones numeradas.
- Texto detrás de la cabeza: solo cuando la persona lo pida para una ocasión especial (tarda mucho).
- Biblioteca stock: 3 bibliotecas (videos, imagenes, sonidos), cada una con su `indice.tsv`. Para buscar, lee primero el índice correcto (texto); no abras videos ni escuches audios para buscar. Usa audios e imágenes de bancos solo si su fila dice uso_comercial: sí (y publicidad: sí si se va a pautar). meta-sound-collection solo para Facebook e Instagram. Si hay archivos nuevos, ejecuta `indexar_biblioteca.py --dir <carpeta>` de la skill EditorPRO, mira cada hoja de `.hojas/` una sola vez y escribe descripción y etiquetas en el índice. Canva es para diseñar, no para buscar videos.
- Música sin problemas: nunca canciones comerciales ni música descargada de redes. Solo música generada, o de _BIBLIOTECA_STOCK/sonidos con su archivo .licencia.txt (uso comercial y publicidad: sí), o sin música. Entrega siempre dos versiones: con música segura y «(sin musica)», para poner un audio en tendencia dentro de la red.
- Habla en español sencillo, sin jerga, y pide permiso antes de instalar algo o de crear o exportar en Canva.
"""


def nuevo(path, texto):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(texto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True)
    ap.add_argument("--marca", required=True)
    a = ap.parse_args()
    d = os.path.abspath(os.path.expanduser(a.dest))
    pack = os.path.join(d, "00_PACK_DE_MARCA")
    for s in ("logos", "tipografias", "referencias", "estilos"):
        os.makedirs(os.path.join(pack, s), exist_ok=True)
    nuevo(os.path.join(pack, "colores.txt"),
          "Colores de %s (código, ej. #1E3A8A)\nPrincipal: \nSecundario: \nAcento: \nKit de marca en Canva (sí/no): \n" % a.marca)
    nuevo(os.path.join(pack, "diccionario.txt"),
          "Palabras que deben escribirse así en los subtítulos (una por línea):\n%s\n" % a.marca)
    plant = os.path.join(d, "000_PLANTILLA")
    for s in SUB:
        os.makedirs(os.path.join(plant, s), exist_ok=True)
    nuevo(os.path.join(plant, "02_REEL_REFERENCIA", "que-copiar.txt"),
          "Qué copiar de este video de referencia (ej. solo la animación de las letras):\n\n")
    nuevo(os.path.join(d, "CLAUDE.md"), REGLAS.format(marca=a.marca))
    print("Carpeta lista: " + d)
    g = glob.glob(os.path.expanduser("~/Library/CloudStorage/GoogleDrive-*/Mi unidad")) + \
        glob.glob(os.path.expanduser("~/Library/CloudStorage/GoogleDrive-*/My Drive"))
    if g:
        e = os.path.join(g[0], "EDICION", a.marca)
        os.makedirs(e, exist_ok=True)
        print("Google Drive listo: " + e)
        b = os.path.join(g[0], "EDICION", "_BIBLIOTECA_STOCK")
        for s2 in ("videos/brolls", "imagenes", "sonidos/musica", "sonidos/efectos", "sonidos/meta-sound-collection"):
            os.makedirs(os.path.join(b, s2), exist_ok=True)
        print("Biblioteca stock: " + b)
    else:
        b = os.path.join(d, "_BIBLIOTECA_STOCK")
        for s2 in ("videos/brolls", "imagenes", "sonidos/musica", "sonidos/efectos", "sonidos/meta-sound-collection"):
            os.makedirs(os.path.join(b, s2), exist_ok=True)
        print("Google Drive para escritorio no encontrado (opcional). Biblioteca stock local: " + b)


if __name__ == "__main__":
    main()
