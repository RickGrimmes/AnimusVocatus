---
name: instagram-media-experience
description: Directrices de diseno e implementacion para experiencias web inmersivas estilo Instagram (Galeria movil y Reproductor Reels/Stories).
---

# Instagram Media Experience (Galeria & Reels Viewer)

Esta skill define los patrones de interfaz de usuario, animaciones, estilos y comportamiento de navegacion para emular la fluidez y usabilidad de Instagram en la suite Vocatus & Animus, optimizada para navegadores moviles.

## 1. Principios de Diseno Visual
- **Paleta de Color Base:**
  - Fondo oscuro inmersivo: `#000000` (pantalla completa para Reels) y `#121212` para superficies elevadas.
  - Fondo claro/editorial para invitaciones: `#fafafa` o crema suave `#fcfbf9` con acentos negros `#1a1a1a`.
  - Bordes tenues: `rgba(255, 255, 255, 0.15)` en dark mode o `#e5e5e5` en light mode.
  - Color de acento de interaccion (likes/favoritos): Rojo carmesi `#ff3040`.
- **Tipografia:**
  - Pila nativa de sistema tipo Instagram: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.
  - Jerarquia: Titulos limpios en peso 600-700, cuerpo en peso 400-500, subtitulos y metadatos en peso 400 con opacidad reducida (70%).

## 2. Componente de Galeria Tipo Telefono (Grid View)
- Cuadricula responsive de 3 columnas (`grid grid-cols-3 gap-0.5 sm:gap-1`).
- Aspect ratio 1:1 (`aspect-square`) con `object-cover`.
- Indicador visual para clips de video (icono sutil de duracion o camara en esquina superior derecha).
- Carga progresiva y uso exclusivo de miniaturas WebP (`thumb_url`) para maxima velocidad con red celular debil.
- Al pulsar una foto o video, transiciona instantaneamente al indice correspondiente del visor Reels.

## 3. Visor Inmersivo Estilo Reels (Reels Viewer)
- **Contenedor:**
  - Pantalla completa fija (`fixed inset-0 z-50 bg-black`).
  - Desplazamiento vertical con `snap-y snap-mandatory overflow-y-scroll`.
  - Cada diapositiva ocupa `h-full w-full snap-start relative flex items-center justify-center`.
- **Media:**
  - Fotos y videos centrados con `max-h-full max-w-full object-contain`.
  - Videos en loop automatico al estar visibles en el viewport (usando `IntersectionObserver`).
- **Superposicion de Informacion (Overlay Inferior Izquierdo):**
  - Avatar o inicial del invitado (`guest_author`).
  - Nombre del autor en negrita y tiempo transcurrido relativo ("hace 10 min").
- **Barra de Acciones Flotante (Lateral Derecho):**
  - Boton de corazon / Me gusta con micro-animacion de rebote (scale 1.25 -> 1.0).
  - Doble toque en pantalla para disparar corazon flotante centrado.
  - Boton para cerrar y regresar a la cuadricula de galeria.

## 4. Optimizacion de Rendimiento Movil
- Generar miniatura en `OffscreenCanvas` antes de subir.
- Mantener en memoria solo las diapositivas contiguas (+1 y -1) del visor de Reels para prevenir consumo excesivo de RAM en Safari iOS / Chrome Android.
