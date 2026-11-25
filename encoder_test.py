"""Encoder test (KY-040 on GPIO17 = CLK, GPIO27 = DT, GPIO22 = button).
Run in Thonny, turn the knob and press it for 15 seconds, then copy everything
printed in the Shell window."""
import subprocess
import time
import traceback

CLK_PIN, DT_PIN, BTN_PIN = 17, 27, 22

# 1. is the game already running (autostart)? Then it holds the encoder pins.
try:
    out = subprocess.run(["pgrep", "-af", "car_game"], capture_output=True, text=True).stdout.strip()
    print("Running game copies:", out if out else "none")
except Exception as e:
    print("pgrep failed:", e)

# 2. which GPIO libraries does Python find, and where from?
for name in ("gpiozero", "lgpio", "RPi.GPIO", "pigpio"):
    try:
        mod = __import__(name, fromlist=["x"])
        print(f"{name}: {getattr(mod, '__version__', getattr(mod, 'VERSION', '?'))}  ({getattr(mod, '__file__', '?')})")
    except Exception as e:
        print(f"{name}: not available ({e.__class__.__name__}: {e})")

# 3. open the encoder with the Pi 5 library (lgpio) on purpose
from gpiozero import Device, RotaryEncoder, Button
try:
    from gpiozero.pins.lgpio import LGPIOFactory
    Device.pin_factory = LGPIOFactory()
    print("Pin factory: lgpio (forced)")
except Exception:
    print("Could not force lgpio:")
    traceback.print_exc()

try:
    enc = RotaryEncoder(CLK_PIN, DT_PIN, max_steps=0)
    btn = Button(BTN_PIN)
    print("Encoder opened with", type(Device.pin_factory).__name__)
except Exception:
    print("Could not open the encoder:")
    traceback.print_exc()
    raise SystemExit

print("Turn the knob and press it now (15 seconds)...")
last = None
t_end = time.time() + 15
while time.time() < t_end:
    now = (enc.steps, btn.is_pressed, enc.a.value, enc.b.value)
    if now != last:
        print(f"  steps {now[0]:4d}   button {'DOWN' if now[1] else 'up  '}   CLK {now[2]}  DT {now[3]}")
        last = now
    time.sleep(0.01)
print("Done.")
