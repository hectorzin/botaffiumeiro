#!/bin/bash

# Instalar pre-commit y las dependencias necesarias
pip install pre-commit types-requests types-PyYAML

# Instalar hooks de pre-commit
pre-commit install-hooks
