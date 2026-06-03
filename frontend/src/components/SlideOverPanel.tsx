// SlideOverPanel component - Right-side detail panel for order/delivery details

import { useEffect, useState } from 'react';
import { X, MapPin, Clock, Package, TrendingUp } from 'lucide-react';
import { StatusPill } from './StatusPill';
import type { Order, Delivery, Driver } from '../types/api';
import { fetchOrder, fetchDelivery, fetchAvailableDrivers, assignDriver } from '../services/api';

interface SlideOverPanelProps {
    orderId: string | null;
    deliveryId?: string | null;
    onClose: () => void;
    onAssignSuccess: (deliveryId: string, driverId: string) => void;
}

export function SlideOverPanel({
    orderId,
    deliveryId,
    onClose,
    onAssignSuccess,
}: SlideOverPanelProps) {
    const [order, setOrder] = useState<Order | null>(null);
    const [delivery, setDelivery] = useState<Delivery | null>(null);
    const [drivers, setDrivers] = useState<Driver[]>([]);
    const [selectedDriverId, setSelectedDriverId] = useState('');
    const [isAssigning, setIsAssigning] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!orderId) {
            setOrder(null);
            setDelivery(null);
            return;
        }

        setLoading(true);
        Promise.all([
            fetchOrder(orderId),
            deliveryId ? fetchDelivery(deliveryId) : Promise.resolve(null),
            fetchAvailableDrivers(),
        ])
            .then(([orderData, deliveryData, driversData]) => {
                setOrder(orderData);
                setDelivery(deliveryData);
                setDrivers(driversData);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [orderId, deliveryId]);

    const handleAssign = async () => {
        if (!delivery || !selectedDriverId) return;

        setIsAssigning(true);
        try {
            await assignDriver(delivery.id, selectedDriverId);
            onAssignSuccess(delivery.id, selectedDriverId);
            onClose();
        } catch (error) {
            console.error('Failed to assign driver:', error);
            alert('Failed to assign driver. Please try again.');
        } finally {
            setIsAssigning(false);
        }
    };

    if (!orderId) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-charcoal bg-opacity-30 z-40 transition-opacity duration-normal"
                onClick={onClose}
            />

            {/* Slide-over Panel */}
            <div
                className="fixed top-0 right-0 h-full w-full max-w-md bg-frost shadow-overlay z-50 overflow-y-auto animate-slide-in"
                style={{
                    animation: 'slideIn 320ms cubic-bezier(0.33, 1, 0.68, 1)',
                }}
            >
                {/* Header */}
                <div className="sticky top-0 bg-frost border-b border-driftwood px-6 py-4 flex items-center justify-between z-10">
                    <h2 className="text-lg font-medium text-charcoal">Order Details</h2>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-sm hover:bg-sand transition-colors duration-fast focus:outline-none focus:ring-2 focus:ring-sage"
                        aria-label="Close panel"
                    >
                        <X size={20} strokeWidth={1.8} className="text-pebble" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {loading ? (
                        <div className="text-center py-12">
                            <div className="inline-block w-8 h-8 border-4 border-sage border-t-transparent rounded-full animate-spin" />
                            <p className="mt-4 text-sm text-pebble">Loading details...</p>
                        </div>
                    ) : order ? (
                        <>
                            {/* Order Info */}
                            <section>
                                <h3 className="text-sm font-medium text-pebble uppercase tracking-wide mb-3">
                                    Order Information
                                </h3>
                                <div className="bg-sand rounded-md p-4 space-y-3">
                                    <div className="flex items-center gap-2">
                                        <Package size={16} className="text-pebble" strokeWidth={1.8} />
                                        <span className="font-mono text-sm text-charcoal">
                                            #{order.external_reference || order.id.slice(0, 8)}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-xs text-pebble">Customer</span>
                                        <p className="text-sm text-charcoal font-medium">{order.customer_name}</p>
                                    </div>
                                    {order.customer_phone && (
                                        <div>
                                            <span className="text-xs text-pebble">Phone</span>
                                            <p className="text-sm text-charcoal">{order.customer_phone}</p>
                                        </div>
                                    )}
                                </div>
                            </section>

                            {/* Delivery Address */}
                            <section>
                                <h3 className="text-sm font-medium text-pebble uppercase tracking-wide mb-3">
                                    Delivery Address
                                </h3>
                                <div className="bg-sand rounded-md p-4">
                                    <div className="flex items-start gap-2">
                                        <MapPin size={16} className="text-pebble mt-0.5" strokeWidth={1.8} />
                                        <div>
                                            <p className="text-sm text-charcoal">{order.delivery_address?.line1}</p>
                                            <p className="text-xs text-pebble mt-1">{order.delivery_address?.city}</p>
                                        </div>
                                    </div>
                                </div>
                            </section>

                            {/* Delivery Status */}
                            {delivery && (
                                <section>
                                    <h3 className="text-sm font-medium text-pebble uppercase tracking-wide mb-3">
                                        Delivery Status
                                    </h3>
                                    <div className="bg-sand rounded-md p-4 space-y-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-pebble">Current Status</span>
                                            <StatusPill status={getStatusPillType(delivery.status)} />
                                        </div>

                                        {/* Lifecycle Visualization */}
                                        <div className="pt-2">
                                            <div className="flex items-center justify-between text-xs text-pebble mb-2">
                                                <span>Lifecycle</span>
                                                <TrendingUp size={14} strokeWidth={1.8} />
                                            </div>
                                            <div className="flex items-center gap-2">
                                                {['PREPARATION', 'ASSIGNED', 'IN_TRANSIT', 'DELIVERED'].map((status, idx) => (
                                                    <div key={status} className="flex-1 flex flex-col items-center gap-1">
                                                        <div
                                                            className={`w-full h-1 rounded-full ${getStatusIndex(delivery.status) >= idx
                                                                ? 'bg-moss'
                                                                : 'bg-driftwood bg-opacity-30'
                                                                }`}
                                                        />
                                                        <span className="text-xs text-pebble">{status.slice(0, 4)}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {delivery.status_changed_at && (
                                            <div className="flex items-center gap-2 text-xs text-pebble">
                                                <Clock size={12} strokeWidth={1.8} />
                                                <span>Updated {new Date(delivery.status_changed_at).toLocaleString()}</span>
                                            </div>
                                        )}
                                    </div>
                                </section>
                            )}

                            {/* Driver Assignment */}
                            {delivery && !delivery.driver_id && (
                                <section>
                                    <h3 className="text-sm font-medium text-pebble uppercase tracking-wide mb-3">
                                        Assign Driver
                                    </h3>
                                    <div className="bg-sand rounded-md p-4 space-y-3">
                                        <select
                                            value={selectedDriverId}
                                            onChange={(e) => setSelectedDriverId(e.target.value)}
                                            className="w-full px-3 py-2 bg-frost border border-driftwood rounded-sm text-charcoal focus:outline-none focus:ring-2 focus:ring-sage"
                                        >
                                            <option value="">Select a driver...</option>
                                            {drivers.map((driver) => (
                                                <option key={driver.id} value={driver.id}>
                                                    Driver #{driver.id.slice(0, 8)} - {driver.vehicle_type || 'Vehicle'}
                                                </option>
                                            ))}
                                        </select>
                                        <button
                                            onClick={handleAssign}
                                            disabled={!selectedDriverId || isAssigning}
                                            className="w-full px-4 py-2 bg-sage text-white rounded-sm hover:bg-sage-light disabled:bg-pebble disabled:cursor-not-allowed transition-colors duration-fast focus:outline-none focus:ring-2 focus:ring-sage"
                                        >
                                            {isAssigning ? 'Assigning...' : 'Assign Driver'}
                                        </button>
                                    </div>
                                </section>
                            )}

                            {/* Mini Map Placeholder */}
                            <section>
                                <h3 className="text-sm font-medium text-pebble uppercase tracking-wide mb-3">
                                    Location
                                </h3>
                                <div className="bg-sand rounded-md p-4 h-48 flex items-center justify-center">
                                    <div className="text-center">
                                        <MapPin size={32} className="mx-auto mb-2 text-pebble opacity-50" strokeWidth={1.5} />
                                        <p className="text-xs text-pebble">Map view coming soon</p>
                                    </div>
                                </div>
                            </section>
                        </>
                    ) : (
                        <div className="text-center py-12">
                            <p className="text-sm text-pebble">Failed to load order details</p>
                        </div>
                    )}
                </div>
            </div>

            <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
          }
          to {
            transform: translateX(0);
          }
        }
      `}</style>
        </>
    );
}

// Helper functions
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

function getStatusIndex(status: string): number {
    const statuses = ['PREPARATION', 'ASSIGNED', 'IN_TRANSIT', 'DELIVERED'];
    return statuses.indexOf(status);
}
