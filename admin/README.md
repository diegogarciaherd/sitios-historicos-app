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

# Grupo45

## Credenciales de prueba

## Credenciales de prueba

| Usuario               | Contraseña  | Rol en la app | Permisos / Notas                        |
|-----------------------|------------|---------------|----------------------------------------|
| admin@fiorella.com    | admin123   | admin         | Todo permitido                          |
| editor1@fiorella.com  | editor123  | editor        | Ver / Crear / Editar                     |
| editor2@fiorella.com  | editor123  | editor        | Bloqueado                                |
| viewer1@fiorella.com  | viewer123  | viewer        | Solo ver                                 |
| viewer2@fiorella.com  | viewer123  | viewer        | Solo ver                                 |
| norole@fiorella.com   | norole123  | sin rol       | SysAdmin:                                |

---                     |

