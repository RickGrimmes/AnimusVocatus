# Roadmap Arco 2: Evolucion de Experiencia y Modularidad (Benchmark Momentiia)

Este documento desglosa el analisis funcional y visual derivado del benchmark de **Momentiia**, estructurado como la guia maestra de evolucion tras la conclusion de los cimientos operativos (Arco 1).

---

## Prioridad Actual e Inmediata: Activacion Real de Cloudflare R2 en la Boveda

Antes de desplegar las dinamicas sociales avanzadas (notas de voz y retos), el sistema requiere la activacion y validacion integral del almacenamiento en la nube con un bucket dedicado de **Cloudflare R2**.

### Objetivos Clave de la Fase R2 (Enfoque Inmediato):
1. **Bucket Dedicado Aevum:** Creacion y configuracion del bucket independiente en Cloudflare R2 con politicas CORS completas (`PUT`, `GET`, `HEAD`).
2. **Credenciales API con Permisos de Objeto:** Generacion de token R2 (Access Key ID y Secret Access Key) con permisos de lectura y escritura exclusivos sobre el bucket.
3. **Flujo End-to-End de Subida Directa:**
   - Validacion de cuota y tipos MIME en el backend (`/api/a/{slug}/batch-presigned`).
   - Generacion de miniaturas WebP en el navegador del invitado con `OffscreenCanvas`.
   - Subida concurrente directa via `HTTP PUT` desde el navegador a Cloudflare R2 sin sobrecarga de servidor.
   - Confirmacion en base de datos (`/api/a/{slug}/media/confirm`) y refresco instantaneo en la galeria y visor Reels.
4. **Dominio Publico o URLs Prefirmadas GET:** Servir imagenes y videos a maxima velocidad con CDN global o descarga firmada temporal.
5. **Validacion del Empaquetador Masivo ZIP:** Comprobacion de lectura asincrona desde R2 para generar el archivo comprimido maestro del evento.

---

## Matriz de Estado y Fases del Arco 2

| Fase | Modulo | Estado | Descripcion Funcional |
| :--- | :--- | :--- | :--- |
| **Fase 2.0** | **Activacion & Optimizacion Cloudflare R2** | **Completado** | Bucket dedicado, firmas S3v4, URLs prefirmadas batch, Cache-Control inmutable, cola paralela (2 workers) y widget no invasivo estilo Momentiia. |
| **Fase 2.1** | Landing Comercial Premium | Completado | Hero dinamico, comparativa vs WhatsApp, cotizador en linea y mockup interactivo. |
| **Fase 2.2** | Simulador de Telefono en Vivo | Completado | Marco interactivo reactivo integrado en el panel del anfitrion (`PhoneSimulator.astro`). |
| **Fase 2.3** | Generador de Carteles QR Imprimibles | Completado | Generacion de disenos vectoriales para centros de mesa con QR y PIN listos para imprenta (`/admin/print/[slug]`). |
| **Fase 2.4** | **Dock Bar Movil + Notas de Voz** | **SIGUIENTE** | Barra de navegacion inferior fija de 5 accesos en `/a/[slug]`, grabador de audio web con ondas de audio y libro de firmas. |
| **Fase 2.5** | Carpetas y Momentos del Evento | Pendiente | Agrupacion de recuerdos por fases (Civil, Ceremonia, Recepcion, Fiesta) en la boveda y panel. |
| **Fase 2.6** | Retos Fotograficos Gamificados | Pendiente | Lista de misiones interactivas para invitados ("Foto con los novios", "El mejor baile") con contador de retos cumplidos. |
| **Fase 2.7** | Dashboard Central del Anfitrion | Pendiente | Vista consolidada `/dashboard` con barra de progreso de configuracion global (8 de 9 pasos) y selector de eventos. |

---

## Detalle Funcional de los Modulos Pendientes

### 1. Dock Bar Movil y Notas de Voz (Fase 2.4)
- **Barra de Navegacion Inferior Fija:**
  - Acceso 1: Inicio (cuenta regresiva, portada y bienvenida).
  - Acceso 2: Album (galeria fluida filtrable por fotos, videos y audios).
  - Acceso 3: Boton central de carga rapida (+ destacado con indicador de progreso).
  - Acceso 4: Dedicatorias (libro de firmas de texto escrito por los invitados).
  - Acceso 5: Notas de voz (grabacion de felicitaciones desde el navegador).
- **Grabadora de Audio en Navegador:**
  - Uso de `MediaRecorder API` para captura de audio en formato WebM/Opus o AAC/M4A.
  - Generador de visualizacion de ondas (*waveform*) en tiempo real.
  - Subida directa a Cloudflare R2 bajo el prefijo `events/{slug}/audio/`.

### 2. Carpetas y Momentos (Fase 2.5)
- Clasificacion dinamica de recuerdos:
  - Selector superior de momentos configurables por el anfitrion (ej. "Preparativos", "Ceremonia", "Banquete", "Fiesta").
  - Filtrado instantaneo tanto en la vista de invitado como en la consola de moderacion.

### 3. Retos Fotograficos (Fase 2.6)
- Gamificacion de la fiesta:
  - Tarjetas de reto con instrucciones claras y boton directo de captura.
  - Insignia de reto cumplido en la galeria y acumulador de progreso general del evento.
