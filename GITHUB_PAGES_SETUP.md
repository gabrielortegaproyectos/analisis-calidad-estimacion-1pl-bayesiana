# 📋 Guía de Configuración de GitHub Pages

## Pasos para activar GitHub Pages en tu repositorio:

### 1️⃣ Configuración en GitHub

1. **Accede a tu repositorio** en GitHub
2. **Ve a Settings** (Configuración) → **Pages** (en el menú lateral izquierdo)
3. **En "Source"** selecciona: **Deploy from a branch**
4. **En "Branch"** selecciona: **main** (o master si usas esa rama)
5. **En "Folder"** selecciona: **/ (root)** 
6. **Haz clic en "Save"**

### 2️⃣ Configuración de Actions (Permisos)

1. Ve a **Settings** → **Actions** → **General**
2. En **"Workflow permissions"** selecciona: **Read and write permissions**
3. Marca la casilla **"Allow GitHub Actions to create and approve pull requests"**
4. Haz clic en **"Save"**

### 3️⃣ Configuración de Pages (Permisos)

1. Ve a **Settings** → **Pages**
2. En **"Build and deployment"** cambia a: **GitHub Actions**
3. Esto permitirá que el workflow automatizado despliegue el sitio

### 4️⃣ Verificación

1. **Haz un push** a la rama main con todos los archivos
2. **Ve a Actions** para ver que se ejecute el workflow
3. **Espera unos minutos** hasta que se complete el despliegue
4. **Tu sitio estará disponible** en: `https://[tu-usuario].github.io/[nombre-repositorio]/`

---

## 🎯 Estructura de archivos creada:

```
docs/
├── index.html              # Página principal del sitio
├── _config.yml             # Configuración de Jekyll/GitHub Pages
├── README.md              # Documentación del sitio
├── .nojekyll              # Permite servir archivos con guiones bajos
└── pipeline_visualization/ # Visualización interactiva de Kedro-Viz
    └── api/
        └── main           # Punto de entrada del pipeline

.github/workflows/
├── pages.yml              # Workflow básico de despliegue
└── build-and-deploy.yml   # Workflow avanzado con generación automática
```

---

## 🔄 Actualización automática

El sitio se actualizará automáticamente cuando:
- ✅ Hagas push a la rama `main`
- ✅ Modifiques el pipeline (regenera visualización)
- ✅ Cambies archivos en la carpeta `docs/`

---

## 🛠️ Comandos útiles

### Generar visualización localmente:
```bash
# Generar la visualización del pipeline
kedro viz build --include-hooks

# Usar el script de actualización automática
./update_pipeline_viz.sh
```

### Vista previa local:
```bash
# Servir localmente (requiere Jekyll)
cd docs
bundle exec jekyll serve

# O usar Python para servir archivos estáticos
cd docs
python -m http.server 8000
```

---

## 🎨 Personalización

### Modificar la página principal:
- Edita `docs/index.html`
- Cambia colores, contenido, o estructura según tus necesidades

### Agregar más páginas:
- Crea nuevos archivos HTML en `docs/`
- Actualiza la navegación en `index.html`

### Cambiar el tema:
- Modifica `docs/_config.yml`
- Cambia `remote_theme` por otro tema de GitHub Pages

---

## 🚨 Solución de problemas

### El sitio no se despliega:
1. ✅ Verifica que GitHub Pages esté configurado en "GitHub Actions"
2. ✅ Revisa que los workflows tengan permisos de escritura
3. ✅ Asegúrate de hacer push a la rama main
4. ✅ Verifica en Actions si hay errores

### La visualización del pipeline no funciona:
1. ✅ Asegúrate de que `pipeline_visualization.html` se haya generado correctamente
2. ✅ Verifica que todos los archivos estén en `docs/pipeline_visualization/`
3. ✅ Revisa la consola del navegador para errores JavaScript

### Problemas de permisos:
1. ✅ Configura permisos de escritura en Actions
2. ✅ Usa GitHub Actions (no Jekyll automático)
3. ✅ Verifica que el GITHUB_TOKEN tenga permisos suficientes

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en GitHub Actions
2. Compara con la documentación oficial de GitHub Pages
3. Verifica que todos los archivos estén committeados correctamente
