// OrderDataGrid component - Main data grid for orders/deliveries

import { MapPin, User, Package } from 'lucide-react';
import { StatusPill } from './StatusPill';
import type { Order, Delivery } from '../types/api';

interface OrderDataGridProps {
    orders: Order[];
    deliveries: Delivery[];
    onRowClick: (orderId: string, deliveryId?: string) => void;
    onAssignClick: (deliveryId: string) => void;
    highlightedDeliveryId?: string;
}

export function OrderDataGrid({
    orders,
    deliveries,
    onRowClick,
    onAssignClick,
    highlightedDeliveryId,
}: OrderDataGridProps) {
    // Merge orders with their deliveries
    const rows = orders.map((order) => {
        const delivery = deliveries.find((d) => d.order_id === order.id);
        return { order, delivery };
    });

    if (rows.length === 0) {
        return (
            <div className="bg-sand rounded-md shadow-rest p-12 text-center">
                <Package size={48} className="mx-auto mb-4 text-pebble opacity-50" strokeWidth={1.5} />
                <h3 className="text-lg font-medium text-charcoal mb-2">No orders found</h3>
                <p className="text-pebble text-sm">
                    No deliveries match your current filters. Try adjusting your search or filters.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-sand rounded-md shadow-rest overflow-hidden">
            {/* Table Header */}
            <div className="bg-frost border-b border-driftwood px-6 py-3 grid grid-cols-12 gap-4 text-xs font-medium text-pebble uppercase tracking-wide">
                <div className="col-span-2">Order ID</div>
                <div className="col-span-3">Address</div>
                <div className="col-span-2">Status</div>
                <div className="col-span-3">Driver / Resource</div>
                <div className="col-span-2">Actions</div>
            </div>

            {/* Table Body */}
            <div className="divide-y divide-driftwood divide-opacity-50">
                {rows.map(({ order, delivery }) => {
                    const isHighlighted = delivery && delivery.id === highlightedDeliveryId;

                    return (
                        <div
                            key={order.id}
                            onClick={() => onRowClick(order.id, delivery?.id)}
                            className={`
                px-6 py-4 grid grid-cols-12 gap-4 items-center cursor-pointer
                transition-all duration-fast hover:bg-frost
                ${isHighlighted ? 'bg-sage bg-opacity-5 animate-pulse' : ''}
              `}
                            role="button"
                            tabIndex={0}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    onRowClick(order.id, delivery?.id);
                                }
                            }}
                        >
                            {/* Order ID */}
                            <div className="col-span-2">
                                <span className="font-mono text-sm text-charcoal">
                                    #{order.external_reference || order.id.slice(0, 8)}
                                </span>
                            </div>

                            {/* Address */}
                            <div className="col-span-3">
                                <div className="flex flex-col gap-1">
                                    <div className="flex items-start gap-2">
                                        <MapPin size={14} className="text-pebble mt-0.5 flex-shrink-0" strokeWidth={1.8} />
                                        <span className="text-sm text-charcoal line-clamp-1">
                                            {order.delivery_address?.line1 || 'N/A'}
                                        </span>
                                    </div>
                                    <span className="text-xs text-pebble ml-5">
                                        {order.delivery_address?.city || 'Unknown zone'}
                                    </span>
                                </div>
                            </div>

                            {/* Status */}
                            <div className="col-span-2">
                                {delivery ? (
                                    <StatusPill status={getStatusPillType(delivery.status)} />
                                ) : (
                                    <StatusPill status="pending">Pending</StatusPill>
                                )}
                            </div>

                            {/* Driver / Resource */}
                            <div className="col-span-3">
                                {delivery?.driver_id ? (
                                    <div className="flex items-center gap-2">
                                        <User size={14} className="text-pebble" strokeWidth={1.8} />
                                        <span className="text-sm text-charcoal">Driver #{delivery.driver_id.slice(0, 8)}</span>
                                    </div>
                                ) : (
                                    <span className="text-sm text-pebble italic">Unassigned</span>
                                )}
                            </div>

                            {/* Actions */}
                            <div className="col-span-2">
                                {delivery && !delivery.driver_id && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onAssignClick(delivery.id);
                                        }}
                                        className="px-3 py-1.5 text-xs font-medium bg-sage text-white rounded-sm hover:bg-sage-light transition-colors duration-fast focus:outline-none focus:ring-2 focus:ring-sage focus:ring-offset-2"
                                    >
                                        Assign
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// Helper to map delivery status to StatusPill type
function getStatusPillType(status: string): any {
    const mapping: Record<string, any> = {
        PREPARATION: 'pending',
        ASSIGNED: 'warning',
        IN_TRANSIT: 'in_transit',
        DELIVERED: 'delivered',
        FAILED: 'attention',
        CANCELLED: 'cancelled',
    };
    return mapping[status] || 'info';
}
