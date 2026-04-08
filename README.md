# VisitaLab — Sistema de Visitas Industriales

Aplicación web full-stack para registrar y gestionar visitas industriales, con generación de informes ejecutivos usando IA (Claude).

## Arquitectura

```
visitalab/
├── app.py                  # Backend Flask + API REST + modelos BD
├── requirements.txt        # Dependencias Python
├── startup.sh              # Comando de arranque para Azure
├── .env.example            # Plantilla de variables de entorno
├── .gitignore
├── static/
│   └── index.html          # Frontend completo (SPA)
└── instance/               # Base de datos SQLite local (no se sube a git)
```

---

## Desarrollo local

### 1. Clonar e instalar dependencias

```bash
git clone https://github.com/TU_USUARIO/visitalab.git
cd visitalab

# Crear entorno virtual
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env — para desarrollo local no necesitas cambiar nada (usará SQLite)
```

### 3. Ejecutar en local

```bash
python app.py
# La app queda disponible en http://localhost:5000
```

---

## Despliegue en Azure (paso a paso)

### Parte 1 — Crear la base de datos PostgreSQL

1. En Azure Portal, busca **"Azure Database for PostgreSQL flexible server"**
2. Clic en **Create**
3. Configura:
   - **Server name**: `visitalab-db` (o el nombre que prefieras)
   - **Region**: la más cercana a ti (East US o Brazil South)
   - **PostgreSQL version**: 16
   - **Compute + storage**: `Burstable, B1ms` (el más económico para empezar)
   - **Admin username**: `visitalab_admin`
   - **Password**: elige una contraseña segura y guárdala
4. En **Networking**: selecciona "Allow public access" y agrega tu IP actual
5. Haz clic en **Review + create → Create**

Una vez creado:
1. Ve al recurso → **Databases** → **Add** → nombre: `visitalab`
2. Ve a **Connection strings** y copia la cadena de conexión. Tendrá esta forma:
   ```
   postgresql://visitalab_admin:TU_CONTRASEÑA@visitalab-db.postgres.database.azure.com/visitalab?sslmode=require
   ```

### Parte 2 — Crear el App Service

1. En Azure Portal, busca **"App Service"** → **Create**
2. Configura:
   - **Name**: `visitalab-app` (debe ser único globalmente)
   - **Publish**: Code
   - **Runtime stack**: Python 3.12
   - **OS**: Linux
   - **Region**: la misma que la BD
   - **Plan**: Free F1 (para empezar) o Basic B1
3. Clic en **Review + create → Create**

### Parte 3 — Configurar variables de entorno en Azure

1. Ve a tu App Service → **Configuration** → **Application settings**
2. Agrega estas variables (clic en "+ New application setting" por cada una):

| Nombre | Valor |
|--------|-------|
| `DATABASE_URL` | `postgresql://visitalab_admin:TU_CONTRASEÑA@visitalab-db.postgres.database.azure.com/visitalab?sslmode=require` |
| `SECRET_KEY` | una cadena larga y aleatoria, ej: `xK9#mP2@qL5vN8wE3jR7tY1uI6oA4sD` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

3. Clic en **Save**

### Parte 4 — Subir el código desde GitHub

#### 4a. Subir a GitHub

```bash
cd visitalab
git init
git add .
git commit -m "Initial commit — VisitaLab v2"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/visitalab.git
git push -u origin main
```

#### 4b. Conectar GitHub con Azure App Service

1. En tu App Service → **Deployment Center**
2. En **Source**, selecciona **GitHub**
3. Autoriza Azure para acceder a tu cuenta GitHub
4. Selecciona:
   - **Organization**: tu usuario
   - **Repository**: visitalab
   - **Branch**: main
5. Clic en **Save**

Azure creará automáticamente un workflow de GitHub Actions (`.github/workflows/main_visitalab-app.yml`) que desplegará la app cada vez que hagas `git push`.

#### 4c. Configurar el comando de inicio

1. En App Service → **Configuration** → **General settings**
2. En **Startup Command**, ingresa:
   ```
   gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout=120 app:app
   ```
3. Clic en **Save**

### Parte 5 — Verificar el despliegue

1. Ve a App Service → **Overview** → clic en la URL (ej: `https://visitalab-app.azurewebsites.net`)
2. Deberías ver la pantalla de bienvenida de VisitaLab
3. Puedes verificar la salud de la API en: `https://visitalab-app.azurewebsites.net/api/health`

---

## Flujo de trabajo diario (una vez configurado)

```bash
# 1. Haces cambios en el código
# 2. Guardas los cambios en git
git add .
git commit -m "Descripción del cambio"
git push

# ✅ Azure detecta el push automáticamente y despliega en ~2-3 minutos
# ✅ La base de datos PostgreSQL NO se borra — los datos persisten siempre
```

---

## Seguridad importante

- **Nunca subas el archivo `.env`** al repositorio. Está en `.gitignore` por defecto.
- Las variables secretas (`DATABASE_URL`, `SECRET_KEY`) viven solo en Azure Application Settings.
- La clave de API de Anthropic se configura directamente en el navegador al usar la función de informes IA — no se almacena en el servidor.

---

## Comandos útiles

```bash
# Ver logs en tiempo real (Azure CLI)
az webapp log tail --name visitalab-app --resource-group TU_RESOURCE_GROUP

# Conectar a la BD PostgreSQL desde local
psql "postgresql://visitalab_admin:CONTRASEÑA@visitalab-db.postgres.database.azure.com/visitalab?sslmode=require"

# Exportar copia de seguridad de la BD
pg_dump "postgresql://..." > backup_$(date +%Y%m%d).sql

# Restaurar copia de seguridad
psql "postgresql://..." < backup_20260407.sql
```

---

## API Reference

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/empresas` | Listar empresas |
| POST | `/api/empresas` | Crear empresa |
| PUT | `/api/empresas/:id` | Actualizar empresa |
| DELETE | `/api/empresas/:id` | Eliminar empresa |
| GET | `/api/visitas` | Listar visitas |
| POST | `/api/visitas` | Crear visita |
| PUT | `/api/visitas/:id` | Actualizar visita |
| DELETE | `/api/visitas/:id` | Eliminar visita |
| GET | `/api/hallazgos` | Listar hallazgos |
| POST | `/api/hallazgos` | Crear hallazgo |
| GET | `/api/oportunidades` | Listar oportunidades |
| POST | `/api/oportunidades` | Crear oportunidad |
| GET | `/api/contactos` | Listar contactos |
| POST | `/api/contactos` | Crear contacto |
| GET | `/api/export` | Exportar todo como JSON |
| POST | `/api/import` | Importar desde JSON |
| DELETE | `/api/vaciar/:tabla` | Vaciar tabla (`visitas`, `empresas`, `hallazgos`, `oportunidades`, `todo`) |
| GET | `/api/health` | Estado del servidor |

---

## Persistencia de datos

Los datos se guardan en **PostgreSQL en Azure** y **nunca se borran** con los deploys:

- Cada `git push` solo actualiza el **código** de la aplicación
- La **base de datos** es independiente del App Service
- SQLAlchemy crea las tablas automáticamente si no existen al iniciar

Para proteger los datos, configura **Automated backups** en el servidor PostgreSQL de Azure (está activado por defecto con retención de 7 días).
