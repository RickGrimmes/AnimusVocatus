/**
 * Genera una miniatura WebP de 400px optimizada en el navegador del usuario
 * para subida a R2 con consumo de CPU servidor igual a cero.
 */
export async function generateClientThumbnail(
  file: File,
  maxDimension = 400,
  quality = 0.8
): Promise<Blob> {
  if (!file.type.startsWith('image/')) {
    throw new Error('Solo se pueden generar miniaturas para archivos de imagen');
  }

  // Si el navegador soporta createImageBitmap (moderno y mas rapido)
  let imageBitmap: ImageBitmap | null = null;
  try {
    imageBitmap = await createImageBitmap(file);
  } catch {
    // fallback tradicional con HTMLImageElement
  }

  const width = imageBitmap ? imageBitmap.width : 0;
  const height = imageBitmap ? imageBitmap.height : 0;

  let targetWidth = width;
  let targetHeight = height;

  if (width > 0 && height > 0) {
    if (width > height) {
      if (width > maxDimension) {
        targetHeight = Math.round((height * maxDimension) / width);
        targetWidth = maxDimension;
      }
    } else {
      if (height > maxDimension) {
        targetWidth = Math.round((width * maxDimension) / height);
        targetHeight = maxDimension;
      }
    }
  }

  if (typeof OffscreenCanvas !== 'undefined' && imageBitmap) {
    const offscreen = new OffscreenCanvas(targetWidth, targetHeight);
    const ctx = offscreen.getContext('2d');
    if (ctx) {
      ctx.drawImage(imageBitmap, 0, 0, targetWidth, targetHeight);
      return await offscreen.convertToBlob({ type: 'image/webp', quality });
    }
  }

  // Fallback para entornos donde OffscreenCanvas no este disponible
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      let w = img.width;
      let h = img.height;
      if (w > h) {
        if (w > maxDimension) {
          h = Math.round((h * maxDimension) / w);
          w = maxDimension;
        }
      } else {
        if (h > maxDimension) {
          w = Math.round((w * maxDimension) / h);
          h = maxDimension;
        }
      }

      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('No se pudo obtener el contexto 2D'));
        return;
      }
      ctx.drawImage(img, 0, 0, w, h);
      canvas.toBlob(
        (blob) => {
          if (blob) resolve(blob);
          else reject(new Error('Fallo la conversion a WebP'));
        },
        'image/webp',
        quality
      );
    };
    img.onerror = reject;
    img.src = URL.createObjectURL(file);
  });
}
