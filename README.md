# Vocatus & Animus

> **Suite Web para Eventos Sociales de Alta Gama**  
> *Invitaciones interactivas (RSVP) + Boveda colaborativa de recuerdos fotograficos en calidad original.*

---

## Vision General

**Vocatus & Animus** es un Micro-SaaS concebido para digitalizar y simplificar el ciclo de vida completo de eventos sociales exclusivos (bodas, XV anos, aniversarios, galas y graduaciones), bajo una linea visual sobria, moderna y de alta usabilidad (*Industrial / Editorial Minimalist*).

El sistema desacopla la experiencia en dos momentos clave:

1. **Vocatus ("El Llamado") - Fase Pre-Evento**
   - Invitacion web interactiva y personalizada (`/v/[slug]`).
   - Confirmacion de asistencia inteligente (**RSVP**) con control estricto de pases por invitado/familia.
   - Itinerario interactivo, codigo de vestimenta, mesa de regalos y enlaces GPS directos a Google Maps y Waze.
   - Cuenta regresiva dinamica y recordatorios.

2. **Animus ("La Memoria") - Fase en Vivo y Post-Evento**
   - Boveda de fotos y videos colaborativa (`/a/[slug]`) sin requerir descarga de apps ni registro de usuarios.
   - **Acceso sin friccion:** Escaneo de codigo **QR** en centros de mesa con **PIN de 4 digitos** embebido o manual.
   - **Subida directa cliente-a-almacenamiento:** Subida via URLs prefirmadas a **Cloudflare R2** ($0 costo por transferencia/egreso), sin saturar el servidor central.
   - **Miniaturas instantaneas en cliente:** Compresion y generacion de thumbnails WebP con `OffscreenCanvas` en el navegador del invitado (~40ms).
   - **Muro en Vivo (Live Wall):** Vista de proyeccion a pantalla completa (`/live/[slug]`) con actualizacion automatica para pantallas en la fiesta.
   - **Empaquetado ZIP Masivo:** Descarga completa asincrona de 10 a 50 GB enviada por correo al anfitrion.
   - **Purga programada a 60 dias:** Ciclo de vida sustentable con reglas automaticas de expiracion en R2 y base de datos.

---

## Flujo de Usuario y Enrutamiento Dinamico (Time-Aware)

El enlace principal compartido con los invitados se adapta automaticamente segun la fecha del evento:

```
┌─────────────────────────────────┐      ┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│        1. ANTES DEL EVENTO      │      │        2. EL DIA DE LA FIESTA   │      │        3. DIAS POSTERIORES      │
│         /v/[evento-slug]        │ ───► │         /a/[evento-slug]        │ ───► │         /v/[evento-slug]        │
├─────────────────────────────────┤      ├─────────────────────────────────┤      ├─────────────────────────────────┤
│ • Invitacion formal             │      │ • QR fisico en mesas con PIN    │      │ • Agradecimiento automatico     │
│ • Formulario RSVP de pases      │      │ • Carga masiva de fotos y clips │      │ • Acceso a la galeria de fotos  │
│ • Ubicacion GPS e itinerario    │      │ • Proyeccion en Live Wall       │      │ • Generacion de ZIP descargable │
└─────────────────────────────────┘      └─────────────────────────────────┘      └─────────────────────────────────┘
```

---

## Stack Tecnologico

| Capa | Tecnologia | Proposito |
| :--- | :--- | :--- |
| **Arquitectura** | **Monorepo** | Unificacion de cliente y API con despliegues independientes |
| **Frontend** | **Astro / Next.js + Tailwind CSS** | Serverless / Edge rendering para carga ultrarrapida en moviles |
| **Backend API** | **FastAPI (Python 3.12)** | Asincronismo, validacion Pydantic v2 y firma criptografica S3 |
| **Base de Datos** | **PostgreSQL 16** | Modelo relacional para eventos, boletos RSVP y metadatos de media |
| **Almacenamiento** | **Cloudflare R2** | Almacenamiento compatible con S3 sin costos de transferencia ($0 egress) |
| **Procesamiento** | **Canvas API / OffscreenCanvas** | Generacion de miniaturas del lado del cliente sin costo de CPU servidor |
| **Correos** | **Resend API** | Notificaciones transaccionales y entrega del ZIP de recuerdos |
| **Contenedores** | **Docker & Docker Compose** | Entorno local consistente para base de datos y backend |

---

## Estructura del Proyecto

```text
ANIMUS-VOCATUS/
├── apps/
│   ├── web/                        # Frontend (Astro / Next.js)
│   │   └── src/
│   │       ├── components/         # Componentes UI (RSVP, Uploader, LiveWall, etc.)
│   │       ├── pages/
│   │       │   ├── v/              # Modulo Vocatus: /v/[slug] (Invitacion & RSVP)
│   │       │   ├── a/              # Modulo Animus: /a/[slug] (Boveda de Invitados)
│   │       │   ├── live/           # Muro en Vivo: /live/[slug] (Proyeccion)
│   │       │   └── admin/          # Panel de anfitrion y moderacion
│   │       └── lib/                # Clientes API, helpers y generador de thumbnails
│   │
│   └── api/                        # Backend (FastAPI + Python 3.12)
│       └── app/
│           ├── routers/            # Endpoints: events, rsvp, vault, admin, auth
│           └── services/           # Servicios: storage (R2), mailer, zip_packager
│
├── .agents/                        # Reglas y configuraciones locales de agentes
├── .env.example                    # Plantilla de variables de entorno
├── docker-compose.yml              # Orquestacion local (PostgreSQL + API)
├── VOCATUS_ANIMUS_SPEC.md          # Especificacion tecnica maestra y contratos de API
└── README.md                       # Documentacion principal del proyecto
```

---

## Puesta en Marcha (Primeros Pasos)

### 1. Variables de Entorno
Copia el archivo de ejemplo para configurar tus credenciales locales:
```bash
cp .env.example .env
```

Configura en tu `.env`:
- Conexion a PostgreSQL (`DATABASE_URL`).
- Credenciales de Cloudflare R2 (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`).
- API Key de Resend (`RESEND_API_KEY`) para correos.
- Claves de firma JWT (`SECRET_KEY`).

### 2. Base de Datos Local
Para levantar PostgreSQL 16 con Docker:
```bash
docker compose up -d db
```

---

## Hoja de Ruta (Roadmap)

- [x] **Fase 0:** Especificacion tecnica y definicion de contratos de API ([VOCATUS_ANIMUS_SPEC.md](file:///c:/Users/babaj/Documents/Yo/ANIMUS-VOCATUS/VOCATUS_ANIMUS_SPEC.md)).
- [x] **Fase 1:** Inicializacion de estructura base del monorepo (`apps/web`, `apps/api`) y documentacion central.
- [x] **Fase 2:** Modelado de datos en SQLAlchemy 2.0 y migraciones Alembic (User, Event, RSVPGuest, MediaItem, ZipJob).
- [x] **Fase 3:** Core API Vocatus (Endpoints publicos de invitacion, busqueda y confirmacion RSVP con conteo de pases).
- [ ] **Fase 4:** Core API Animus (Validacion de PIN de 4 digitos, JWT efimero y generacion batch de URLs prefirmadas R2).
- [ ] **Fase 5:** Frontend Invitados (Vistas mobile-first `/v/[slug]` y `/a/[slug]` con carga directa y miniaturas en cliente).
- [ ] **Fase 6:** Live Wall (`/live/[slug]`) con polling/refresco en pantalla completa.
- [ ] **Fase 7:** Empaquetador masivo ZIP asincrono y notificaciones por correo via Resend.
- [ ] **Fase 8:** Panel de Administracion para anfitriones (metricas, moderacion de fotos y descarga de tarjetas QR).

---

## Especificacion Tecnica Detallada

Para consultar el modelo de datos relacional (Mermaid ERD), diagramas de secuencia, lista blanca de tipos MIME, limites por paquete comercial y contratos OpenAPI, revisa el archivo [VOCATUS_ANIMUS_SPEC.md](file:///c:/Users/babaj/Documents/Yo/ANIMUS-VOCATUS/VOCATUS_ANIMUS_SPEC.md).
