import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import configparser
import urllib.request
from datetime import datetime
import os
import threading
import time
import sys

# --- Ruta base del ejecutable ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")

# --- Funciones de configuración ---
def cargar_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        # Valores por defecto
        config['SETTINGS'] = {
            'guardar_cada_horas': '1',
            'ruta_log': BASE_DIR,
            'cerrar_despues': 'True'
        }
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
    else:
        config.read(CONFIG_FILE)
    return config

def guardar_config(config):
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

# --- Función para obtener IP pública ---
def obtener_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org") as r:
            ip = r.read().decode('utf-8')
        return ip
    except Exception:
        return None

# --- Guardar IP en archivo ---
def guardar_ip():
    ip = obtener_ip()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    carpeta_log = config['SETTINGS'].get('ruta_log', BASE_DIR)
    archivo_log = os.path.join(carpeta_log, 'ips.txt')

    # Crear carpeta si no existe
    if not os.path.exists(carpeta_log):
        os.makedirs(carpeta_log, exist_ok=True)

    if not ip:
        last_ip.set("Error: no se pudo registrar la IP")
        messagebox.showerror("Error", "No se pudo registrar la IP")
        return None

    try:
        with open(archivo_log, "a", encoding="utf-8") as f:
            f.write(f"{ts} - {ip}\n")
        last_ip.set(f"Última IP: {ip}\nRegistrada: {ts}")
        return ip
    except Exception:
        last_ip.set("Error: no se pudo registrar la IP")
        messagebox.showerror("Error", "No se pudo registrar la IP")
        return None

# --- Registro periódico ---
def registro_periodico():
    while True:
        ip = guardar_ip()
        if ip and config['SETTINGS'].getboolean('cerrar_despues', True):
            root.after(2000, root.destroy)
            break
        horas = float(config['SETTINGS'].get('guardar_cada_horas', '1'))
        time.sleep(horas * 3600)

# --- Configuración desde el menú ---
def configurar_horas():
    horas = simpledialog.askfloat("Configurar", "Cada cuántas horas guardar la IP:",
                                  initialvalue=float(config['SETTINGS'].get('guardar_cada_horas', '1')))
    if horas is not None:
        config['SETTINGS']['guardar_cada_horas'] = str(horas)
        guardar_config(config)
        messagebox.showinfo("Configuración", "Horas guardadas correctamente.")

def configurar_ruta():
    carpeta = filedialog.askdirectory(initialdir=config['SETTINGS'].get('ruta_log', BASE_DIR),
                                      title="Seleccionar carpeta donde guardar el log")
    if carpeta:
        config['SETTINGS']['ruta_log'] = carpeta
        guardar_config(config)
        messagebox.showinfo("Configuración", f"Log se guardará en:\n{carpeta}")

def configurar_cierre():
    cerrar = messagebox.askyesno("Configurar", "Cerrar la app después de registrar la IP?")
    config['SETTINGS']['cerrar_despues'] = str(cerrar)
    guardar_config(config)
    messagebox.showinfo("Configuración", "Parámetro de cierre guardado correctamente.")

# --- Interfaz ---
root = tk.Tk()
root.title("Registro automático de IP")
root.geometry("450x200")
root.resizable(False, False)

last_ip = tk.StringVar(value="Obteniendo IP...")

tk.Label(root, textvariable=last_ip, font=("Arial", 12), justify="center").pack(expand=True, pady=20)

# --- Menú ---
config = cargar_config()
menubar = tk.Menu(root)
menu_config = tk.Menu(menubar, tearoff=0)
menu_config.add_command(label="Intervalo de registro (horas)", command=configurar_horas)
menu_config.add_command(label="Ruta donde guardar log", command=configurar_ruta)
menu_config.add_command(label="Cerrar app después de registrar", command=configurar_cierre)
menubar.add_cascade(label="Configuración", menu=menu_config)
root.config(menu=menubar)

# --- Ejecutar registro automático en segundo hilo ---
threading.Thread(target=registro_periodico, daemon=True).start()

root.mainloop()
