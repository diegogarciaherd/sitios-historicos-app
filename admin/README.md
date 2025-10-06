1. Para correr la aplicacion en local, ejecutar el comando:

```sh
python main.py
```

2. Para que ande el GEometry hay que instalar la extension postgis en la base de datos.

```sh
sudo apt update
sudo apt install postgis postgresql-16-postgis-3
```

y entrar en la base de datos y correr el comando:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```
