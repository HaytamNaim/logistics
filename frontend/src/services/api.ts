// API service functions for orders, deliveries, drivers, and zones

import type {
    Order,
    OrderCreate,
    OrderFilters,
    Delivery,
    DeliveryFilters,
    DeliveryAssign,
    AutoAssignResult,
    Driver,
    Zone,
} from '../types/api';

const API_BASE = '/api/v1';

// Prevents concurrent refresh attempts from triggering multiple refresh calls
let refreshPromise: Promise<string> | null = null;

async function refreshTokens(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token');

    const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        throw new Error('Session expired');
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
    }
    return data.access_token;
}

async function apiCall<T>(endpoint: string, options?: RequestInit, retried = false): Promise<T> {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
            ...options?.headers,
        },
    });

    if (response.status === 401 && !retried) {
        // Deduplicate concurrent refresh calls
        if (!refreshPromise) {
            refreshPromise = refreshTokens().finally(() => { refreshPromise = null; });
        }
        try {
            await refreshPromise;
        } catch {
            throw new Error('Session expired. Please log in again.');
        }
        return apiCall<T>(endpoint, options, true);
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

// Orders API
export async function fetchOrders(filters?: OrderFilters): Promise<Order[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.zone_id) params.append('zone_id', filters.zone_id);
    if (filters?.from_date) params.append('from_date', filters.from_date);
    if (filters?.to_date) params.append('to_date', filters.to_date);
    if (filters?.search) params.append('search', filters.search);

    const query = params.toString();
    return apiCall<Order[]>(`/orders${query ? `?${query}` : ''}`);
}

export async function fetchOrder(id: string): Promise<Order> {
    return apiCall<Order>(`/orders/${id}`);
}

export async function createOrder(data: OrderCreate): Promise<Order> {
    return apiCall<Order>('/orders', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

// Deliveries API
export async function fetchDeliveries(filters?: DeliveryFilters): Promise<Delivery[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.driver_id) params.append('driver_id', filters.driver_id);
    if (filters?.zone_id) params.append('zone_id', filters.zone_id);

    const query = params.toString();
    let deliveries = await apiCall<Delivery[]>(`/deliveries${query ? `?${query}` : ''}`);

    // Client-side filter for unassigned only (no server param for this)
    if (filters?.unassigned_only) {
        deliveries = deliveries.filter((d) => !d.driver_id);
    }

    return deliveries;
}

export async function fetchDelivery(id: string): Promise<Delivery> {
    return apiCall<Delivery>(`/deliveries/${id}`);
}

export async function assignDriver(deliveryId: string, driverId: string): Promise<Delivery> {
    return apiCall<Delivery>(`/deliveries/${deliveryId}/assign`, {
        method: 'POST',
        body: JSON.stringify({ driver_id: driverId } as DeliveryAssign),
    });
}

export async function autoAssignPending(): Promise<AutoAssignResult> {
    return apiCall<AutoAssignResult>('/deliveries/assign-auto', { method: 'POST' });
}

// Drivers API
export async function fetchAvailableDrivers(): Promise<Driver[]> {
    return apiCall<Driver[]>('/drivers/available');
}

export async function fetchDrivers(): Promise<Driver[]> {
    return apiCall<Driver[]>('/drivers');
}

// Zones API
export async function fetchZones(): Promise<Zone[]> {
    return apiCall<Zone[]>('/zones');
}
