const API_BASE_URL = (typeof window !== 'undefined' && (window as any).__API_URL__) 
  || 'http://localhost:8000';

export interface VocatusEvent {
  slug: string;
  title: string;
  event_date: string;
  event_type: string;
  location_name?: string;
  location_address?: string;
  location_maps_url?: string;
  location_waze_url?: string;
  itinerary?: string;
  gift_registry_info?: string;
  dress_code?: string;
  is_active: boolean;
}

export interface GuestSearchItem {
  id: string;
  guest_name: string;
  allocated_passes: number;
  confirmed_passes: number;
  status: string;
}

export interface RSVPPayload {
  guest_id?: string;
  guest_name?: string;
  confirmed_passes: number;
  status: 'confirmed' | 'declined';
  dietary_restrictions?: string;
  message?: string;
}

export interface MediaFeedItem {
  id: string;
  event_id: string;
  r2_key: string;
  thumb_r2_key?: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  guest_author?: string;
  moderation_status: string;
  is_favorite: boolean;
  created_at: string;
  url?: string;
  thumb_url?: string;
}

// Fallback demo para invitacion Vocatus
export const DEMO_VOCATUS_EVENT: VocatusEvent = {
  slug: 'boda-carlos-y-sofia',
  title: 'Carlos & Sofia',
  event_date: '2026-10-25T18:00:00Z',
  event_type: 'boda',
  location_name: 'Hacienda de los Morales',
  location_address: 'Vazquez de Mella 525, Polanco, CDMX',
  location_maps_url: 'https://maps.google.com/?q=Hacienda+de+los+Morales',
  location_waze_url: 'https://waze.com/ul?q=Hacienda+de+los+Morales',
  dress_code: 'Rigurosa Etiqueta / Black Tie',
  gift_registry_info: 'Liverpool: 51239485 | El Palacio de Hierro: 982341',
  itinerary: '18:00 Ceremonia Religiosa | 19:30 Coctel de Bienvenida | 21:00 Cena y Brindis | 23:00 Apertura de Pista',
  is_active: true,
};

export async function fetchEventVocatus(slug: string): Promise<VocatusEvent> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v/${slug}`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('API local no disponible, usando datos demostrativos:', err);
  }
  return DEMO_VOCATUS_EVENT;
}

export async function searchEventGuests(slug: string, query: string): Promise<GuestSearchItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v/${slug}/search?q=${encodeURIComponent(query)}`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('API error searching guests:', err);
  }
  return [];
}

export async function submitEventRSVP(slug: string, payload: RSVPPayload) {
  const res = await fetch(`${API_BASE_URL}/api/v/${slug}/rsvp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Error al enviar confirmacion' }));
    throw new Error(error.detail || 'Error al confirmar');
  }
  return await res.json();
}

export async function enterVaultWithPin(slug: string, pin: string) {
  const res = await fetch(`${API_BASE_URL}/api/a/${slug}/enter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pin }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'PIN incorrecto' }));
    throw new Error(error.detail || 'PIN incorrecto');
  }
  return await res.json();
}

export async function fetchMediaFeed(slug: string, limit = 50, offset = 0): Promise<MediaFeedItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/a/${slug}/feed?limit=${limit}&offset=${offset}`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('API error fetching feed:', err);
  }
  return [];
}

export async function requestBatchPresignedUrls(
  slug: string,
  files: Array<{ filename: string; size_bytes: number; content_type: string }>,
  token: string,
) {
  const res = await fetch(`${API_BASE_URL}/api/a/${slug}/batch-presigned`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ files }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error al solicitar subida' }));
    throw new Error(err.detail || 'Error al solicitar subida');
  }
  return await res.json();
}

export async function confirmMediaUpload(
  slug: string,
  payload: {
    id: string;
    r2_key: string;
    thumb_r2_key?: string;
    filename: string;
    content_type: string;
    size_bytes: number;
    guest_author?: string;
  },
  token: string,
) {
  const res = await fetch(`${API_BASE_URL}/api/a/${slug}/media/confirm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error al asentar archivo' }));
    throw new Error(err.detail || 'Error al asentar archivo');
  }
  return await res.json();
}
