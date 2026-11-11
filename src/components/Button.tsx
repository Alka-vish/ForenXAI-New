import React from 'react';

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses =
    'font-medium transition-all duration-200 cursor-pointer inline-flex items-center justify-center rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500/50 disabled:opacity-40 disabled:cursor-not-allowed';

  const sizeClasses = {
    sm: 'px-4 py-1.5 text-xs',
    md: 'px-5 py-2.5 text-sm',
    lg: 'py-3 px-6 text-sm',
  }[size];

  const variantClasses = {
    primary:
      'bg-red-600 hover:bg-red-500 active:bg-red-700 text-white shadow-lg shadow-red-900/20',

    outline:
      'border border-red-600 text-red-400 hover:bg-red-600/10 hover:text-red-300 active:bg-red-600/20',

    secondary:
      'border border-neutral-700 bg-[#181818] text-neutral-300 hover:bg-[#242424] hover:text-white active:bg-[#2a2a2a]',
  }[variant];

  const widthClass = fullWidth ? 'w-full' : '';

  return (
    <button
      className={`${baseClasses} ${sizeClasses} ${variantClasses} ${widthClass} ${className}`.trim()}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};