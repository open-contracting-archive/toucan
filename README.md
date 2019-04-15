# OCDS Kit Web
OCDS Kit Web es una aplicación web para la manipulación de archivos OCDS basada en el proyecto [OCDS Kit](https://github.com/open-contracting/ocdskit).
OCDS Kit Web provee al usuario las mismas funcionalidades de OCDS Kit a través de una interfaz web intuitiva y fácil de utilizar.

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
* OCDSKIT_WEB_MEDIA_ROOT: ruta del directorio donde se guardan los archivos subidos. A libre elección.
* OCDSKIT_WEB_LOCALE_PATH: Debe apuntar al directorio locale/ dentro del proyecto.
* OCDSKIT_WEB_MAXNUMFILES: número máximo de archivos a subir por operación.
* OCDSKIT_WEB_MAXFILESIZE: tamaño máximo de archivos a subir en bytes.

### Levantar el proyecto
Levantar el servidor de desarrollo:
```
python manage.py runserver
```

## Funcionalidades
### Create Release Packages
Genera un Release Package a partir de varios archivos Release.
Utiliza el comando `package-releases`.
>Tipo de archivo válido: Release.

### Merge Release Packages
Genera un Record Package a partir de archivos Release Package.
Utiliza el comando `combine-release-packages`.
>Tipo de archivo válido: Release Package.

### Upgrade from 1.0 to 1.1
Actualiza packages y releases de la versión 1.0 de OCDS a la 1.1.
Utiliza el comando `upgrade`.
>Tipo de archivo válido: cualquier tipo.

### Generate a spreadsheet version of schema
Genera un spreadsheet de cualquier versión de un OCDS schema.
Utiliza el comando `mapping-sheet`.
>Puede generar spreadsheets de Release, Release Package o Record Package.

### Convert to CSV/Excel
Convierte un archivo Release Package a una versión CSV/Excel.
Utiliza la herramienta [flatten-tool](https://github.com/OpenDataServices/flatten-tool).
>Tipo de archivo válido: Release Package.

### Data Review Tool
Enlaza a la [Herramienta de Revisión de Datos](http://standard.open-contracting.org/review/).

### OCDS Extension Creator
Enlaza a la [Herramienta de Creación de Extensiones OCDS](https://open-contracting.github.io/extension_creator/).

## Arquitectura
### Descripción  de la arquitectura
Se utiliza Django Framework para construir los módulos Fron-end y Back-end para la aplicación.
El módulo Front-end contiene los elementos de presentación para interactuar con el usuario.
En el módulo Back-end se encuentran implementados el OCDS Kit y el flatten-tool como librerias que implementan las funcionalidades.
![alt text](https://github.com/lucianovh95/ocdskit-web/blob/ocdskit-web-uca/blob/img/architecture.png "Diagrama General")

### Diseño
Página principal de la aplicación:

![alt text](https://github.com/lucianovh95/ocdskit-web/blob/ocdskit-web-uca/blob/img/landing_page.png "Página de inicio")

Vista de funcionalidades, el diseño es el mismo:

![alt text](https://github.com/lucianovh95/ocdskit-web/blob/ocdskit-web-uca/blob/img/feature_view.png "Diseño para las funcionalidades")

### Restricciones
Las restricciones del sistema son las siguientes:

Tamaño máximo de archivos | 10MB
--- | ---
Cantidad máxima de archivos por operación | 20
Timeout de sesión | 24 horas

## Ejemplos de uso
### Crear un Release Package
1. Agregar uno o más archivos release.
2. Generar Release Package.

![alt text](https://github.com/lucianovh95/ocdskit-web/blob/ocdskit-web-uca/blob/img/example1_a.png "Página de la función.")

Al generar con éxito un Release Package, aparece el siguiente mensaje para descargar el archivo.

![alt text](https://github.com/lucianovh95/ocdskit-web/blob/ocdskit-web-uca/blob/img/example1_b.png "Mensaje de éxito.")

### Generar una versión spreadsheet de un OCDS schema
1. Seleccionar la versión y tipo de archivo a generar.
2. Genera y descarga el archivo.

![alt text](https://github.com/lucianovh95/ocdskit-web/blob/ocdskit-web-uca/blob/img/example2.png "Página de la función.")

## Herramientas utilizadas
* [Python 3.5+](https://www.python.org/) - Lenguaje de programación interpretado.
* [Django 2.1](https://www.djangoproject.com/) - Framework Web de Python.
* [JQuery 3.3](https://jquery.com/) - Biblioteca JavaScript.
* [Bootstrap 3](https://getbootstrap.com/) - Biblioteca Multiplataforma.

## Versiones
Se utiliza Git para el control de versiones.

## Licencias
Copyright (c) Open Contracting Partnership