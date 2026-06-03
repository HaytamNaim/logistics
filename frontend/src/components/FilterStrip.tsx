// FilterStrip component for Order Management Dashboard

import { useState, useEffect } from 'react';
import { Search, Filter } from 'lucide-react';
import type { Zone } from '../types/api';
import { fetchZones } from '../services/api';

interface FilterStripProps {
    onFilterChange: (filters: {
        search: string;
        status: string;
        zoneId: string;
        unassignedOnly: boolean;
    }) => void;
}

const STATUS_OPTIONS = [
    { value: '', label: 'All Statuses' },
    { value: 'PREPARATION', label: 'Pending' },
    { value: 'ASSIGNED', label: 'Assigned' },
    { value: 'IN_TRANSIT', label: 'In Transit' },
    { value: 'DELIVERED', label: 'Delivered' },
];

export function FilterStrip({ onFilterChange }: FilterStripProps) {
    const [search, setSearch] = useState('');
    const [status, setStatus] = useState('');
    const [zoneId, setZoneId] = useState('');
    const [unassignedOnly, setUnassignedOnly] = useState(false);
    const [zones, setZones] = useState<Zone[]>([]);

    useEffect(() => {
        fetchZones().then(setZones).catch(console.error);
    }, []);

    useEffect(() => {
        onFilterChange({ search, status, zoneId, unassignedOnly });
    }, [search, status, zoneId, unassignedOnly, onFilterChange]);

    return (
        <div className="bg-sand rounded-md shadow-rest p-4 mb-6">
            <div className="flex flex-wrap gap-4 items-center">
                {/* Search Input */}
                <div className="flex-1 min-w-[240px]">
                    <div className="relative">
                        <Search
                            className="absolute left-3 top-1/2 -translate-y-1/2 text-pebble"
                            size={18}
                            strokeWidth={1.8}
                        />
                        <input
                            type="text"
                            placeholder="Search order #, customer, address..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-frost border border-driftwood rounded-sm text-charcoal placeholder-pebble focus:outline-none focus:ring-2 focus:ring-sage transition-all duration-fast"
                        />
                    </div>
                </div>

                {/* Status Dropdown */}
                <div className="min-w-[160px]">
                    <select
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                        className="w-full px-3 py-2 bg-frost border border-driftwood rounded-sm text-charcoal focus:outline-none focus:ring-2 focus:ring-sage transition-all duration-fast appearance-none cursor-pointer"
                        style={{
                            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236B645C' d='M6 8L2 4h8z'/%3E%3C/svg%3E")`,
                            backgroundRepeat: 'no-repeat',
                            backgroundPosition: 'right 0.75rem center',
                            paddingRight: '2.5rem',
                        }}
                    >
                        {STATUS_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                                {opt.label}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Zone Dropdown */}
                <div className="min-w-[160px]">
                    <select
                        value={zoneId}
                        onChange={(e) => setZoneId(e.target.value)}
                        className="w-full px-3 py-2 bg-frost border border-driftwood rounded-sm text-charcoal focus:outline-none focus:ring-2 focus:ring-sage transition-all duration-fast appearance-none cursor-pointer"
                        style={{
                            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236B645C' d='M6 8L2 4h8z'/%3E%3C/svg%3E")`,
                            backgroundRepeat: 'no-repeat',
                            backgroundPosition: 'right 0.75rem center',
                            paddingRight: '2.5rem',
                        }}
                    >
                        <option value="">All Zones</option>
                        {zones.map((zone) => (
                            <option key={zone.id} value={zone.id}>
                                {zone.name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Unassigned Toggle */}
                <label className="flex items-center gap-2 cursor-pointer select-none">
                    <input
                        type="checkbox"
                        checked={unassignedOnly}
                        onChange={(e) => setUnassignedOnly(e.target.checked)}
                        className="w-4 h-4 rounded border-driftwood text-sage focus:ring-2 focus:ring-sage cursor-pointer"
                    />
                    <span className="text-sm text-charcoal">Show Unassigned Only</span>
                </label>

                {/* Filter Icon */}
                <div className="text-pebble">
                    <Filter size={20} strokeWidth={1.8} />
                </div>
            </div>
        </div>
    );
}
