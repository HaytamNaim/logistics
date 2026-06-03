// OrderManagement - Main Order Management Dashboard page

import { useState, useEffect, useCallback } from 'react';
import { Plus, Sparkles } from 'lucide-react';
import { FilterStrip } from '../components/FilterStrip';
import { OrderDataGrid } from '../components/OrderDataGrid';
import { SlideOverPanel } from '../components/SlideOverPanel';
import { useToast } from '../components/ToastManager';
import type { Order, Delivery, OrderFilters, DeliveryFilters } from '../types/api';
import { fetchOrders, fetchDeliveries, autoAssignPending } from '../services/api';

export function OrderManagement() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [deliveries, setDeliveries] = useState<Delivery[]>([]);
    const [loading, setLoading] = useState(false);
    const [filters, setFilters] = useState<{
        search: string;
        status: string;
        zoneId: string;
        unassignedOnly: boolean;
    }>({
        search: '',
        status: '',
        zoneId: '',
        unassignedOnly: false,
    });
    const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
    const [selectedDeliveryId, setSelectedDeliveryId] = useState<string | null>(null);
    const [highlightedDeliveryId, setHighlightedDeliveryId] = useState<string | undefined>();
    const [isAutoAssigning, setIsAutoAssigning] = useState(false);

    const toast = useToast();

    // Fetch orders and deliveries
    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const orderFilters: OrderFilters = {
                status: filters.status || undefined,
                zone_id: filters.zoneId || undefined,
                search: filters.search || undefined,
            };

            const deliveryFilters: DeliveryFilters = {
                status: filters.status || undefined,
                zone_id: filters.zoneId || undefined,
                unassigned_only: filters.unassignedOnly,
            };

            const [ordersData, deliveriesData] = await Promise.all([
                fetchOrders(orderFilters),
                fetchDeliveries(deliveryFilters),
            ]);

            setOrders(ordersData);
            setDeliveries(deliveriesData);
        } catch (error) {
            console.error('Failed to load data:', error);
            toast.error('Failed to load orders and deliveries');
        } finally {
            setLoading(false);
        }
    }, [filters, toast]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    // Handle row click to open slide-over
    const handleRowClick = (orderId: string, deliveryId?: string) => {
        setSelectedOrderId(orderId);
        setSelectedDeliveryId(deliveryId || null);
    };

    // Handle assign button click
    const handleAssignClick = (deliveryId: string) => {
        const order = orders.find((o) => o.delivery?.id === deliveryId);
        if (order) {
            setSelectedOrderId(order.id);
            setSelectedDeliveryId(deliveryId);
        }
    };

    // Handle successful driver assignment (optimistic UI)
    const handleAssignSuccess = useCallback(
        (deliveryId: string, driverId: string) => {
            // Optimistic update
            setDeliveries((prev) =>
                prev.map((d) =>
                    d.id === deliveryId
                        ? { ...d, driver_id: driverId, assigned_at: new Date().toISOString() }
                        : d
                )
            );

            // Highlight the updated row
            setHighlightedDeliveryId(deliveryId);
            setTimeout(() => setHighlightedDeliveryId(undefined), 2000);

            toast.success(`Delivery assigned successfully`, 'Driver Assigned');

            // Refresh data to ensure consistency
            setTimeout(() => loadData(), 1000);
        },
        [toast, loadData]
    );

    // Handle auto-assign pending deliveries
    const handleAutoAssign = async () => {
        setIsAutoAssigning(true);
        try {
            const result = await autoAssignPending();

            if (result.assigned > 0) {
                toast.success(
                    `${result.assigned} ${result.assigned === 1 ? 'delivery' : 'deliveries'} assigned automatically`,
                    '✨ Auto-Assign Complete'
                );
                loadData();
            } else {
                toast.info('No pending deliveries to assign', 'Auto-Assign');
            }
        } catch (error) {
            console.error('Auto-assign failed:', error);
            toast.error('Failed to auto-assign deliveries');
        } finally {
            setIsAutoAssigning(false);
        }
    };

    return (
        <div className="min-h-screen">
            {/* Header */}
            <div className="bg-frost border-b border-driftwood px-6 py-6 mb-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-display font-medium text-charcoal mb-1">
                            Order Management
                        </h1>
                        <p className="text-sm text-pebble">
                            Track and manage deliveries across all zones
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        {/* Auto-Assign Button */}
                        <button
                            onClick={handleAutoAssign}
                            disabled={isAutoAssigning}
                            className="flex items-center gap-2 px-4 py-2 bg-amber text-white rounded-md hover:bg-opacity-90 disabled:bg-pebble disabled:cursor-not-allowed transition-all duration-fast focus:outline-none focus:ring-2 focus:ring-amber focus:ring-offset-2 shadow-rest"
                        >
                            <Sparkles size={18} strokeWidth={1.8} />
                            <span className="font-medium">
                                {isAutoAssigning ? 'Assigning...' : '✨ Auto-Assign Pending'}
                            </span>
                        </button>

                        {/* New Order Button */}
                        <button
                            onClick={() => toast.info('New Order form coming soon')}
                            className="flex items-center gap-2 px-4 py-2 bg-sage text-white rounded-md hover:bg-sage-light transition-colors duration-fast focus:outline-none focus:ring-2 focus:ring-sage focus:ring-offset-2 shadow-rest"
                        >
                            <Plus size={18} strokeWidth={1.8} />
                            <span className="font-medium">New Order</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="px-6 pb-6">
                {/* Filters */}
                <FilterStrip onFilterChange={setFilters} />

                {/* Data Grid */}
                {loading ? (
                    <div className="bg-sand rounded-md shadow-rest p-12 text-center">
                        <div className="inline-block w-12 h-12 border-4 border-sage border-t-transparent rounded-full animate-spin" />
                        <p className="mt-4 text-sm text-pebble">Loading orders...</p>
                    </div>
                ) : (
                    <OrderDataGrid
                        orders={orders}
                        deliveries={deliveries}
                        onRowClick={handleRowClick}
                        onAssignClick={handleAssignClick}
                        highlightedDeliveryId={highlightedDeliveryId}
                    />
                )}
            </div>

            {/* Slide-Over Panel */}
            <SlideOverPanel
                orderId={selectedOrderId}
                deliveryId={selectedDeliveryId}
                onClose={() => {
                    setSelectedOrderId(null);
                    setSelectedDeliveryId(null);
                }}
                onAssignSuccess={handleAssignSuccess}
            />
        </div>
    );
}
