import React, { ButtonHTMLAttributes } from 'react';
import { cn } from '@/utils/helpers';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  disabled,
  className,
  ...props
}) => {
  const baseStyles = 'br-button';

  const variants = {
    primary: 'primary',
    secondary: 'secondary',
    outline: '',
    ghost: '',
    destructive: '',
  };

  const sizes = {
    sm: 'small',
    md: '',
    lg: 'large',
    xl: 'large',
  };

  const variantClass = variants[variant] || '';
  const sizeClass = sizes[size] || '';

  return (
    <button
      className={cn(baseStyles, variantClass, sizeClass, className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span className="loading mr-2"></span>
      )}
      {leftIcon && !loading && <span className="me-2">{leftIcon}</span>}
      {children}
      {rightIcon && !loading && <span className="ms-2">{rightIcon}</span>}
    </button>
  );
};

export default Button;