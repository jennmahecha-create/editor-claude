#!/usr/bin/env python3
"""Diagnostica el computador y elige el perfil de instalación de Mi Editor PRO.

Perfiles:
  PRO       16 GB de RAM o más y 25 GB libres: todo, incluido el seguimiento de objetos (SAM 2.1) y el 3D.
  ESTANDAR  8 a 16 GB de RAM o 15 a 25 GB libres: todo menos el seguimiento de objetos y el 3D.
  LIGERO    menos de 8 GB de RAM o menos de 15 GB libres: lo esencial (cortar, subtítulos, zooms, color,
            gráficos, efectos para vender); sin recortes de persona ni seguimiento.
Guarda ~/.claude/mi-editor-pro/perfil.json y lo imprime en español sencillo.
Uso: diagnosticar.py [--forzar PRO|ESTANDAR|LIGERO]"""
import argparse, json, os, platform, shutil, subprocess

SEGUIMIENTO = ["/etiqueta-sigue", "/foco", "/lupa", "/pixelar", "/reencuadre-objeto", "/parallax-3d",
               "/contorno-neon", "/sticker", "/eco", "/ingredientes (con objeto)"]
RECORTE = ["/sub-detras", "/titulo-detras", "/color-pop", "/fondo-borroso", "/cambiar-fondo", "/quitar-fondo"]


def ram_gb():
    try:
        s = platform.system()
        if s == "Darwin":
            return int(subprocess.check_output(["sysctl", "-n", "hw.memsize"]).strip()) / 1e9
        if s == "Windows":
            import ctypes
            class M(ctypes.Structure):
                _fields_ = [("l", ctypes.c_ulong), ("m", ctypes.c_ulong), ("t", ctypes.c_ulonglong),
                            ("a", ctypes.c_ulonglong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong),
                            ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("e", ctypes.c_ulonglong)]
            m = M(); m.l = ctypes.sizeof(M)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.t / 1e9
        for l in open("/proc/meminfo"):
            if l.startswith("MemTotal"):
                return int(l.split()[1]) / 1e6
    except Exception:
        pass
    return 8.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar", choices=["PRO", "ESTANDAR", "LIGERO"])
    a = ap.parse_args()
    ram = ram_gb()
    libre = shutil.disk_usage(os.path.expanduser("~")).free / 1e9
    nucleos = os.cpu_count() or 4
    s = platform.system()
    arm = platform.machine() in ("arm64", "aarch64")
    nvidia = bool(shutil.which("nvidia-smi"))
    if a.forzar:
        perfil = a.forzar
    elif ram >= 15.5 and libre >= 25:
        perfil = "PRO"
    elif ram >= 7.5 and libre >= 15:
        perfil = "ESTANDAR"
    else:
        perfil = "LIGERO"
    sin = {"PRO": [], "ESTANDAR": SEGUIMIENTO, "LIGERO": SEGUIMIENTO + RECORTE}[perfil]
    hilos = max(1, min(nucleos, 4 if perfil == "LIGERO" else (6 if perfil == "ESTANDAR" else nucleos)))
    d = {"perfil": perfil, "ram_gb": round(ram, 1), "disco_libre_gb": round(libre), "nucleos": nucleos,
         "sistema": ("mac-arm" if s == "Darwin" and arm else "mac-intel" if s == "Darwin" else s.lower()),
         "tarjeta_nvidia": nvidia, "instalar_seguimiento": perfil == "PRO", "instalar_recorte_preciso": perfil != "LIGERO",
         "efectos_no_disponibles": sin, "hilos_render": hilos,
         "nota": "Se puede subir de perfil más adelante con: «instala los efectos avanzados»."}
    os.makedirs(os.path.expanduser("~/.claude/mi-editor-pro"), exist_ok=True)
    json.dump(d, open(os.path.expanduser("~/.claude/mi-editor-pro/perfil.json"), "w"), ensure_ascii=False, indent=1)
    textos = {"PRO": "Tu computador es potente: instalo todo, incluidos los efectos avanzados.",
              "ESTANDAR": "Tu computador va muy bien: instalo todo lo importante. Dejo fuera solo los efectos que siguen objetos, que en tu equipo irían lentos.",
              "LIGERO": "Tu computador es modesto: instalo lo esencial para que vaya rápido y sin trabarse (cortes, subtítulos, zooms, color, gráficos y efectos para vender)."}
    print(f"Memoria: {d['ram_gb']} GB · Disco libre: {d['disco_libre_gb']} GB · Núcleos: {nucleos}")
    print(f"PERFIL: {perfil} · {textos[perfil]}")
    if libre < 10:
        print("AVISO: queda muy poco disco (menos de 10 GB). Libera espacio antes de editar.")
    print("JSON:" + json.dumps(d, ensure_ascii=False))


if __name__ == "__main__":
    main()
