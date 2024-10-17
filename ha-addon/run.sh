#!/bin/bash
set -e

# Ejecutar el script de Python que convierte JSON en YAML
python3 /botaffiumeiro/json2yaml.py

cat /botaffiumeiro/data/config.yaml

# Iniciar el bot
python3 /botaffiumeiro/botaffiumeiro.py
