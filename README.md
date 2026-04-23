# Iron Wings - WWII Flight Simulator

IL-2 Sturmovik style flight simulator built with Panda3D.

## Features

- **Realistic Flight Physics**: Based on IL-2 characteristics (AM-38 engine ~1500 HP)
- **Procedural Terrain**: Dynamic heightmap with grass, mountains, and water
- **IL-2 Style Aircraft**: Detailed model with engine cowling, armor plate, cannons
- **Full HUD**: Speed, altitude, vertical speed, throttle, heading, attitude
- **Atmospheric Effects**: Clouds, animated water, fog
- **Procedural Audio**: Engine and wind sounds

## Controls

| Key | Action |
|-----|--------|
| W/S | Pitch up/down |
| A/D | Roll left/right |
| Q/E | Yaw left/right |
| Shift | Increase throttle |
| Ctrl | Decrease throttle |
| Space | Air brake |
| R | Reset position |
| ESC | Quit |

## Requirements

- Python 3.8+
- Panda3D

## Installation

```bash
pip install panda3d
```

## Running

```bash
cd iron_wings
python main.py
```

## Flight Characteristics

- **Max Speed**: 200 m/s (~720 km/h)
- **Cruise Speed**: 100 m/s (~360 km/h)
- **Stall Speed**: 50 m/s (~180 km/h)
- **Max Altitude**: 8000 m
- **Engine Power**: 45000 N (AM-38 style)

## Physics Model

The simulator uses arcade-sim hybrid physics:
- Throttle affects engine power (0-100%)
- Lift based on dynamic pressure and angle of attack
- Drag based on speed and air density at altitude
- Coordinated turns (banking affects turn rate)
- Stall behavior when speed drops below threshold

## License

MIT
