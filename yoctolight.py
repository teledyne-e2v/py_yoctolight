# ********************************************************************
#
#  $Id: helloworld.py 58233 2023-12-04 10:57:58Z seb $
#
#  An example that shows how to use a  Yocto-Light
#
#  You can find more information on our web site:
#   Yocto-Light documentation:
#      https://www.yoctopuce.com/EN/products/yocto-light/doc.html
#   Python V2 API Reference:
#      https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html
#
# *********************************************************************

#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, time
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
# from YoctoLib.Sources.yocto_api import YRefParam
# add ../../Sources to the PYTHONPATH
sys.path.append(os.path.join("Sources"))
from yocto_api import *
from yocto_lightsensor import *

# --- Declaration Constante
ExitKey = "escape"      # Touche pour quitter l'appli
LightOnKey = " "        # Touche Pour éteindre / Allumer la Led
ResetKey = "enter"      # Touche pour reset du graphique
HelpKey = "h"        # Touche pour Afficher Masque l'aide

# --- Contenu de l’aide ---
help_text = (
    "Raccourcis :\n"
    "  • ESC : Quitter\n"
    "  • ESPACE : Basculer 'Led ON / OFF'\n"
    "  • ENTER : Reset affichage\n"
    "  • H : Afficher/masquer cette aide"
)

# --- Déclaration des variables
stop = {"value": False}  # dict pour mutabilité dans la closure
flag_Light = True
times = []
mlx_values = []
help_visible = True

def die(msg):
    sys.exit(msg + ' (check USB cable)')

def on_key(event):
    global flag_Light, times, mlx_values, help_visible
    # suivant le backend, la touche remonte 'escape' ou 'esc'
    if event.key == ExitKey:
        stop["value"] = True
        print("Échap détecté")
    elif event.key == LightOnKey:
        flag_Light = not (flag_Light)
        if flag_Light:
            print('Led ON')
            module.set_beacon(YModule.BEACON_OFF)  # BEACON_OFF
            module.get_persistentSettings(tval)

            module.set_luminosity(90)
        else :
            print('Led OFF')
            module.set_beacon(YModule.BEACON_OFF)  # BEACON_ON
            module.set_luminosity(0)
    elif event.key == ResetKey:
        times = []
        mlx_values = []
    elif event.key.lower() == HelpKey:
        help_visible = not help_visible
        help_box.set_visible(help_visible)
        fig.canvas.draw_idle()


errmsg = YRefParam()
#target = 'LGHTMK5C-2EB30D' # SN sur etiquet sachet ESD
target = None

# --- Intialisation du module Yocto
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("init error" + errmsg.value)

if target is None:
    # retreive any Light sensor
    sensor = YLightSensor.FirstLightSensor()
else:
    sensor = YLightSensor.FindLightSensor(target + '.lightSensor')

if sensor is None:
    die('No module connected')
    sys.exit()

module = sensor.get_module()
sensor.set_resolution(0.001)
sensor.set_measureType(YLightSensor.MEASURETYPE_HIGH_RESOLUTION) # MEASURETYPE_HUMAN_EYE
sensor.get_measureType()
module.saveToFlash()               # Pour sauvegarder dans le module

print(f"Product Name : {module.get_productName()}")
print(f"Serial:       {module.get_serialNumber()}")
print(f"Resolution: {sensor.get_resolution()} {sensor.get_measureType()}")

# --- Préparation du graphe Matplotlib ---
plt.ion()  # mode interactif
fig, ax = plt.subplots()

line, = ax.plot(times, mlx_values, "-o", markersize=3)
ax.set_xlabel("Temps (s)")
ax.set_ylabel("Luminosité (mlux)")
ax.set_title("Milli Lux" )
ax.grid(True)
cid = fig.canvas.mpl_connect("key_press_event", on_key)
# --- Ajout du texte d’aide en overlay (coordonnées axes : 0..1) ---
help_box = ax.text(
    0.01, 0.99, help_text,
    transform=ax.transAxes,
    va='top', ha='left', color='white',
    fontsize=10,
    bbox=dict(boxstyle='round', facecolor=(0, 0, 0, 0.6), edgecolor='none', pad=0.6)
)

# --- Boucle d'acquisition/affichage ---
t0 = time.time()
tval = 500
try:
    while sensor.isOnline() and not stop["value"]:
        YAPI.Sleep(tval)
        lux = sensor.get_currentValue()
        t = time.time() - t0
        print(f"Light :   {lux}lx - Time {t}")

        mlx_values.append(lux*1000)
        times.append(t)

        # Mise à jour du tracé
        line.set_data(times, mlx_values)

        ax.relim()
        ax.autoscale_view()
        plt.pause(tval/1000)

finally:
    # Nettoyage propre

    if target is None:
        # retreive any Light sensor
        print(" Yocto light disconnected or user break")
    else:
        print(target + " disconnected or user break")


    fig.canvas.mpl_disconnect(cid)
    YAPI.FreeAPI()
    plt.ioff()
    # plt.show()  # laisse la figure visible après l'arrêt, optionnel


