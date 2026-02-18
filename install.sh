#!/bin/env bash

# Install script for menumake-py.

cp src/main.py src/menumake
sudo chmod +x src/menumake
sudo cp src/menumake /usr/local/bin/menumake

echo "menumake-py installed successfully. You can run it using the command 'menumake'."
