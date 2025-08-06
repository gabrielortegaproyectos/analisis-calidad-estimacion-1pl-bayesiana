#!/bin/bash
# Script para generar y actualizar la visualización del pipeline

echo "🚀 Generando visualización del pipeline con Kedro-Viz..."

# Generar la visualización del pipeline
kedro viz build --include-hooks

# Copiar a la carpeta docs si existe
if [ -d "docs" ]; then
    echo "📁 Copiando visualización a docs/pipeline_visualization..."
    rm -rf docs/pipeline_visualization
    cp -r pipeline_visualization.html docs/pipeline_visualization
    echo "✅ Visualización actualizada en docs/"
else
    echo "⚠️  Directorio docs no encontrado. Creando estructura..."
    mkdir -p docs
    cp -r pipeline_visualization.html docs/pipeline_visualization
    echo "✅ Estructura creada y visualización copiada"
fi

echo "🎉 Pipeline visualizado y listo para GitHub Pages!"
echo "💡 Recuerda hacer commit de los cambios en docs/"
