#!/bin/bash
# Iron Wings - Run Script

cd "$(dirname "$0")"

echo "Starting Iron Wings - WWII Flight Simulator..."
echo ""
echo "Controls:"
echo "  W/S - Pitch up/down"
echo "  A/D - Roll left/right"
echo "  Q/E - Yaw"
echo "  Shift/Ctrl - Throttle"
echo "  Space - Brake"
echo "  R - Reset"
echo "  ESC - Quit"
echo ""

python main.py
