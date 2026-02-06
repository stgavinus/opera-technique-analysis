#!/bin/bash

# Ensure we are in the project root
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please wait, setting it up..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

echo "---------------------------------------------------------"
echo " Opera Technique Analysis - Launcher"
echo "---------------------------------------------------------"
echo " 1) Live Analysis Mode (Voice Report: Vibrato, HNR, etc.)"
echo " 2) Visual Feedback Mode (Real-time Spectrum & Waveform)"
echo " q) Quit"
echo "---------------------------------------------------------"
read -p "Select an option: " choice

case $choice in
    1)
        echo "Starting Live Analysis Mode..."
        ./venv/bin/python opera_technique/live_session.py
        ;;
    2)
        echo "Starting Visual Feedback Mode..."
        ./venv/bin/python opera_technique/visual_session.py
        ;;
    q|Q)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid option."
        exit 1
        ;;
esac
