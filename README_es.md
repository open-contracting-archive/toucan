# OCDS Toucan

OCDS Toucan es una aplicación web para la manipulación de archivos OCDS basada en el proyecto [OCDS Kit](https://ocdskit.readthedocs.io/).
OCDS Toucan provee al usuario las mismas funcionalidades de OCDS Kit a través de una interfaz web intuitiva y fácil de utilizar.

## Inicio
### Prerequisitos
1. Instalar [Python 3.6+](https://www.python.org/downloads).
2. [Clonar](https://help.github.com/en/articles/cloning-a-repository) el proyecto de Github.
3. Instalar [virtualenv](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv). **La instalación de esta herramienta es opcional, pero recomendada**.

### Instalación
1. Instalar las dependencias del proyecto:
```
pip install -r requirements.txt
```
2. Definir las siguientes variables de entorno:
* OCDS_TOUCAN_MEDIA_ROOT: ruta del directorio donde se guardan los archivos subidos. A libre elección.
* OCDS_TOUCAN_LOCALE_PATH: Debe apuntar al directorio locale/ dentro del proyecto.
* OCDS_TOUCAN_MAXNUMFILES: número máximo de archivos a subir por operación.
* OCDS_TOUCAN_MAXFILESIZE: tamaño máximo de archivos a subir en bytes.

### Levantar el proyecto
Levantar el servidor de desarrollo:
```
python manage.py runserver
```
