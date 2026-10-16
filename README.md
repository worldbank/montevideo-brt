# Proyecto Montevideo BRT

Este repositorio analiza la movilidad urbana en el Área Metropolitana de Montevideo y sus alrededores. Utilizando datos provistos por Kido Dynamics, Waze y Mapbox a través del [Development Data Partnership](portal.datapartnership.org/home), se evaluaron la movilidad de personas entre zonas del área de estudio, los embotellamientos y siniestros viales, y los tiempos de viaje para pares O-D de interés.

Para complementar el análisis, se utilizaron datos del Censo 2023 y se estimó el índice de Necesidades Básicas Insatisfechas (NBI) para evaluar niveles de accesibilidad.

Cobertura temporal de los datos: 

- Matriz de movilidad: 3 miércoles del mes de octubre de 2025.

- Congestión vial y accidentes: 4 de septiembre de 2021 al 30 de agosto de 2026.

- Tiempos de viaje: 27 de julio al 1 de septiembre de 2026.

## Tabla de Contenidos
```{tableofcontents}
```

## Instrucciones de uso
### Requisitos previos

- Python 3.8 o superior
- Jupyter Lab para ejecutar los notebooks

### Instalación

1. Clone el repositorio:
   ```bash
   git clone https://github.com/worldbank/montevideo-brt.git
   cd montevideo-brt
   ```

2. Cree y active el entorno de conda:
   ```bash
   conda env create -f environment.yml
   conda activate montevideo-brt
   ```

### Uso

Para consultar la documentación detallada y los notebooks de análisis, visita la [documentación del proyecto](https://legendary-dollop-k53e1zj.pages.github.io/README.html).


## Contacto

Para consultas, comentarios o contribuciones, póngase en contacto con el Development Data Partnership a través de datapartnership@worldbank.org.

También puede abrir un issue en el [repositorio de GitHub](https://github.com/worldbank/montevideo-brt/issues).

## Code of Conduct

The World Bank Data Lab <span style="color:#3EACAD">template</span> used to create this project maintains a [Code of Conduct](docs/CODE_OF_CONDUCT.md) to ensure an inclusive and respectful environment for everyone. Please adhere to it in all interactions within our community.

## License

This project is licensed under the MIT License together with the [World Bank IGO Rider](https://github.com.mcas.ms/worldbank/.github/blob/main/WB-IGO-RIDER.md). The Rider is purely procedural: it reserves all privileges and immunities enjoyed by the World Bank, without adding restrictions to the MIT permissions. Please review both files before using, distributing or contributing.
