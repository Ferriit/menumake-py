#!/bin/env bash

# Install script for menumake-py.

mv src/main.py src/menumake
chmod +x src/menumake
mv src/menumake /usr/local/bin/menumake

echo "menumake-py installed successfully"
