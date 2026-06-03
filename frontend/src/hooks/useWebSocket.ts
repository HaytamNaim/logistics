// Custom React hook for WebSocket connection to track delivery updates

import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
    type: 'pong' | 'update' | 'error';
    message?: string;
    data?: any;
}

interface UseWebSocketOptions {
    onMessage?: (data: any) => void;
    onError?: (error: Error) => void;
    reconnectInterval?: number;
    pingInterval?: number;
}

export function useWebSocket(
    deliveryId: string | null,
    options: UseWebSocketOptions = {}
) {
    const {
        onMessage,
        onError,
        reconnectInterval = 3000,
        pingInterval = 30000,
    } = options;

    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<number | null>(null);
    const pingIntervalRef = useRef<number | null>(null);

    const connect = useCallback(() => {
        if (!deliveryId) return;

        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/api/v1/deliveries/${deliveryId}/track`;

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                setIsConnected(true);

                // Start ping interval
                pingIntervalRef.current = window.setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'ping' }));
                    }
                }, pingInterval);
            };

            ws.onmessage = (event) => {
                try {
                    const message: WebSocketMessage = JSON.parse(event.data);

                    if (message.type === 'update' && onMessage) {
                        onMessage(message.data);
                    } else if (message.type === 'error' && onError) {
                        onError(new Error(message.message || 'WebSocket error'));
                    }
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onerror = (event) => {
                console.error('WebSocket error:', event);
                if (onError) {
                    onError(new Error('WebSocket connection error'));
                }
            };

            ws.onclose = () => {
                setIsConnected(false);

                // Clear ping interval
                if (pingIntervalRef.current) {
                    clearInterval(pingIntervalRef.current);
                    pingIntervalRef.current = null;
                }

                // Attempt to reconnect
                reconnectTimeoutRef.current = window.setTimeout(() => {
                    connect();
                }, reconnectInterval);
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            if (onError) {
                onError(error as Error);
            }
        }
    }, [deliveryId, onMessage, onError, reconnectInterval, pingInterval]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
            pingIntervalRef.current = null;
        }

        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        setIsConnected(false);
    }, []);

    useEffect(() => {
        if (deliveryId) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [deliveryId, connect, disconnect]);

    return {
        isConnected,
        disconnect,
        reconnect: connect,
    };
}
