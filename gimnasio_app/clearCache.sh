#!/bin/bash

echo "Verificando si estás en un entorno virtual..."

echo "Eliminando cachés y archivos generados..."
find . -name "__pycache__" -type d -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -type f -delete

echo "Eliminando entorno virtual si existe..."
if [ -d "env" ]; then
  rm -rf env
  echo "Entorno virtual eliminado."
else
  echo "No se encontró un entorno virtual para eliminar."
fi

echo "Eliminando base de datos existente..."
rm -f database/gimnasio.db

echo "Limpiando logs..."
rm -f logs/*.log

echo "Eliminando PDF's..."
rm -f generated_pdfs/*

# Salir del entorno virtual si está activado
if [[ "$VIRTUAL_ENV" != "" ]]; then
  echo "Saliendo del entorno virtual..."
  deactivate
else
  echo "No estás en un entorno virtual."
fi

echo "Proceso de limpieza completado. Puedes reiniciar el proyecto ahora."
