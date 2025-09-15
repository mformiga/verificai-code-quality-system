import React from 'react';
import { cn } from '@/utils/helpers';

interface AlertProps {
  variant?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  children: React.ReactNode;
  className?: string;
  closable?: boolean;
  onClose?: () => void;
}

const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  title,
  children,
  className,
  closable = false,
  onClose,
}) => {
  const variants = {
    success: {
      container: 'bg-green-50 border-green-200 text-green-800',
      icon: '✅',
      title: 'text-green-800',
    },
    error: {
      container: 'bg-red-50 border-red-200 text-red-800',
      icon: '❌',
      title: 'text-red-800',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      icon: '⚠️',
      title: 'text-yellow-800',
    },
    info: {
      container: 'bg-blue-50 border-blue-200 text-blue-800',
      icon: 'ℹ️',
      title: 'text-blue-800',
    },
  };

  const currentVariant = variants[variant];

  return (
    <div className={cn(
      'border rounded-lg p-4',
      currentVariant.container,
      className
    )}>
      <div className="flex">
        <div className="flex-shrink-0">
          <span className="text-lg" role="img" aria-label={variant}>
            {currentVariant.icon}
          </span>
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={cn('text-sm font-medium', currentVariant.title)}>
              {title}
            </h3>
          )}
          <div className="text-sm">
            {children}
          </div>
        </div>
        {closable && onClose && (
          <div className="ml-auto pl-3">
            <button
              onClick={onClose}
              className={cn(
                'inline-flex rounded-md p-1.5',
                variant === 'success' && 'hover:bg-green-200',
                variant === 'error' && 'hover:bg-red-200',
                variant === 'warning' && 'hover:bg-yellow-200',
                variant === 'info' && 'hover:bg-blue-200'
              )}
            >
              <span className="sr-only">Fechar</span>
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alert;