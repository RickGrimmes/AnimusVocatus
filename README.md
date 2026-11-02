# Aevum

> **Suite Web Integral para Eventos Sociales de Alta Gama**  
> *Aevum (latín): La era, el tiempo sin fin o la eternidad. La preservación del momento presente y del recuerdo perdurable.*

---

## 1. Visión General del Proyecto

**Aevum** es una plataforma tecnológica concebida para digitalizar, optimizar y elevar la experiencia de eventos sociales exclusivos (bodas, XV años, aniversarios, galas y graduaciones), bajo una dirección de diseño sobria, editorial y de alta usabilidad (*Industrial / Editorial Minimalist*).

El sistema resuelve la fragmentación tradicional de los eventos sociales (donde las invitaciones se envían en formatos estáticos, las fotos se pierden en grupos de mensajería con compresión destructiva y los anfitriones carecen de métricas centralizadas) unificando todo el ciclo de vida en una única arquitectura monorepo.

### Identidad Visual y Tipografía
- **Isotipo Oficial:** `[AE]` entre corchetes.
- **Tipografía de Marca:** `Bodoni Moda SC` (Google Fonts). Obligatoria para la marca **Aevum** y su isotipo `[AE]`.
- **Tipografías de Soporte:** `Playfair Display` para encabezados editoriales, `Faculty Glyphic` y `Roboto` para cuerpo de texto, y `Space Mono` para credenciales, códigos PIN y datos técnicos.
- **Estilo:** Paletas crema cálido (`#faf6ed`), grafito profundo (`#0f0f11`), acentos dorados sutiles y transparencias en vidrio satinado (*glassmorphism*).

---

## 2. Los 4 Pilares Fundamentales del Sistema

La arquitectura de **Aevum** está estructurada formalmente en cuatro pilares complementarios pero funcionalmente desacoplados:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                PLATAFORMA AEVUM                                  │
├────────────────────┬────────────────────┬───────────────────┬────────────────────┤
│    PILAR 1         │    PILAR 2         │    PILAR 3        │    PILAR 4         │
│ LANDING COMERCIAL  │  INVITACIONES Y    │ BÓVEDA DE RECUERDOS│ PANEL DE CONTROL   │
│   Y CAPTACIÓN      │    RSVP (VOCATUS)  │ Y REELS (ANIMUS)  │ Y ADMINISTRACIÓN   │
│   Ruta: /          │   Ruta: /v/[slug]  │ Ruta: /a/[slug]   │ Ruta: /admin       │
└────────────────────┴────────────────────┴───────────────────┴────────────────────┘
```

### Pilar 1: Landing Comercial y Portal de Captación (`/`)
Es la vitrina pública de cara al mercado y a clientes potenciales. Diseñada para educar, generar confianza y convertir visitas en contrataciones.
- **Hero Interactivo:** Titular dinámico con rotación de eventos y presentación de la propuesta de valor.
- **Sección Antítesis de WhatsApp:** Comparativa directa frente a métodos tradicionales (pérdida de calidad, caos organizativo, aplicaciones nativas que nadie instala).
- **Simulador Interactivo con QR en Vivo:** Demostración en tiempo real dentro de un marco de smartphone navegable que permite al visitante escanear el QR con su propio móvil y probar la experiencia de inmediato.
- **Cotizador en Línea:** Calculadora interactiva de presupuestos basada en número de invitados, almacenamiento y módulos requeridos.
- **Portafolio y Muestrario de Plantillas:** Presentación de estilos visuales adaptables por temática de evento.

### Pilar 2: Invitaciones Digitales y Control RSVP - Vocatus (`/v/[slug]`)
Módulo pre-evento enfocado en la logística, comunicación y confirmación de asistencia inteligente.
- **Experiencia Inmersiva:** Portada editorial personalizada, cuenta regresiva en tiempo real y detalles del protocolo.
- **Logística Completa:** Itinerarios con hitos horarios, código de vestimenta con guía de colores, enlaces directos a Google Maps / Waze y mesa de regalos con datos bancarios / enlaces comerciales.
- **Sistema RSVP Inteligente:** Búsqueda predictiva del invitado por nombre o pase familiar, validación estricta de boletos asignados vs. confirmados, restricciones dietéticas (alergias, menú infantil, vegetariano) y dedicatorias de felicitación.
- **Enrutamiento Consciente del Tiempo (Time-Aware):** El enlace muta el día del evento mostrando un banner de acceso directo a la subida de fotos, y post-evento redirige al agradecimiento y descarga.

### Pilar 3: Bóveda Colaborativa de Fotos y Videos - Animus (`/a/[slug]`)
Módulo activo durante la fiesta y en la fase post-evento para recopilar recuerdos espontáneos en calidad original.
- **Acceso Cero Fricción:** Acceso instantáneo mediante escaneo de código QR en centros de mesa con validación automática vía PIN de 4 dígitos. Sin registros de usuario ni descargas de tiendas de apps.
- **Subida Directa a Almacenamiento (Zero Server Load):** Carga masiva de fotos y videos directamente a Cloudflare R2 mediante URLs prefirmadas en lote (`batch-presigned`), preservando el ancho de banda y la CPU del servidor central.
- **Miniaturas en Cliente (Client-Side Canvas):** Procesamiento y compresión WebP ejecutados localmente en el navegador del invitado mediante `OffscreenCanvas` antes de subir (~40ms por imagen).
- **Visor Inmersivo Estilo Reels / Stories:** Reproductor vertical a pantalla completa con navegación táctil fluida, indicador de autor y contador de favoritos.
- **Muro en Vivo (Live Wall - `/live/[slug]`):** Vista optimizada para pantallas gigantes y proyectores del salón de eventos, con refresco automático de fotos aprobadas y código QR persistente en esquina.

### Pilar 4: Panel Administrativo y de Gestión (`/admin` y `/admin/[slug]`)
Consola centralizada tanto para el superadministrador como para los anfitriones del evento.
- **Visión General y Métricas:** Control de días restantes, balance de almacenamiento en tiempo real (bytes usados vs. contratados) y resumen de confirmaciones RSVP.
- **Simulador de Smartphone en Vivo (`PhoneSimulator.astro`):** Vista previa reactiva que permite al anfitrión verificar cómo ven sus invitados el álbum en dispositivos móviles.
- **Curaduría y Moderación en Vivo:** Aprobación, ocultación o destacado de fotografías y videos subidos por los invitados antes de proyectarse en el Live Wall.
- **Generador de Carteles de Mesa para Imprenta (`/admin/print/[slug]`):** Herramienta que genera de forma automática los diseños en tamaño estándar con código QR vectorial y PIN de 4 dígitos, listos para enviar a corte e imprenta física.
- **Empaquetador Masivo ZIP:** Generación asíncrona en segundo plano del archivo maestro de recuerdos en máxima resolución para entrega formal al anfitrión.

---

## 3. Topología de Infraestructura y Pila Tecnológica

| Componente | Tecnología | Justificación y Función |
| :--- | :--- | :--- |
| **Arquitectura de Código** | Monorepo (`apps/web` + `apps/api`) | Sincronización atómica de modelos de datos, contratos API e interfaz. |
| **Frontend de Invitados y Admin** | Astro + Vanilla CSS / Tailwind | Generación estática y renderizado en el borde (Edge), carga en < 1s sobre redes móviles con baja cobertura. |
| **Backend Core** | FastAPI (Python 3.12) | Asincronismo de alto rendimiento, validación con Pydantic v2 y firma de URLs S3. |
| **Base de Datos** | PostgreSQL 16 | Almacenamiento relacional estricto para eventos, pases RSVP y metadatos de archivos. |
| **Almacenamiento de Archivos** | Cloudflare R2 | Compatibilidad nativa con S3 API con cero costos de egreso de datos ($0/GB egress). |
| **Miniaturas** | OffscreenCanvas (Navegador) | Generación de thumbnails WebP del lado del cliente para eliminar consumo de CPU en servidor. |
| **Correos Transaccionales** | Resend API | Envío de notificaciones de confirmación de asistencia y enlace de entrega del ZIP maestro. |
| **Contenedores** | Docker y Docker Compose | Orquestación local homogénea para base de datos y backend. |

---

## 4. Estructura del Monorepo

```text
ANIMUS-VOCATUS/
├── apps/
│   ├── web/                              # Frontend Edge (Astro)
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── GalleryGrid.astro     # Cuadrícula fluida de medios estilo móvil
│   │   │   │   ├── LiveWallOverlay.astro # Capa de proyección para salones
│   │   │   │   ├── PhoneSimulator.astro  # Marco de smartphone interactivo
│   │   │   │   ├── PinGate.astro         # Puerta de autenticación por PIN
│   │   │   │   ├── ReelsViewer.astro     # Reproductor inmersivo vertical
│   │   │   │   ├── RSVPModal.astro       # Flujo interactivo de pases y dedicatorias
│   │   │   │   └── UploaderModal.astro   # Gestor de subida con Canvas WebP
│   │   │   ├── layouts/
│   │   │   │   └── Layout.astro          # Layout base con tipografías y metas
│   │   │   ├── pages/
│   │   │   │   ├── index.astro           # Pilar 1: Landing comercial y vitrina
│   │   │   │   ├── v/[slug].astro        # Pilar 2: Invitación y RSVP (Vocatus)
│   │   │   │   ├── a/[slug].astro        # Pilar 3: Bóveda colaborativa (Animus)
│   │   │   │   ├── live/[slug].astro     # Extensión Pilar 3: Muro en vivo
│   │   │   │   └── admin/                # Pilar 4: Panel administrativo
│   │   │   │       ├── index.astro       # Selector y métricas generales
│   │   │   │       ├── [slug].astro      # Gestión del evento y moderación
│   │   │   │       └── print/
│   │   │   │           └── [slug].astro  # Carteles QR para imprenta
│   │   │   └── lib/                      # Cliente API y generador de thumbnails
│   │   ├── package.json
│   │   └── tailwind.config.cjs
│   │
│   └── api/                              # Backend Core (FastAPI)
│       ├── app/
│       │   ├── config.py                 # Configuración por variables de entorno
│       │   ├── database.py               # Motor SQLAlchemy 2.0 y sesiones
│       │   ├── models.py                 # Entidades User, Event, RSVP, Media, ZipJob
│       │   ├── schemas.py                # Validaciones Pydantic v2
│       │   ├── routers/
│       │   │   ├── auth.py               # Sesiones de anfitrión y PIN de acceso
│       │   │   ├── events.py             # Consulta y configuración de eventos
│       │   │   ├── rsvp.py               # Búsqueda y confirmación de pases
│       │   │   ├── vault.py              # URLs prefirmadas batch y feed de medios
│       │   │   └── admin.py              # Moderación, métricas y trigger ZIP
│       │   ├── services/
│       │   │   ├── storage.py            # Firma de URLs Cloudflare R2 con boto3
│       │   │   ├── mailer.py             # Integración con Resend
│       │   │   └── zip_packager.py       # Empaquetado asíncrono en ZIP
│       │   └── main.py                   # Inicialización y middlewares CORS
│       ├── Dockerfile
│       └── requirements.txt
│
├── .agents/                              # Reglas y habilidades de los agentes
│   ├── rules/
│   │   └── no-emojis.md                  # Regla obligatoria: Cero emojis
│   └── skills/
│       └── instagram-media-experience/   # Directrices de UX inmersiva
├── docker-compose.yml                    # Postgres y API para desarrollo local
├── .env.example                          # Plantilla de variables de entorno
├── AGENTS.md                             # Protocolos de conducta y estilo
├── ROADMAP_ARCO_2_MOMENTIIA.md           # Plan de evolución y benchmark
├── VOCATUS_ANIMUS_SPEC.md                # Especificación técnica maestra
└── README.md                             # Documento raíz del proyecto
```

---

## 5. Guía de Puesta en Marcha (Instalación Local)

### Paso 1: Configurar Variables de Entorno
Copia la plantilla de variables de entorno en la raíz:
```bash
cp .env.example .env
```

### Paso 2: Iniciar Base de Datos Local
Inicia el contenedor de PostgreSQL 16:
```bash
docker compose up -d db
```

### Paso 3: Levantar el Backend (FastAPI)
Desde un entorno virtual con Python 3.12:
```bash
pip install -r apps/api/requirements.txt
python -m uvicorn app.main:app --app-dir apps/api --reload --port 8000
```
La documentación interactiva de la API estará disponible en `http://localhost:8000/docs`.

### Paso 4: Levantar el Frontend (Astro)
En otra terminal:
```bash
cd apps/web
npm install
npm run dev
```
La aplicación web se ejecutará en `http://localhost:4321`.

---

## 6. Estado del Desarrollo y Hoja de Ruta

### Arco 1: Cimientos Operativos (Completado)
- **Fase 0:** Especificación técnica integral y contratos OpenAPI.
- **Fase 1:** Configuración inicial del monorepo y contenedor de base de datos.
- **Fase 2:** Esquema relacional con SQLAlchemy 2.0 y soporte multi-evento.
- **Fase 3:** API de Vocatus con búsqueda inteligente de pases y confirmación RSVP.
- **Fase 4:** API de Animus con validación de PIN y URLs prefirmadas R2 en lote.
- **Fase 5:** Vistas web `/v/[slug]` y `/a/[slug]` con visor vertical Reels y miniaturas Canvas.
- **Fase 6:** Live Wall (`/live/[slug]`) con rotación en pantalla completa para proyectores.
- **Fase 7:** Servicio asíncrono de empaquetado masivo ZIP y entrega transaccional por correo.
- **Fase 8:** Panel de control de anfitrión (`/admin`) con métricas de almacenamiento y moderación.
- **Fase 9:** Landing comercial interactiva (`/`) con cotizador en línea y demostración en vivo.

### Arco 2: Evolución de Experiencia (En Curso)
- **Activación y Optimización de Cloudflare R2:** Bucket dedicado enlazado, firmas S3v4, URLs prefirmadas en lote y cabeceras `Cache-Control: public, max-age=31536000, immutable` para caché perimetral permanente.
- **Subida en Segundo Plano Estilo Momentiia:** Carga no invasiva con banner superior, tarjeta flotante de progreso en esquina inferior derecha, cola concurrente de 2 trabajadores en paralelo y persistencia de autor/modo anónimo por 6 horas.
- **Simulador de Smartphone en Panel:** Incorporado en el panel administrativo (`PhoneSimulator.astro`).
- **Carteles de Mesa para Imprenta:** Generador dinámico listo para impresión física (`/admin/print/[slug]`).
- **Próximos pasos:** Barra inferior fija (Dock Bar) de 5 accesos, libro de firmas y dedicatorias de texto, grabadora web de notas de voz con visualizador de ondas y retos fotográficos de la fiesta.

---

## 7. Documentación Complementaria

- [VOCATUS_ANIMUS_SPEC.md](file:///c:/Users/babaj/Documents/Yo/ANIMUS-VOCATUS/VOCATUS_ANIMUS_SPEC.md): Especificación técnica exhaustiva, esquemas ERD, flujos de autenticación y límites de almacenamiento.
- [ROADMAP_ARCO_2_MOMENTIIA.md](file:///c:/Users/babaj/Documents/Yo/ANIMUS-VOCATUS/ROADMAP_ARCO_2_MOMENTIIA.md): Análisis funcional comparativo y módulos de gamificación.
- [AGENTS.md](file:///c:/Users/babaj/Documents/Yo/ANIMUS-VOCATUS/AGENTS.md): Reglas de estilo y directrices obligatorias de comunicación para el desarrollo.
