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

## Arquitectura de Negocio: 3 Areas en 1 Solo Proyecto

No se requieren tres repositorios ni proyectos separados. La suite centraliza toda la operacion en este unico monorepo:

```
                                 PLATAFORMA VOCATUS & ANIMUS
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
1. LANDING COMERCIAL                2. PANEL ADMINISTRATIVO             3. PRODUCTO MODULAR
   Ruta: /                             Ruta: /admin                        Rutas: /v y /a
   • Captacion de clientes             • Superadmin (Tu operacion):        • Vocatus: Invitacion
   • Demos interactivos                  cotizaciones, alta de eventos,      con confirmacion RSVP
   • Cotizador en linea                  activacion de modulos y cuotas.   • Animus: Boveda QR/PIN,
   • Portafolio de plantillas          • Anfitrion (Tus clientes):           galeria tipo telefono
                                         metricas RSVP, moderacion de        y reproductor Reels
                                         fotos y descarga ZIP.
```

### Desacoplamiento de Modulos (Venta Flexible)
Cada evento es 100% independiente con su propio `slug` y puede contratarse en tres modalidades:

1. **Solo Vocatus (Invitaciones & RSVP):** Para eventos que solo requieren logistica e invitacion digital. Se desactiva la boveda Animus y no se muestra el banner de fotos.
2. **Solo Animus (Boveda de Recuerdos & Reels):** Para graduaciones, cumpleanos o bodas donde ya entregaron invitaciones fisicas. Se entrega unicamente el codigo QR y PIN de mesa para subir fotos y videos.
3. **Suite Completa (Vocatus + Animus):** Ambos modulos activos y sincronizados en el tiempo (*Time-Aware Routing*).

### Motor de Plantillas Dinamicas (Theme Engine)
Para evitar crear un proyecto de codigo por cada cliente, el sistema utiliza un **motor de plantillas dinamicas**:
* **Mismo motor de datos:** Todos los eventos usan la misma API y base de datos (itinerario, pases, almacenamiento).
* **Piel visual configurable:** En base de datos cada evento guarda su `template_id` y su `theme_config`:
  - `editorial_minimalist`: Bodas elegantes y sobrias (tipografia serif clasica, fondo crema, detalles dorados o negros).
  - `gold_luxury`: XV anos y aniversarios de gala (acentos dorados, brillos, video de bienvenida).
  - `party_neon`: Cumpleanos y fiestas de noche (modo oscuro, colores vivos, enfoque en la fiesta).
  - `botanical_soft`: Bautizos y primeras comuniones (tonos pastel, acuarelas florales suaves).
  - `academic_gala`: Graduaciones y galas corporativas.
* **Soporte VIP a la medida:** Si un cliente contrata un desarrollo 100% artesanal y exclusivo, Astro permite crear una pagina dedicada dentro del mismo proyecto (por ejemplo `src/pages/v/boda-vip.astro`) sin clonar repositorios ni alterar a otros clientes.

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
| **Frontend** | **Astro + Tailwind CSS** | Serverless / Edge rendering para carga ultrarrapida en moviles |
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
│   ├── web/                        # Frontend en Astro (Edge Ready)
│   │   └── src/
│   │       ├── components/         # RSVPModal, PinGate, GalleryGrid, ReelsViewer, UploaderModal
│   │       ├── layouts/            # Layout.astro (temas dark y editorial)
│   │       ├── pages/
│   │       │   ├── index.astro     # Landing comercial y portal de acceso
│   │       │   ├── v/[slug].astro  # Invitacion Vocatus con cuenta regresiva y RSVP
│   │       │   ├── a/[slug].astro  # Boveda Animus con galeria tipo telefono y Reels
│   │       │   ├── live/[slug].astro # Proyeccion en vivo (Live Wall)
│   │       │   └── admin/          # Panel de administracion y cotizaciones
│   │       └── lib/                # Clientes API y generador de miniaturas en cliente
│   │
│   └── api/                        # Backend (FastAPI + Python 3.12)
│       └── app/
│           ├── routers/            # auth, events, rsvp, vault, admin
│           └── services/           # storage (Cloudflare R2), mailer, zip_packager
│
├── .agents/                        # Reglas y skills locales (instagram-media-experience)
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

### 2. Base de Datos Local
Para levantar PostgreSQL 16 con Docker:
```bash
docker compose up -d db
```

### 3. Levantar Backend y Frontend en Desarrollo
```bash
# Terminal 1 - Backend FastAPI
python -m uvicorn app.main:app --app-dir apps/api --reload --port 8000

# Terminal 2 - Frontend Astro
cd apps/web
npm run dev
```

---

## Hoja de Ruta (Roadmap)

- [x] **Fase 0:** Especificacion tecnica y definicion de contratos de API ([VOCATUS_ANIMUS_SPEC.md](file:///c:/Users/babaj/Documents/Yo/ANIMUS-VOCATUS/VOCATUS_ANIMUS_SPEC.md)).
- [x] **Fase 1:** Inicializacion de estructura base del monorepo (`apps/web`, `apps/api`) y documentacion central.
- [x] **Fase 2:** Modelado de datos en SQLAlchemy 2.0 y migraciones Alembic (User, Event, RSVPGuest, MediaItem, ZipJob).
- [x] **Fase 3:** Core API Vocatus (Endpoints publicos de invitacion, busqueda y confirmacion RSVP con conteo de pases).
- [x] **Fase 4:** Core API Animus (Validacion de PIN de 4 digitos, JWT efimero y generacion batch de URLs prefirmadas R2).
- [x] **Fase 5:** Frontend Invitados (Vistas mobile-first `/v/[slug]` y `/a/[slug]` con carga directa, galeria tipo telefono y visor estilo Reels).
- [x] **Fase 6:** Live Wall (`/live/[slug]`) con polling/refresco en pantalla completa para proyectores.
- [x] **Fase 7:** Empaquetador masivo ZIP asincrono y notificaciones por correo via Resend.
- [ ] **Fase 8:** Panel de Administracion & Cotizador (`/admin`) — Gestion de superadmin para cotizar y crear eventos + Dashboard para el anfitrion (metricas en vivo, moderacion de fotos y generador de plantillas QR).
- [ ] **Fase 9:** Landing Page Comercial & Captacion (`/`) — Vitrina de venta de alto impacto para clientes finales, cotizador interactivo en linea y demostraciones en vivo.

### Proximo Arco: Evolucion Visual & Experiencia VIP (Arco 2)
Una vez concluidas las 9 fases fundacionales, se activara el **Arco 2 ("Hacerlo Guapo")** inspirado en las mejores practicas de la industria (Momentiia): simulador de telefono en vivo, notas de voz, retos fotograficos, organizacion por carpetas y generador de carteles de mesa. El desglose completo se encuentra documentado en [ROADMAP_ARCO_2_MOMENTIIA.md](file:///c:/Users/babaj/Documents/Yo/ANIMUS-VOCATUS/ROADMAP_ARCO_2_MOMENTIIA.md).

---

## Especificacion Tecnica Detallada

Para consultar el modelo de datos relacional (Mermaid ERD), diagramas de secuencia, lista blanca de tipos MIME, limites por paquete comercial y contratos OpenAPI, revisa el archivo [VOCATUS_ANIMUS_SPEC.md](file:///c:/Users/babaj/Documents/Yo/ANIMUS-VOCATUS/VOCATUS_ANIMUS_SPEC.md).
