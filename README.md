# QA Project - Urban Routes (Automatización UI)

## Descripción del Proyecto
Este proyecto contiene una suite de pruebas automatizadas E2E (End-to-End) para la aplicación web Urban Routes. El objetivo es validar la funcionalidad principal de la plataforma: el flujo completo para solicitar un taxi.

Las pruebas simulan el comportamiento de un usuario real, abarcando las siguientes acciones:
1. Configuración de la ruta (origen y destino).
2. Selección de la tarifa "Comfort".
3. Registro de número de teléfono y validación mediante código SMS interceptado.
4. Vinculación de una tarjeta de crédito como método de pago.
5. Inserción de comentarios para el conductor.
6. Adición de extras al viaje (manta, pañuelos y helados).
7. Solicitud final del servicio y espera de asignación de conductor.

## Tecnologías y Técnicas Utilizadas
* **Lenguaje:** Python 3
* **Framework de Pruebas:** Pytest
* **Automatización Web:** Selenium WebDriver
* **Patrón de Diseño Arquitectónico:** Page Object Model (POM) para separar la lógica de la prueba de los localizadores web.
* **Control de Versiones:** Git / GitHub

## Requisitos Previos
* Python 3.x instalado.
* Google Chrome instalado.
* `chromedriver` compatible con tu versión de Chrome.

## Instalación y Configuración
1. Clona este repositorio en tu máquina local:
   ```bash
   git clone git@github.com:HaiD-69/qa-project-Urban-Routes-es.git