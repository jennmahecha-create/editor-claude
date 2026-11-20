#!/usr/bin/env python3
"""Busca y descarga videos, fotos y música gratis (Pixabay y Pexels) a la biblioteca stock, con su licencia.

Claves (gratis): en ~/.config/editorpro/claves.env
    PIXABAY_KEY=...
    PEXELS_KEY=...
Uso:
  stock_gratis.py buscar  --tipo video|foto --q "manos escribiendo celular" [--orientacion vertical|horizontal] [--n 8]
  stock_gratis.py bajar   --fuente pixabay|pexels --tipo video|foto --id 12345 --dest "<biblioteca>/videos" [--nombre manos_celular]
Después de bajar, ejecuta indexar_biblioteca.py en esa biblioteca."""
import argparse, json, os, re, sys, urllib.parse, urllib.request

CLAVES = os.path.expanduser("~/.config/editorpro/claves.env")
UA = {"User-Agent": "MiEditorPRO/1.0"}


def claves():
    d = {}
    if os.path.exists(CLAVES):
        for l in open(CLAVES, encoding="utf-8"):
            k, _, v = l.strip().partition("=")
            if k and v and not k.startswith("#"):
                d[k.strip()] = v.strip()
    return d


def get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def buscar(a, k):
    res = []
    vert = a.orientacion == "vertical"
    if k.get("PIXABAY_KEY"):
        base = "https://pixabay.com/api/videos/" if a.tipo == "video" else "https://pixabay.com/api/"
        p = {"key": k["PIXABAY_KEY"], "q": a.q, "per_page": max(3, a.n), "safesearch": "true", "lang": "es"}
        if a.tipo == "foto":
            p["image_type"] = "photo"
            if a.orientacion:
                p["orientation"] = a.orientacion
        for h in get(base + "?" + urllib.parse.urlencode(p)).get("hits", []):
            if a.tipo == "video":
                v = h["videos"].get("large") or h["videos"].get("medium")
                w, hh = v.get("width", 0), v.get("height", 0)
                if a.orientacion and (hh > w) != vert:
                    continue
                res.append({"fuente": "pixabay", "id": h["id"], "dur_s": h.get("duration"), "tam": f"{w}x{hh}",
                            "etiquetas": h.get("tags"), "ver": h.get("pageURL")})
            else:
                res.append({"fuente": "pixabay", "id": h["id"], "tam": f"{h.get('imageWidth')}x{h.get('imageHeight')}",
                            "etiquetas": h.get("tags"), "ver": h.get("pageURL")})
    if k.get("PEXELS_KEY"):
        base = "https://api.pexels.com/videos/search" if a.tipo == "video" else "https://api.pexels.com/v1/search"
        p = {"query": a.q, "per_page": max(3, a.n), "locale": "es-ES"}
        if a.orientacion:
            p["orientation"] = "portrait" if vert else "landscape"
        d = get(base + "?" + urllib.parse.urlencode(p), {"Authorization": k["PEXELS_KEY"]})
        for h in d.get("videos" if a.tipo == "video" else "photos", []):
            res.append({"fuente": "pexels", "id": h["id"], "dur_s": h.get("duration"),
                        "tam": f"{h.get('width')}x{h.get('height')}", "etiquetas": h.get("alt") or "", "ver": h.get("url")})
    if not res and not (k.get("PIXABAY_KEY") or k.get("PEXELS_KEY")):
        sys.exit("No hay claves. Pega tu clave de Pixabay (o Pexels) en " + CLAVES)
    print(json.dumps(res[: a.n * 2], ensure_ascii=False, indent=1))


def bajar(a, k):
    if a.fuente == "pixabay":
        base = "https://pixabay.com/api/videos/" if a.tipo == "video" else "https://pixabay.com/api/"
        h = get(base + "?" + urllib.parse.urlencode({"key": k["PIXABAY_KEY"], "id": a.id}))["hits"][0]
        url = (h["videos"].get("large") or h["videos"]["medium"])["url"] if a.tipo == "video" else (h.get("largeImageURL") or h["webformatURL"])
        pagina, autor = h.get("pageURL"), h.get("user")
        lic = "Licencia de contenido de Pixabay (uso gratis, sin atribución obligatoria)"
    else:
        hdr = {"Authorization": k["PEXELS_KEY"]}
        if a.tipo == "video":
            h = get(f"https://api.pexels.com/videos/videos/{a.id}", hdr)
            f = sorted([x for x in h["video_files"] if x.get("width")], key=lambda x: x["width"] * x["height"])
            f = [x for x in f if max(x["width"], x["height"]) <= 1920] or f
            url, autor = f[-1]["link"], (h.get("user") or {}).get("name")
        else:
            h = get(f"https://api.pexels.com/v1/photos/{a.id}", hdr)
            url, autor = h["src"]["original"], h.get("photographer")
        pagina = h.get("url")
        lic = "Licencia de Pexels (uso gratis, sin atribución obligatoria)"
    ext = ".mp4" if a.tipo == "video" else os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".jpg"
    nombre = re.sub(r"[^a-z0-9_-]+", "_", (a.nombre or f"{a.fuente}_{a.id}").lower()) + ext
    os.makedirs(a.dest, exist_ok=True)
    ruta = os.path.join(a.dest, nombre)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(ruta, "wb") as out:
        out.write(r.read())
    with open(ruta + ".licencia.txt", "w", encoding="utf-8") as f:
        f.write(f"Fuente: {a.fuente.capitalize()} ({pagina})\nAutor: {autor}\nLicencia: {lic}\n"
                "Uso comercial: sí\nPublicidad: sí\n"
                "Cuidado: no vender el archivo tal cual; si hay personas o marcas reconocibles, no dar a entender que te recomiendan.\n")
    print("Descargado: " + ruta)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar"); b.add_argument("--tipo", choices=["video", "foto"], required=True); b.add_argument("--q", required=True)
    b.add_argument("--orientacion", choices=["vertical", "horizontal"]); b.add_argument("--n", type=int, default=6)
    d = sub.add_parser("bajar"); d.add_argument("--fuente", choices=["pixabay", "pexels"], required=True)
    d.add_argument("--tipo", choices=["video", "foto"], required=True); d.add_argument("--id", required=True)
    d.add_argument("--dest", required=True); d.add_argument("--nombre")
    a = ap.parse_args()
    k = claves()
    buscar(a, k) if a.cmd == "buscar" else bajar(a, k)


if __name__ == "__main__":
    main()
