#!/bin/bash

# Script para activar el entorno virtual de Python
echo "Activando entorno virtual 'env'..."
source /root/webpython+react/env/bin/activate

echo "Entorno virtual activado!"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo ""
echo "Para desactivar el entorno virtual, ejecuta: deactivate"
echo "Para ejecutar el backend: cd backend && python run.py"
echo "Para ejecutar el frontend: cd frontend && npm start"
