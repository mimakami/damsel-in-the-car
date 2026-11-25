"""LED test for the Raspberry Pi 5 (WS2812 / NeoPixel chain on GPIO10 = pin 19).

Stop the game first (two programs cannot drive the LEDs at the same time).
Run this file in Thonny and copy everything printed in the Shell window.

What you should see on the LEDs:
  1. all red, 2. all green, 3. all blue (1 second each)
  4. one white light running from LED 1 to LED 30 (the number is printed)
  5. the dummy LEDs (25-30) in green, yellow, orange, red
  6. all off
"""
import os
import sys
import time
import traceback

LED_PIN = 10          # GPIO10 = physical pin 19
LED_COUNT = 30
LED_ORDER = "RGB"     # if red and green come out swapped, change to "GRB"
BRIGHT = 60           # 0..255, kept low for the test

print("Python:", sys.executable, sys.version.split()[0])


def check_device(path):
    if not os.path.exists(path):
        print(f"  {path}: MISSING")
        return False
    st = os.stat(path)
    try:
        import grp
        group = grp.getgrgid(st.st_gid).gr_name
    except Exception:
        group = st.st_gid
    print(f"  {path}: present, group '{group}', mode {oct(st.st_mode & 0o777)}")
    return True


print("Devices:")
has_pio = check_device("/dev/pio0")
has_spi = check_device("/dev/spidev0.0")
try:
    import grp
    import getpass
    user = getpass.getuser()
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    print(f"  user '{user}' is in groups: {', '.join(groups)}")
except Exception:
    pass


def run_test(set_all, set_one, show):
    def fill(c):
        set_all(c)
        show()
    for name, c in (("red", (BRIGHT, 0, 0)), ("green", (0, BRIGHT, 0)), ("blue", (0, 0, BRIGHT))):
        print("  all", name)
        fill(c)
        time.sleep(1.0)
    fill((0, 0, 0))
    for i in range(LED_COUNT):
        print("  LED", i + 1)
        set_all((0, 0, 0))
        set_one(i, (BRIGHT, BRIGHT, BRIGHT))
        show()
        time.sleep(0.25)
    fill((0, 0, 0))
    print("  dummy colours on LEDs 25-30 (what the game uses for injury severity):")
    for name, c in (("green  = low risk", (0, 255, 0)), ("yellow = moderate", (255, 190, 0)),
                    ("orange = high", (255, 90, 0)), ("red    = very likely", (255, 0, 0))):
        print("   ", name)
        set_all((0, 0, 0))
        for i in range(24, min(30, LED_COUNT)):
            set_one(i, tuple(int(v * 0.8) for v in c))
        show()
        time.sleep(1.5)
    fill((0, 0, 0))
    print("  done, all off")


# ---- 1. Adafruit Pi 5 driver (PIO) ----
print("\nTest 1: Adafruit Pi 5 NeoPixel driver (PIO)")
ok = False
try:
    import board
    print("  import board: ok")
    from adafruit_raspberry_pi5_neopixel_write import neopixel_write
    print("  import adafruit_raspberry_pi5_neopixel_write: ok")
    pin = getattr(board, f"D{LED_PIN}")
    pixels = [(0, 0, 0)] * LED_COUNT

    def set_all(c):
        for i in range(LED_COUNT):
            pixels[i] = c

    def set_one(i, c):
        pixels[i] = c

    def show():
        data = bytearray()
        for r, g, b in pixels:
            data += bytes((g, r, b)) if LED_ORDER == "GRB" else bytes((r, g, b))
        neopixel_write(pin, data)

    run_test(set_all, set_one, show)
    ok = True
except Exception:
    print("  FAILED:")
    traceback.print_exc()

# ---- 2. Pi5Neo (SPI) ----
if not ok:
    print("\nTest 2: Pi5Neo (SPI, needs SPI switched on in raspi-config)")
    try:
        from pi5neo import Pi5Neo
        print("  import pi5neo: ok")
        neo = Pi5Neo("/dev/spidev0.0", LED_COUNT, 800)

        def order(c):
            r, g, b = c
            return (g, r, b) if LED_ORDER == "RGB" else (r, g, b)

        def set_all(c):
            for i in range(LED_COUNT):
                neo.set_led_color(i, *order(c))

        def set_one(i, c):
            neo.set_led_color(i, *order(c))

        run_test(set_all, set_one, neo.update_strip)
        ok = True
    except Exception:
        print("  FAILED:")
        traceback.print_exc()

print("\nRESULT:", "a driver worked - did the LEDs do what is described at the top?" if ok
      else "no driver could talk to the LEDs - please send me everything above")
