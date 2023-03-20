import gc
import json
import math
import os
import random
import time
import uasyncio

from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN, PEN_P8
from ulab import numpy

from microdot_asyncio import Microdot, send_file
from microdot_asyncio_websocket import with_websocket
from phew import connect_to_wifi
from WIFI_CONFIG import SSID, PSK

"""
A random, trippy effect.
Experiment with the damping, number of spawns, intensity and offset to change the effect.
"""
gc.collect()

gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY_GALACTIC_UNICORN, pen_type=PEN_P8)

# MAXIMUM OVERKILL
# machine.freq(250_000_000)


def write_file(file, data):
    with open(file, "w") as f:
        s = json.dumps(data)
        f.write(s)
        PRESETS = os.listdir()

def read_file(file):
    with open(file, "r") as f:
        s = f.read()
        return json.loads(s)

print("Connecting to WIFI")
time.sleep(0.1)

ip = connect_to_wifi(SSID, PSK)
print(f"Start tripping at: http://{ip}")

server = Microdot()

@server.route("/", methods=["GET"])
def route_index(request):
    return send_file("/trippy_web_ui/index.html")


@server.route("/static/<path:path>", methods=["GET"])
def route_static(request, path):
    return send_file(f"/trippy_web_ui/static/{path}")

@server.route("/values", methods=["GET"])
def route_index(request):
    return VALUES

@server.route("/presets", methods=["GET"])
def route_index(request):
    return PRESETS

@server.route('/tripppppy')
@with_websocket
async def echo(request, ws):
    global VALUES, CURRENT_FILE, PRESETS, trippy
    while True:
        data = await ws.receive()
        payload = json.loads(data)
        key = payload.get('key')
        value = payload.get('value')
        file = payload.get('file')
        
        if key == "LOAD":
            CURRENT_FILE = file
            load_values()
            reset_display()
            await ws.send(json.dumps(VALUES))
            print(f"Loaded Preset: {CURRENT_FILE}", VALUES)

        elif key == "SAVE":
            write_file(CURRENT_FILE, VALUES)
            print(f"Saved Preset: {CURRENT_FILE}", VALUES)

        elif key == "SAVE_AS":
            write_file(file, VALUES)
            CURRENT_FILE = file
            PRESETS = os.listdir()
            # await ws.send(json.dumps(PRESETS))
            print(f"Saved Preset as: {CURRENT_FILE}", VALUES)

        elif key == "TEXT":
            VALUES[key] = value
            make_palette()

        elif key == "DRIFT":
            VALUES[key] = json.loads(value)
            
        else:
            VALUES[key] = float(value)

        if key == "BRIGHTNESS":
            gu.set_brightness(VALUES.get("BRIGHTNESS"))

        if key == "STROBE" and not VALUES.get("STROBE"):
            gu.set_brightness(VALUES.get("BRIGHTNESS"))

        if key.startswith("PALETTE"):
            make_palette()

def reset_display():
   trippy = numpy.zeros((height, width))
   make_palette()
   gu.set_brightness(VALUES.get("BRIGHTNESS"))

def make_palette():

    # reserve slots 0 and 1 for text color and text outline
    
    graphics.reset_pen(0)
    graphics.create_pen_hsv(0, 0, 0)

    graphics.reset_pen(1)
    graphics.create_pen_hsv(0, 0, 1)
        
    # Fill palette with a rainbow sweep
    for x in range(VALUES.get("PALETTE_SIZE")):
        hue = (float(x) / VALUES.get("PALETTE_SIZE") * VALUES.get("PALETTE_RANGE")) + VALUES.get("PALETTE_OFFSET")
        graphics.reset_pen(x + 2)
        _ = graphics.create_pen_hsv(hue, 1.0, 1.0)

async def gfxloop():
    global trippy
    
    count = 1

    levels = numpy.sin(numpy.linspace(-numpy.pi, numpy.pi, 64))
    
    while True:
        
        BRIGHTNESS = VALUES.get("BRIGHTNESS")
        
        DAMPING_FACTOR = VALUES.get("DAMPING_FACTOR")
        INTENSITY = VALUES.get("INTENSITY")
        STROBE = VALUES.get("STROBE")
        SPEED = VALUES.get("SPEED")

        PALETTE_SIZE = VALUES.get("PALETTE_SIZE")
        
        DOT_WIDTH = VALUES.get("DOT_WIDTH")
        DOT_HEIGHT = VALUES.get("DOT_HEIGHT")
        DRIFT = VALUES.get('DRIFT')
        DRIFT_SPEED = VALUES.get('DRIFT_SPEED')

        TEXT = VALUES.get("TEXT")
        
        gc.collect()
        
        if STROBE:
            levels = numpy.roll(levels, math.ceil(8 * STROBE))
            gu.set_brightness(BRIGHTNESS * levels[0])

        if not count % (21 - SPEED):
            # add new drop
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            trippy[y][x] = random.randint(0, int(INTENSITY))

        a = numpy.roll(trippy, 1, axis=0) * DOT_WIDTH
        b = numpy.roll(trippy, -1, axis=0) * DOT_WIDTH
        d = numpy.roll(trippy, 1, axis=1) * DOT_HEIGHT
        e = numpy.roll(trippy, -1, axis=1) * DOT_HEIGHT

        # Average over 5 adjacent pixels and apply damping
        trippy[:] += a + b + d + e
        trippy[:] *= DAMPING_FACTOR / 5.0

        if DRIFT[0] and DRIFT_SPEED:
            z = numpy.roll(trippy, DRIFT[0], axis=DRIFT[1]) * DRIFT_SPEED
            trippy *= 1 - DRIFT_SPEED
            trippy += z 
        
        memoryview(graphics)[:] = numpy.ndarray((numpy.clip(trippy, 0, 1) * (PALETTE_SIZE - 1)) + 2 , dtype=numpy.uint8).tobytes()

        if TEXT:
            w = graphics.measure_text(TEXT, 1)
            ox = math.ceil((53 - w) / 2)
            # Draw text over the top
            graphics.set_pen(0)
            graphics.text(TEXT, ox - 1, 1, -1, 1)
            graphics.text(TEXT, ox - 1, 3, -1, 1)
            graphics.text(TEXT, ox - 1, 2, -1, 1)
            graphics.text(TEXT, ox, 1, -1, 1)
            graphics.text(TEXT, ox, 3, -1, 1)
            graphics.text(TEXT, ox + 1, 1, -1, 1)
            graphics.text(TEXT, ox + 1, 2, -1, 1)
            graphics.text(TEXT, ox + 1, 3, -1, 1)
#             graphics.text(TEXT, 2, 3, 1, 1)
            graphics.set_pen(1)
            graphics.text(TEXT, ox, 2, -1, 1)
    
        gu.update(graphics)

        count += 1

        await uasyncio.sleep_ms(10)


def load_values():
    global VALUES
    
    VALUES = read_file(CURRENT_FILE)
    if not VALUES.get('TEXT'):
        VALUES['TEXT'] = ''

    if not VALUES.get('DRIFT'):
        VALUES['DRIFT'] = [0, 0]

    if not VALUES.get('DRIFT_SPEED'):
        VALUES['DRIFT_SPEED'] = 0.0
        
    if not VALUES.get('STROBE'):
        VALUES['STROBE'] = 0

    #VALUES["TEXT"] = '1 2 3 4'

print("Loading Preset")
os.chdir('/trippy_web_ui/saves')
PRESETS = os.listdir()
CURRENT_FILE = PRESETS[0]
VALUES = None
load_values()

gu.set_brightness(VALUES["BRIGHTNESS"])
graphics.set_font("bitmap6")

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

trippy = numpy.zeros((height, width))

make_palette()

uasyncio.create_task(gfxloop())
server.run(host=ip, port=80)


