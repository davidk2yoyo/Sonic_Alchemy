#!/bin/bash
# Activation script for Python virtual environment

source venv/bin/activate
echo "Virtual environment activated!"
echo "Python: $(which python)"
echo "Python version: $(python --version)"
