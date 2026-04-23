# Iron Wings - WWII Flight Simulator Specification

## Project Overview

**Name**: Iron Wings
**Type**: Desktop Flight Simulator
**Engine**: Panda3D
**Target**: IL-2 Sturmovik-style WWII combat flight simulation

## Features

### Flight Physics
- **Realistic aircraft performance** based on IL-2 M3 specifications
- AM-38 engine simulation with throttle control
- Lift, drag, and thrust calculations
- Coordinated turns with banking
- Stall behavior at low speeds
- Altitude affects air density and performance

### Aircraft Model (IL-2 M3 Style)
- Fuselage with tapered nose cone
- Engine cowling (AM-38)
- Main wings with angled tips
- Horizontal and vertical stabilizers
- Armor plate (characteristic of IL-2)
- Dual cannon pods
- Three-blade propeller

### Environment
- **Terrain**: Procedural heightmap with grass, mountains, water
- **Sky**: Sky dome with sun
- **Clouds**: 50 volumetric cloud objects
- **Water**: Animated water plane (lakes/rivers)
- **Trees**: 300+ procedurally placed trees

### HUD Elements
- Airspeed (km/h)
- Altitude (m)
- Vertical Speed (m/s)
- Throttle (%)
- Heading (°)
- Pitch and Roll angles
- Stall and terrain warnings

### Controls
| Key | Action |
|-----|--------|
| W | Pitch up (nose down) |
| S | Pitch down (nose up) |
| A | Roll left |
| D | Roll right |
| Q | Yaw left |
| E | Yaw right |
| Shift | Increase throttle |
| Ctrl | Decrease throttle |
| Space | Air brake |
| R | Reset position |
| ESC | Quit |

## Technical Specifications

### Flight Parameters
| Parameter | Value |
|-----------|-------|
| Mass | 5000 kg |
| Max Thrust | 45000 N |
| Max Speed | 200 m/s (720 km/h) |
| Cruise Speed | 100 m/s (360 km/h) |
| Stall Speed | 50 m/s (180 km/h) |
| Wing Area | 30 m² |
| Wingspan | 18 m |
| Max Altitude | 8000 m |

### Control Rates
| Control | Rate |
|---------|------|
| Pitch | 0.8 rad/s |
| Roll | 1.2 rad/s |
| Yaw | 0.5 rad/s |

### Rendering
- Procedural terrain (128x128 segments)
- Dynamic lighting (ambient + directional)
- Fog and atmospheric effects
- Sky dome

## Architecture

```
iron_wings/
├── main.py          # Main simulator (single file)
├── run.sh           # Launch script
├── README.md        # Documentation
└── SPEC.md          # This file
```

## Dependencies
- Python 3.8+
- Panda3D 1.10.16+

## Running
```bash
pip install panda3d
python main.py
```

## License
MIT
