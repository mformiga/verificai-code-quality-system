import React, { HTMLAttributes } from 'react';
import { cn } from '@/utils/helpers';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outlined' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  padding = 'md',
  className,
  ...props
}) => {
  const baseStyles = 'br-card';

  const variants = {
    default: '',
    outlined: 'border-2 border-gray-300',
    elevated: 'shadow-md',
  };

  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  return (
    <div
      className={cn(baseStyles, variants[variant], paddings[padding], className)}
      {...props}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}

const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  action,
  children,
  className,
  ...props
}) => (
  <div className={cn('card-header text-center', className)} {...props}>
    <div className="space-y-2">
      {title && (
        <h3 className="text-h3">
          {title}
        </h3>
      )}
      {subtitle && (
        <p className="text-regular text-muted">
          {subtitle}
        </p>
      )}
      {children}
    </div>
    {action && <div>{action}</div>}
  </div>
);

interface CardContentProps extends HTMLAttributes<HTMLDivElement> {}

const CardContent: React.FC<CardContentProps> = ({
  children,
  className,
  ...props
}) => (
  <div className={cn('card-content', className)} {...props}>
    {children}
  </div>
);

interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {}

const CardFooter: React.FC<CardFooterProps> = ({
  children,
  className,
  ...props
}) => (
  <div className={cn('flex items-center pt-4 border-t border-gray-200', className)} {...props}>
    {children}
  </div>
);

export { Card, CardHeader, CardContent, CardFooter };