# Desarrollo de un Sistema Inteligente para la Transcripción y Resumen Automático de Contenido Multimedia

## Descripción

En este Trabajo de Fin de Máster se ha diseñado e implementado un sistema inteligente capaz de transcribir automáticamente contenido multimedia, audios o vídeos y generar a partir de dicha transcripción:

- Resúmenes breves y detallados.
- Títulos temáticos para cada fragmento.

El sistema integra:

1. **Reconocimiento Automático del Habla (ASR)** basado en el modelo Whisper de OpenAI.
2. **Preprocesamiento lingüístico** para depurar las transcripciones (eliminación de muletillas y ruido verbal).
3. **Generación de resúmenes** mediante el modelo Gemma 4B ejecutado localmente con Ollama.
4. **Interfaz web** desarrollada en Flask para:
   - Subida de archivos multimedia.
   - Almacenamiento de historiales.
   - Consulta de resultados en una base de datos SQLite.

La evaluación del sistema, realizada sobre distintos casos de prueba y medida con métricas ROUGE, muestra un alto grado de precisión en la selección de contenido relevante. Se discuten limitaciones operativas (recursos GPU, escalabilidad) y se plantean líneas futuras como integración de traducción automática y despliegue en contenedores o entornos cloud.

## Características

- Transcripción automática de audio y vídeo.
- Limpieza y normalización de texto.
- Resúmenes temáticos y detallados.
- Generación de títulos automáticos.
- Interfaz web intuitiva con Flask.
- Persistence layer con SQLite para historiales.

## Requisitos de Software

- Python 3.x
- Librerías de Python listadas en `requirements.txt` y `requirements-gpu.txt`.
- Ollama (modelo Gemma3:4b).
- FFmpeg.
- Ngrok.

## Instalación

1. Clonar este repositorio:

   ```bash
   git clone https://github.com/elenagonzalezrebollo/TFM.git
   cd TFM
2. Crear y activar un entorno virtual:
   ```bash
    python3 -m venv venv
    venv\Scripts\activate      
3. Instalar los requisitos:
   ```bash
    pip install -r requirements.txt requirements-gpu.txt
4. Configurar variables de entorno:

- FFMPEG_PATH: Ruta al ejecutable de FFmpeg.
- Variables necesarias para Ollama (según instalación local).

## Uso
1. Navegar al directorio de la aplicación Flask:
   ```bash
    cd tfm_flask
2. Iniciar el servidor:
   ```bash
    # Opción 1: script de arranque
    ./run.py

    # Opción 2: comando Flask
    flask run --host=0.0.0.0 --port=5000
3. (Opcional) Exponer la App públicamente con Ngrok:
   ```bash
    ngrok http 5000
4. Abrir la URL generada por Ngrok o http://localhost:5000 en el navegador.

## Licencia
Este proyecto está licenciado bajo los términos de la licencia AGPL-3.0 license. Consulta el archivo LICENSE para más detalles.
