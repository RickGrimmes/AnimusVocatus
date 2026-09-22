# Roadmap Arco 2: Evolucion de Experiencia y Modularidad (Benchmark Momentiia)

Este documento desglosa el analisis funcional y visual derivado del benchmark de **Momentiia**, estructurado como la guia maestra para el **Arco 2** ("Hacerlo Guapo") una vez concluido el despliegue del Arco 1 (Fases 1 a 9).

---

## 1. Landing Page Comercial (Vitrina de Alta Conversion)

### A. Composicion Estetica
- **Paleta de Color:** Fondo crema calido (`#faf6ed` a `#ffffff`) con acentos dorados editoriales y tipografia serif clasica de alto contraste.
- **Micro-interacciones:** Iconos flotantes organicos (camara, corazon, nota) con animacion sutil de flotacion.
- **Copy Dinamico:** Titular interactivo con rotacion de tipos de evento:
  *"Todas las fotos de tu [boda / graduacion / XV anos / cumpleanos / aniversario] en un solo lugar"*.

### B. Seccion Comparativa "Antitesis de WhatsApp"
- Argumento de venta central:
  - *WhatsApp:* fotos comprimidas, se pierden en el chat, requieren pedir fotos una por una.
  - *Otras apps:* obligan a registrarse y los invitados mayores no las usan.
  - *Animus:* cero registros, escaneo QR instantaneo, calidad original, notas de voz y dedicatorias en una sola boveda.
- Cuadricula de 6 pilares de valor:
  1. Invitados sin registro previo.
  2. Album privado y exclusivo por QR / PIN.
  3. Soporte de fotos y videos en calidad original.
  4. Interfaz intuitiva para cualquier edad.
  5. Cero instalaciones de apps nativas.
  6. Preservacion de metadatos y calidad sin compresion destructiva.
- **Mockup Interactivo en Vivo:** Telefono en pantalla con simulacion interactiva y QR para que el visitante de la landing lo escanee con su celular y viva la demo en tiempo real.

---

## 2. Experiencia del Invitado (Web App Movil)

### A. Cabecera y Portada
- Banner hero con fotografía de los anfitriones y degradado suave hacia el fondo crema.
- Titulo del evento en serif elegante, fecha y contador total de recuerdos.
- Filtro rapido de contenidos (todas, fotos, videos, audios).

### B. Barra de Navegacion Flotante Inferior (Dock Bar)
Estructura de 5 accesos directos:
1. **Inicio:** Cuenta regresiva del gran dia, informacion clave y bienvenida.
2. **Album:** Cuadricula fluida de fotos y videos con recuento de favoritos.
3. **Subir (+ Prominente):** Boton circular central de carga rapida con indicador toast de subida en segundo plano.
4. **Libro de Firmas / Mensajes:** Muro de dedicatorias de texto escritas por los invitados.
5. **Notas de Voz:** Grabadora de audio en el navegador para dejar felicitaciones de voz con reproductor de ondas (*waveform*).

---

## 3. Panel de Administracion del Anfitrion (Dashboard VIP)

### A. Pantalla Principal del Dashboard (`/dashboard`)
- Saludo personalizado: *"Hola, [Nombre]. Esto es lo que tienes entre manos."*
- Tarjeta de Proximo Evento:
  - Foto de portada, dias restantes con contador regresivo.
  - Barra de progreso de configuracion: *"8 de 9 pasos listos (89%)"*.
  - Estado de cuenta / suscripcion.
- Tarjetas de Metricas Rapidas:
  - Total de albumes activos.
  - Fotos y videos guardados.
  - Mensajes y notas de voz recibidos.
- Acciones Rapidas:
  - Crear un nuevo album.
  - Ver y gestionar albumes.
  - Descargar carteles para mesa.
  - Vista previa interactiva ("Ver como invitado").

### B. Panel Detallado por Evento (`/dashboard/events/[id]`)
Menu lateral modular especializado:
1. **Resumen:**
   - Contador regresivo en tiempo real (dias, horas, minutos, segundos).
   - Textos y citas inspiracionales configurables para el gran dia.
   - Simulador en vivo (*Phone Mockup Frame*): muestra en tiempo real en la columna derecha como ven los invitados el album segun los cambios del anfitrion.
2. **Fotos y Carpetas:**
   - Organizacion de fotos por momentos o carpetas (ej. Civil, Ceremonia, Fiesta, Tornaboda).
3. **Retos Fotograficos:**
   - Dinamica de gamificacion para la fiesta (ej. "Foto con los novios", "El mejor paso de baile", "El invitado mejor vestido").
4. **Libro de Firmas:**
   - Moderacion y lectura de todas las dedicatorias y mensajes de texto dejados por los asistentes.
5. **Apariencia & Plantillas:**
   - Seleccion de temas visuales (crema editorial, oscuro fiesta, minimalista dorado, etc.), fuentes y colores.
6. **Generador de Carteles de Mesa:**
   - Herramienta para descargar plantillas PDF listas para imprimir con el QR del evento y PIN de mesa integrado.
7. **Personas & Moderacion:**
   - Gestion de anfitriones, colaboradores con permisos de moderacion y bloqueo de contenido no deseado.
8. **Configuracion:**
   - Almacenamiento, limite de dias, descargas masivas ZIP y reglas de privacidad.

---

## 4. Matriz de Fases del Arco 2 (Plan Futuro)

| Fase Arco 2 | Modulo | Descripcion Funcional |
| :--- | :--- | :--- |
| **Fase 2.1** | Landing Comercial Premium | Hero interactivo con copy dinamico, comparativa WhatsApp y demo con QR en vivo. |
| **Fase 2.2** | Dock Bar Movil + Notas de Voz | Barra de 5 accesos en `/a/[slug]`, grabador de audio web con ondas y libro de dedicatorias. |
| **Fase 2.3** | Dashboard Central del Anfitrion | Home del panel con barra de progreso (8 de 9 pasos), tarjetas de metricas y accesos rapidos. |
| **Fase 2.4** | Simulador de Telefono en Vivo | Preview interactivo en tiempo real integrado en el panel del anfitrion. |
| **Fase 2.5** | Retos Fotograficos y Carpetas | Sistema de gamificacion (misiones para la fiesta) y agrupacion de recuerdos por carpetas. |
| **Fase 2.6** | Generador de Carteles QR Imprimibles | Exportacion de disenos elegantes de centros de mesa con QR y PIN listos para imprenta. |
