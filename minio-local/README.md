# MinIO Local Setup

Información para configurar un entorno local de MinIO para almacenamiento de objetos.

## Requisitos Previos

- Docker instalado en tu máquina local.
- Docker Compose instalado.

## Setup inicial

La primera vez que se ejecuta MinIO, se deben realizar los siguientes pasos:

1. Correr el contenedor de MinIO usando Docker Compose:

```bash
docker-compose up -d --build
```

2. Ejecutar el script de configuración dentro del contenedor:

```bash
docker compose run --rm minio-setup sh
```

## Para Iniciar MinIO

Para iniciar el servicio de MinIO, utiliza el siguiente comando:

```bash
docker-compose up -d
```
