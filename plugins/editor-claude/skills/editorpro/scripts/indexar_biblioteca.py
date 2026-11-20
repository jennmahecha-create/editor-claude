#!/usr/bin/env python3
"""Indexa una biblioteca de videos e imágenes (stock y B-rolls) para buscar en texto, sin gastar.

Uso:  python3 indexar_biblioteca.py --dir "<carpeta>"            # agrega solo lo nuevo
      python3 indexar_biblioteca.py --dir "<carpeta>" --pendientes  # lista lo que falta describir

Crea en la carpeta:
  indice.tsv          una línea por archivo: archivo, tipo, duración, ancho x alto, orientación, fecha, descripción, etiquetas
  .hojas/<archivo>.jpg una hoja con 6 fotogramas (para que Claude la mire UNA sola vez y escriba la descripción)
Nunca borra ni mueve nada. Solo necesita ffmpeg y ffprobe."""
import argparse, csv, json, os, shutil, subprocess, sys, time

VIDEO = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi"}
IMAGEN = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
AUDIO = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
CAMPOS = ["archivo", "tipo", "duracion_s", "resolucion", "orientacion", "fecha", "descripcion", "etiquetas", "fuente", "licencia", "uso_comercial", "publicidad"]


def herramienta(n):
    p = shutil.which(n) or os.path.expanduser("~/.local/bin/" + n)
    if not os.path.exists(p):
        sys.exit("Falta %s. Escribe EditorPRO para instalarlo." % n)
    return p


def probe(ffprobe, f):
    r = subprocess.run([ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", f],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return 0.0, 0, 0
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    w, h = int(v.get("width") or 0), int(v.get("height") or 0)
    rot = str((v.get("tags") or {}).get("rotate", "")) + str(v.get("side_data_list", ""))
    if "90" in rot:
        w, h = h, w
    return float(d.get("format", {}).get("duration") or 0), w, h


def hoja(ffmpeg, f, dur, salida):
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    if dur <= 0:
        cmd = [ffmpeg, "-v", "error", "-y", "-i", f, "-vf", "scale=480:-2", "-frames:v", "1", salida]
    else:
        fps = 6.0 / max(dur, 0.5)
        cmd = [ffmpeg, "-v", "error", "-y", "-i", f, "-vf",
               "fps=%.4f,scale=320:-2,tile=3x2:padding=4" % fps, "-frames:v", "1", salida]
    subprocess.run(cmd, capture_output=True)


def licencia(ruta):
    """Lee <archivo>.licencia.txt si existe (Fuente:, Licencia:, Uso comercial:, Publicidad:)."""
    d = {"fuente": "", "licencia": "", "uso_comercial": "", "publicidad": ""}
    for cand in (ruta + ".licencia.txt", os.path.splitext(ruta)[0] + ".licencia.txt"):
        if os.path.exists(cand):
            for l in open(cand, encoding="utf-8", errors="ignore"):
                k, _, v = l.partition(":")
                k = k.strip().lower()
                v = v.strip()
                if k.startswith("fuente"): d["fuente"] = v
                elif k.startswith("licencia"): d["licencia"] = v
                elif k.startswith("uso comercial"): d["uso_comercial"] = v
                elif k.startswith("publicidad"): d["publicidad"] = v
            break
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--pendientes", action="store_true")
    a = ap.parse_args()
    base = os.path.abspath(os.path.expanduser(a.dir))
    os.makedirs(base, exist_ok=True)
    idx = os.path.join(base, "indice.tsv")
    filas = {}
    if os.path.exists(idx):
        with open(idx, encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                filas[r["archivo"]] = r
    if a.pendientes:
        falta = [k for k, r in filas.items() if not r.get("descripcion")]
        print("\n".join(falta) if falta else "Todo descrito.")
        return
    ffmpeg, ffprobe = herramienta("ffmpeg"), herramienta("ffprobe")
    nuevos = 0
    for raiz, dirs, archivos in os.walk(base):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for n in sorted(archivos):
            ext = os.path.splitext(n)[1].lower()
            if ext not in VIDEO | IMAGEN | AUDIO:
                continue
            ruta = os.path.join(raiz, n)
            rel = os.path.relpath(ruta, base)
            if rel in filas:
                filas[rel].update({k: v for k, v in licencia(ruta).items() if v})
                continue
            if ext in AUDIO:
                dur = probe(ffprobe, ruta)[0]; w = h = 0; ori = "-"
                tipo = "audio"
            else:
                dur, w, h = probe(ffprobe, ruta) if ext in VIDEO else (0.0, *probe(ffprobe, ruta)[1:])
                ori = "vertical" if h > w else ("horizontal" if w > h else "cuadrado")
                hoja(ffmpeg, ruta, dur if ext in VIDEO else 0, os.path.join(base, ".hojas", rel + ".jpg"))
                tipo = "video" if ext in VIDEO else "imagen"
            filas[rel] = {"archivo": rel, "tipo": tipo,
                          "duracion_s": "%.1f" % dur, "resolucion": "%dx%d" % (w, h), "orientacion": ori,
                          "fecha": time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(ruta))),
                          "descripcion": "", "etiquetas": "", **licencia(ruta)}
            nuevos += 1
    with open(idx, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS, delimiter="\t")
        w.writeheader()
        for k in sorted(filas):
            w.writerow({c: filas[k].get(c, "") for c in CAMPOS})
    falta = sum(1 for r in filas.values() if not r.get("descripcion"))
    print("Índice: %s · %d archivos · %d nuevos · %d sin describir" % (idx, len(filas), nuevos, falta))
    if falta:
        print("Siguiente: videos e imágenes → mira cada hoja de .hojas/ UNA vez; audios → describe por nombre, licencia y, si hace falta, escuchando solo 10 s. Escribe descripcion y etiquetas en indice.tsv.")
    sin_lic = [r["archivo"] for r in filas.values() if r.get("tipo") == "audio" and not r.get("licencia")]
    if sin_lic:
        print("⚠️ Audios SIN licencia (no se usan hasta tener su .licencia.txt): " + ", ".join(sin_lic))


if __name__ == "__main__":
    main()
