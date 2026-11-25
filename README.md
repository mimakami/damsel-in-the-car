# Damsel in the Car

A crash-safety arcade game for the Raspberry Pi 5, built for a Critical Making project on gender bias in vehicle crash safety.

The player dodges traffic with a rotary encoder; the faster they drive, the worse the crash. After a crash the game:

1. shows the injury risk for men and women at the crash speed, based on real crash data,
2. guides the player through a physical crash ramp: pull the lever to the blinking lights, release on 3-2-1,
3. plays a crash test replay at the crash speed,
4. lights up two crash test dummies (addressable LEDs) in the colour of the injury severity: green → yellow → orange → red → purple.

## Hardware

| Part | Connection on the Raspberry Pi 5 |
|---|---|
| Rotary encoder KY-040 | + → pin 1 (3.3 V), GND → pin 9, CLK → pin 11 (GPIO17), DT → pin 13 (GPIO27), SW → pin 15 (GPIO22) |
| 30 × WS2812 LEDs | 5V → pin 2, GND → pin 6, DIN → 330 Ω → pin 19 (GPIO10) |

LED order in the chain:

| LEDs | Position |
|---|---|
| 1–12 | right side of the ramp, top to bottom |
| 13–24 | left side of the ramp, bottom to top |
| 25 / 26 / 27 | male dummy: head / torso / lower body |
| 28 / 29 / 30 | female dummy: lower body / torso / head |

## Installation

On Raspberry Pi OS (Python 3.13):

```
sudo apt install python3-pygame python3-gpiozero python3-lgpio python3-dev
python3 -m pip install --break-system-packages --pre adafruit-blinka Adafruit-Blinka-Raspberry-Pi5-Neopixel
python3 car_game.py
```

`/dev/pio0` must exist and be accessible to the `gpio` group (Raspberry Pi OS from 2025 on; otherwise `sudo apt full-upgrade`). Without the encoder or LEDs the game still runs, with the keyboard: arrow keys, SPACE, ESC.

All settings (pins, brightness, difficulty levels, timings, language) are at the top of `car_game.py`.

## Files

| File | Purpose |
|---|---|
| `car_game.py` | the game |
| `led_test.py` | checks the LED chain on its own |
| `encoder_test.py` | checks the rotary encoder on its own |

## Data sources

The game uses the crash speed as delta-V, as if the car hit a solid wall.

- **Moderate injury or worse (MAIS 2+):** Wang, J.-S. (2022). *MAIS(05/08) Injury Probability Curves as Functions of Delta V.* NHTSA, DOT HS 813 219.
- **Female vs. male odds ratio (2.23, MAIS 2+):** Brumbelow, M. L. & Jermakian, J. S. (2022). *Injury risks and crashworthiness benefits for females and males: Which differences are physiological?* Traffic Injury Prevention 23(1).
- **Serious injury or death (AIS 3+), separate curves for men and women:** Funk, J. R., Cormier, J. M. & Gabler, H. C. (2008). *Effect of delta-V errors in NASS on frontal crash risk calculations.* Annals of Advances in Automotive Medicine 52, 155–164.
- Background: Forman, J. et al. (2019). *Automobile injury trends in the contemporary fleet: Belted occupants in frontal collisions.* Traffic Injury Prevention 20(6).

The NHTSA curve covers men and women together, so the female/male odds ratio is split evenly around it. This is an approximation for an exhibit, not a medical or engineering assessment.

## Credits

Pixel font: [Silkscreen](https://kottke.org/plus/type/silkscreen/) by Jason Kottke, SIL Open Font License 1.1, embedded in `car_game.py`.
