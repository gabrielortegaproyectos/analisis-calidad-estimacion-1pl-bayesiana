#!/bin/bash
# Script para probar el sitio web localmente

echo "🌐 Iniciando servidor web local para probar GitHub Pages..."

# Verificar si Python está disponible
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python no está instalado. Instala Python para continuar."
    exit 1
fi

# Cambiar al directorio docs
cd "$(dirname "$0")/docs" || exit 1

echo "📁 Sirviendo archivos desde: $(pwd)"
echo "🔗 Sitio disponible en: http://localhost:8000"
echo "📊 Pipeline disponible en: http://localhost:8000/pipeline_visualization/api/main"
echo ""
echo "💡 Presiona Ctrl+C para detener el servidor"
echo ""

# Iniciar servidor
$PYTHON_CMD -m http.server 8000
