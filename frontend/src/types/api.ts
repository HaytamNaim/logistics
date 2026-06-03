// TypeScript interfaces matching backend API schemas

export interface Zone {
    id: string;
    name: string;
    description?: string;
    polygon?: any;
    created_at: string;
    updated_at: string;
}

export interface DeliveryAddress {
    id: string;
    zone_id: string;
    line1: string;
    line2?: string;
    city: string;
    state_province?: string;
    postal_code?: string;
    country: string;
    latitude?: number;
    longitude?: number;
    created_at: string;
    updated_at: string;
}

export interface OrderItem {
    id: string;
    order_id: string;
    sku: string;
    description: string;
    quantity: number;
    weight_kg?: number;
    created_at: string;
}

export interface Order {
    id: string;
    external_reference?: string;
    delivery_address_id: string;
    customer_name: string;
    customer_phone?: string;
    customer_email?: string;
    status: 'PENDING' | 'CONFIRMED' | 'PREPARING' | 'READY' | 'DISPATCHED' | 'DELIVERED' | 'CANCELLED';
    requested_delivery_start?: string;
    requested_delivery_end?: string;
    total_weight_kg?: number;
    notes?: string;
    created_at: string;
    updated_at: string;
    created_by: string;
    items?: OrderItem[];
    delivery_address?: {
        id: string;
        line1: string;
        city: string;
    };
    delivery?: {
        id: string;
        status: string;
        driver_id?: string;
    };
}

export interface OrderCreate {
    delivery_address_id: string;
    customer_name: string;
    customer_phone?: string;
    customer_email?: string;
    external_reference?: string;
    requested_delivery_start?: string;
    requested_delivery_end?: string;
    total_weight_kg?: number;
    notes?: string;
    items: Array<{
        sku: string;
        description: string;
        quantity: number;
        weight_kg?: number;
    }>;
}

export interface Delivery {
    id: string;
    order_id: string;
    driver_id?: string;
    assigned_by?: string;
    assigned_at?: string;
    status: 'PREPARATION' | 'ASSIGNED' | 'IN_TRANSIT' | 'DELIVERED' | 'FAILED' | 'CANCELLED';
    status_changed_at?: string;
    estimated_distance_km?: number;
    estimated_duration_mins?: number;
    estimated_arrival?: string;
    route_snapshot?: any;
    failure_reason?: string;
    created_at: string;
    updated_at: string;
    status_history?: Array<{
        status: string;
        previous_status?: string;
        created_at: string;
    }>;
}

export interface Driver {
    id: string;
    user_id: string;
    license_number: string;
    vehicle_type?: string;
    vehicle_plate?: string;
    phone?: string;
    availability_status: 'AVAILABLE' | 'BUSY' | 'OFF_DUTY';
    current_location?: {
        lat: number;
        lng: number;
        updated_at: string;
    };
    max_capacity_kg?: number;
    last_availability_updated?: string;
    created_at: string;
    updated_at: string;
}

export interface DeliveryAssign {
    driver_id: string;
}

export interface AutoAssignResult {
    assigned: number;
    failed: number;
    details: Array<{
        delivery_id: string;
        driver_id?: string;
        success: boolean;
        reason?: string;
    }>;
}

// Filter types
export interface OrderFilters {
    status?: string;
    zone_id?: string;
    from_date?: string;
    to_date?: string;
    search?: string; // Client-side filter for order ref, customer name, address
}

export interface DeliveryFilters {
    status?: string;
    driver_id?: string;
    zone_id?: string;
    unassigned_only?: boolean;
}
