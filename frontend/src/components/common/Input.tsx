import React, { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/utils/helpers';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helperText,
  leftIcon,
  rightIcon,
  className,
  id,
  ...props
}, ref) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="br-input">
      {label && (
        <label
          htmlFor={inputId}
          className="br-label"
        >
          {label}
        </label>
      )}

      <div className="br-input-group">
        {leftIcon && (
          <div className="br-input-icon-left">
            <span className="text-gray-500">{leftIcon}</span>
          </div>
        )}

        <input
          ref={ref}
          id={inputId}
          className={cn(
            'br-input',
            error ? 'is-invalid' : '',
            className
          )}
          {...props}
        />

        {rightIcon && (
          <div className="br-input-icon-right">
            <span className="text-gray-500">{rightIcon}</span>
          </div>
        )}
      </div>

      {(error || helperText) && (
        <p className={cn(
          'br-feedback',
          error ? 'is-invalid' : 'br-help-text',
          'text-small'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;