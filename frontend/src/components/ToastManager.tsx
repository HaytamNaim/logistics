// ToastManager - Context provider for toast notifications

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { Toast, ToastVariant } from './Toast';

interface ToastMessage {
    id: string;
    variant: ToastVariant;
    title?: string;
    message: string;
}

interface ToastContextType {
    showToast: (variant: ToastVariant, message: string, title?: string) => void;
    success: (message: string, title?: string) => void;
    error: (message: string, title?: string) => void;
    info: (message: string, title?: string) => void;
    warning: (message: string, title?: string) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export function useToast() {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within ToastProvider');
    }
    return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
    const [toasts, setToasts] = useState<ToastMessage[]>([]);

    const showToast = useCallback(
        (variant: ToastVariant, message: string, title?: string) => {
            const id = `toast-${Date.now()}-${Math.random()}`;
            const newToast: ToastMessage = { id, variant, message, title };

            setToasts((prev) => [...prev, newToast]);

            // Auto-dismiss after 5-8 seconds based on variant
            const duration = variant === 'attention' ? 8000 : 5000;
            setTimeout(() => {
                setToasts((prev) => prev.filter((t) => t.id !== id));
            }, duration);
        },
        []
    );

    const success = useCallback(
        (message: string, title?: string) => showToast('success', message, title),
        [showToast]
    );

    const error = useCallback(
        (message: string, title?: string) => showToast('attention', message, title),
        [showToast]
    );

    const info = useCallback(
        (message: string, title?: string) => showToast('info', message, title),
        [showToast]
    );

    const warning = useCallback(
        (message: string, title?: string) => showToast('warning', message, title),
        [showToast]
    );

    const dismissToast = useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    return (
        <ToastContext.Provider value={{ showToast, success, error, info, warning }}>
            {children}

            {/* Toast Container */}
            <div className="fixed top-4 right-4 z-50 space-y-3 max-w-sm">
                {toasts.map((toast) => (
                    <div
                        key={toast.id}
                        className="animate-slide-in-right"
                        style={{
                            animation: 'slideInRight 320ms cubic-bezier(0.33, 1, 0.68, 1)',
                        }}
                    >
                        <Toast
                            variant={toast.variant}
                            title={toast.title}
                            onDismiss={() => dismissToast(toast.id)}
                        >
                            {toast.message}
                        </Toast>
                    </div>
                ))}
            </div>

            <style>{`
        @keyframes slideInRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
        </ToastContext.Provider>
    );
}
