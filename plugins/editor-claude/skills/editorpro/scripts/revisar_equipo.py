#!/usr/bin/env python3
"""Revisa si el computador tiene lo necesario para editar videos con Claude.
Solo lee: no instala ni cambia nada. Funciona en Mac y Windows con Python 3.6+."""
import glob, json, os, platform, re, shutil, subprocess, sys

HOME = os.path.expanduser("~")
EXTRA = [os.path.join(HOME, p) for p in (".local/bin", ".local/node/bin", ".bun/bin")] + ["/opt/homebrew/bin", "/usr/local/bin"]


def which(name):
    p = shutil.which(name)
    if p:
        return p
    for d in EXTRA:
        for c in (name, name + ".exe"):
            f = os.path.join(d, c)
            if os.path.isfile(f) and os.access(f, os.X_OK):
                return f
    return None


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else ""
    except Exception:
        return ""


def ver(text):
    m = re.search(r"(\d+)\.(\d+)", text or "")
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def sistema():
    s = platform.system()
    if s == "Darwin":
        arm = platform.machine() == "arm64" or run(["sysctl", "-n", "hw.optional.arm64"]) == "1"
        return "mac-arm" if arm else "mac-intel"
    return "windows" if s == "Windows" else "linux"


def best_python():
    cands = [which("python"), which("python3"), sys.executable]
    if platform.system() == "Windows" and which("py"):
        cands.insert(0, "py")
    best = (None, (0, 0))
    for c in filter(None, cands):
        v = ver(run([c, "--version"]))
        if v > best[1]:
            best = (c, v)
    return best


def chrome():
    rutas = ["/Applications/Google Chrome.app", "/Applications/Chromium.app",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe")]
    return next((r for r in rutas if r and os.path.exists(r)), None)


def drive():
    d = glob.glob(os.path.join(HOME, "Library/CloudStorage/GoogleDrive-*"))
    if d:
        return d[0]
    for letra in "GHIJKLMNOPQRSTUVWXYZ":
        p = letra + r":\Mi unidad"
        if os.path.isdir(p) or os.path.isdir(letra + r":\My Drive"):
            return letra + ":\\"
    return None


def main():
    so = sistema()
    items = []

    def add(clave, ok, detalle, necesario=True):
        items.append({"clave": clave, "ok": bool(ok), "detalle": detalle, "necesario": necesario})

    ff = which("ffmpeg")
    add("FFmpeg", ff, run([ff, "-version"])[:60] if ff else "no instalado")
    fp = which("ffprobe")
    add("ffprobe", fp, fp or "no instalado")
    nd = which("node")
    nv = run([nd, "--version"]) if nd else ""
    add("Node.js 20+", nd and ver(nv) >= (20, 0), nv or "no instalado")
    py, pv = best_python()
    add("Python 3.10+", pv >= (3, 10), "%s (%d.%d)" % (py, pv[0], pv[1]) if py else "no instalado")
    ch = chrome()
    add("Chrome", ch, ch or "no instalado")
    libre = shutil.disk_usage(HOME).free / 1e9
    add("Espacio libre (15 GB+)", libre >= 15, "%.0f GB libres" % libre)
    if so == "mac-arm" or so == "mac-intel":
        add("Homebrew", which("brew"), which("brew") or ("no disponible en Mac Intel" if so == "mac-intel" else "no instalado"), necesario=False)
    if so == "windows":
        add("winget", which("winget"), which("winget") or "no instalado", necesario=False)
    yd = which("yt-dlp")
    add("yt-dlp (descargar referencias)", yd, run([yd, "--version"]) if yd else "no instalado (opcional, Nivel 2 y 6)", necesario=False)
    gl = which("gallery-dl")
    add("gallery-dl (Pinterest/Instagram)", gl, run([gl, "--version"]) if gl else "no instalado (opcional, Nivel 2)", necesario=False)
    bn = which("bun")
    add("Bun (Telegram)", bn, run([bn, "--version"]) if bn else "no instalado (opcional, Nivel 5)", necesario=False)
    gd = drive()
    add("Google Drive para escritorio", gd, gd or "no instalado (opcional, Nivel 3)", necesario=False)

    nombres = {"mac-arm": "Mac con Apple Silicon", "mac-intel": "Mac con Intel", "windows": "Windows", "linux": "Linux"}
    print("\nEquipo: %s · %s\n" % (nombres[so], platform.platform()))
    for i in items:
        marca = "✅" if i["ok"] else ("❌" if i["necesario"] else "➖")
        print("  %s %-28s %s" % (marca, i["clave"], i["detalle"]))
    falta = [i["clave"] for i in items if i["necesario"] and not i["ok"]]
    print("\n" + ("Todo listo ✅" if not falta else "Falta: " + ", ".join(falta)))
    print("JSON:" + json.dumps({"sistema": so, "falta": falta, "items": items}, ensure_ascii=False))


if __name__ == "__main__":
    main()
