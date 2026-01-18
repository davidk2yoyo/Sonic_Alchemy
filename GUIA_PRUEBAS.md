# 🧪 Guía de Pruebas - VoiceCanvas

## 📋 Estado del Sistema

✅ **Sistema completamente funcional y listo para pruebas**

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3010
- MinIO Console: http://localhost:9011

## 🚀 Pasos para Probar el Sistema

### 1. Abrir Swagger UI (Recomendado)

1. Abre tu navegador y ve a: **http://localhost:8000/docs**
2. Verás la documentación interactiva de la API

### 2. Autenticarse

1. En Swagger UI, busca el endpoint **`POST /api/v1/auth/login`**
2. Haz clic en "Try it out"
3. Usa estas credenciales:
   ```json
   {
     "email": "demo@voicecanvas.com",
     "password": "Demo123456"
   }
   ```
4. Haz clic en "Execute"
5. Copia el `access_token` de la respuesta

### 3. Autorizar en Swagger

1. Haz clic en el botón **"Authorize"** (🔒) en la parte superior derecha
2. Pega el `access_token` en el campo "Value"
3. Haz clic en "Authorize"
4. Cierra el diálogo

### 4. Probar Endpoints

#### 📝 Generar Letras

1. Busca **`POST /api/v1/lyrics/generate`**
2. Haz clic en "Try it out"
3. Ingresa:
   ```json
   {
     "theme": "amor en la playa",
     "emotion": "felicidad",
     "style": "balada"
   }
   ```
4. Haz clic en "Execute"
5. Verás las letras generadas por Gemini

#### 🎨 Subir y Analizar Canvas (Imagen)

1. Busca **`POST /api/v1/canvas/upload`**
2. Haz clic en "Try it out"
3. Haz clic en "Choose File" y selecciona una imagen (JPG, PNG, WEBP)
4. Haz clic en "Execute"
5. Copia el `id` del canvas de la respuesta
6. Busca **`POST /api/v1/canvas/analyze/{canvas_id}`**
7. Ingresa el `canvas_id` que copiaste
8. Haz clic en "Execute"
9. Verás el análisis de emociones de la imagen

#### 🎤 Subir y Procesar Audio

1. Busca **`POST /api/v1/voice/upload`**
2. Haz clic en "Try it out"
3. Haz clic en "Choose File" y selecciona un archivo de audio (WAV, MP3, M4A, OGG)
4. Haz clic en "Execute"
5. Copia el `id` del voice recording de la respuesta
6. Busca **`POST /api/v1/voice/process/{voice_id}`**
7. Ingresa el `voice_id` y las correcciones deseadas
8. Haz clic en "Execute"
9. Verás el procesamiento del audio

#### 📁 Proyectos

1. Busca **`GET /api/v1/projects`**
2. Haz clic en "Try it out" y luego "Execute"
3. Verás la lista de tus proyectos

## ✅ Verificación de Funcionalidad

### Endpoints que Deben Funcionar:

- ✅ `POST /api/v1/auth/login` - Login
- ✅ `POST /api/v1/auth/register` - Registro
- ✅ `POST /api/v1/lyrics/generate` - Generar letras
- ✅ `POST /api/v1/canvas/upload` - Subir imagen
- ✅ `POST /api/v1/canvas/analyze/{id}` - Analizar imagen
- ✅ `GET /api/v1/canvas/{id}` - Obtener canvas
- ✅ `POST /api/v1/voice/upload` - Subir audio
- ✅ `POST /api/v1/voice/process/{id}` - Procesar audio
- ✅ `GET /api/v1/voice/{id}` - Obtener voice recording
- ✅ `GET /api/v1/projects` - Listar proyectos
- ✅ `POST /api/v1/projects` - Crear proyecto

## 🔧 Solución de Problemas

### Si un endpoint da error 500:
- Verifica que estés autenticado (token válido)
- Revisa los logs del backend
- Verifica que los servicios Docker estén corriendo

### Si no puedes subir archivos:
- Verifica que MinIO esté corriendo: `docker-compose ps`
- Verifica que el archivo sea del formato correcto
- Verifica que el tamaño del archivo no exceda el límite (50MB)

### Si Gemini no funciona:
- Verifica que `GEMINI_API_KEY` esté configurada en `.env`
- Verifica que no hayas excedido la cuota de la API

## 📝 Notas

- Todos los endpoints requieren autenticación (excepto login/register)
- Los archivos se almacenan en MinIO
- El procesamiento de imágenes y audio puede tomar tiempo
- Los resultados se guardan en la base de datos PostgreSQL
