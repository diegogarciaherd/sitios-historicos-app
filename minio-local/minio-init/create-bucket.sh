#!/bin/sh

set -e

echo "🔄 Esperando a que MinIO esté listo..."
sleep 5

echo "🔗 Configurando alias..."
mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

# Crear bucket si no existe
if ! mc ls local/grupo45 > /dev/null 2>&1; then
  echo "📦 Creando bucket grupo45..."
  mc mb local/grupo45
fi

# Crear carpeta public/ (MinIO no crea carpetas hasta que subas algo, pero sirve para orden)
mc cp /etc/hosts local/grupo45/public/placeholder.txt

# Permitir acceso público solo a /public/*
echo "🌍 Haciendo pública la carpeta public/..."
mc anonymous set download local/grupo45/public

echo "✅ Configuración completada."