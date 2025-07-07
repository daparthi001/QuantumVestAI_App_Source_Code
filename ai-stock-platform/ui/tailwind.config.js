/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./src/**/*.{html,js,ts,jsx,tsx}"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        quantum: {
          primary: '#4a90e2',
          'primary-light': '#7bb5f0',
          'primary-dark': '#2a70c2',
          secondary: '#8b5cf6',
          tertiary: '#06b6d4',
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#06b6d4'
        },
        glass: {
          bg: 'rgba(255, 255, 255, 0.1)',
          'bg-dark': 'rgba(0, 0, 0, 0.1)',
          border: 'rgba(255, 255, 255, 0.2)',
        },
        dark: {
          'bg-primary': '#0a0a0a',
          'bg-secondary': '#1a1a1a',
          'bg-tertiary': '#2a2a2a',
          'text-primary': '#ffffff',
          'text-secondary': '#cccccc',
          'text-tertiary': '#999999'
        }
      },
      fontFamily: {
        'quantum': ['Inter', 'system-ui', 'sans-serif'],
        'quantum-mono': ['JetBrains Mono', 'Fira Code', 'monospace']
      },
      fontSize: {
        'quantum-xs': '0.75rem',
        'quantum-sm': '0.875rem',
        'quantum-md': '1rem',
        'quantum-lg': '1.125rem',
        'quantum-xl': '1.25rem',
        'quantum-2xl': '1.5rem',
        'quantum-3xl': '1.875rem',
        'quantum-4xl': '2.25rem'
      },
      spacing: {
        'quantum-xs': '0.25rem',
        'quantum-sm': '0.5rem',
        'quantum-md': '1rem',
        'quantum-lg': '1.5rem',
        'quantum-xl': '2rem',
        'quantum-2xl': '3rem'
      },
      borderRadius: {
        'quantum-sm': '0.375rem',
        'quantum-md': '0.5rem',
        'quantum-lg': '0.75rem',
        'quantum-xl': '1rem',
        'quantum-2xl': '1.5rem'
      },
      backgroundImage: {
        'quantum-gradient-1': 'linear-gradient(135deg, #4a90e2 0%, #8b5cf6 100%)',
        'quantum-gradient-2': 'linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)',
        'quantum-gradient-3': 'linear-gradient(135deg, #06b6d4 0%, #10b981 100%)',
        'quantum-gradient-4': 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
        'quantum-radial': 'radial-gradient(circle, rgba(74, 144, 226, 0.1) 0%, transparent 70%)'
      },
      boxShadow: {
        'quantum-sm': '0 2px 8px rgba(0, 0, 0, 0.1)',
        'quantum-md': '0 4px 16px rgba(0, 0, 0, 0.15)',
        'quantum-lg': '0 8px 32px rgba(0, 0, 0, 0.2)',
        'quantum-glow': '0 0 20px rgba(74, 144, 226, 0.3)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.1)',
        'glass-dark': '0 8px 32px rgba(0, 0, 0, 0.3)'
      },
      backdropBlur: {
        'quantum': '20px'
      },
      animation: {
        'quantum-pulse': 'quantum-pulse 2s ease-in-out infinite',
        'quantum-glow': 'quantum-glow 3s ease-in-out infinite',
        'quantum-float': 'quantum-float 20s ease-in-out infinite',
        'quantum-shimmer': 'quantum-shimmer 2s infinite',
        'quantum-rotate': 'spin 20s linear infinite'
      },
      keyframes: {
        'quantum-pulse': {
          '0%, 100%': { transform: 'scale(1)', opacity: '1' },
          '50%': { transform: 'scale(1.05)', opacity: '0.8' }
        },
        'quantum-glow': {
          '0%': { boxShadow: '0 0 5px rgba(74, 144, 226, 0.5)' },
          '50%': { boxShadow: '0 0 20px rgba(74, 144, 226, 0.8), 0 0 30px rgba(139, 92, 246, 0.6)' },
          '100%': { boxShadow: '0 0 5px rgba(74, 144, 226, 0.5)' }
        },
        'quantum-float': {
          '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
          '33%': { transform: 'translate(30px, -30px) rotate(120deg)' },
          '66%': { transform: 'translate(-20px, 20px) rotate(240deg)' }
        },
        'quantum-shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' }
        }
      },
      transitionDuration: {
        'quantum-fast': '150ms',
        'quantum-medium': '300ms',
        'quantum-slow': '500ms'
      },
      zIndex: {
        'quantum-dropdown': '1000',
        'quantum-sticky': '1020',
        'quantum-fixed': '1030',
        'quantum-modal': '1040',
        'quantum-tooltip': '1070'
      }
    }
  },
  plugins: [
    function({ addUtilities, addComponents, theme }) {
      const newUtilities = {
        '.quantum-text-gradient': {
          background: 'linear-gradient(135deg, #4a90e2, #8b5cf6)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
          'font-weight': '700'
        },
        '.glass-morphism': {
          background: 'rgba(255, 255, 255, 0.1)',
          'backdrop-filter': 'blur(10px)',
          '-webkit-backdrop-filter': 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          'border-radius': '0.75rem'
        },
        '.quantum-hover': {
          transition: 'all 0.3s ease-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            'box-shadow': '0 12px 40px rgba(0, 0, 0, 0.2)'
          }
        }
      }

      const newComponents = {
        '.quantum-btn': {
          position: 'relative',
          display: 'inline-flex',
          'align-items': 'center',
          'justify-content': 'center',
          padding: '0.75rem 1.5rem',
          'font-size': '0.875rem',
          'font-weight': '500',
          'border-radius': '0.75rem',
          border: 'none',
          cursor: 'pointer',
          transition: 'all 0.3s ease-out',
          overflow: 'hidden',
          background: 'linear-gradient(135deg, #4a90e2 0%, #8b5cf6 100%)',
          color: 'white',
          'box-shadow': '0 4px 15px rgba(74, 144, 226, 0.3)',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '0',
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
            transition: 'left 0.5s'
          },
          '&:hover::before': {
            left: '100%'
          },
          '&:hover': {
            transform: 'translateY(-2px)',
            'box-shadow': '0 6px 20px rgba(74, 144, 226, 0.4)'
          },
          '&:active': {
            transform: 'translateY(0)'
          }
        },
        '.quantum-card': {
          background: 'rgba(255, 255, 255, 0.1)',
          'backdrop-filter': 'blur(10px)',
          '-webkit-backdrop-filter': 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          'border-radius': '0.75rem',
          'box-shadow': '0 8px 32px rgba(0, 0, 0, 0.1)',
          transition: 'all 0.3s ease-out',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '-50%',
            left: '-50%',
            width: '200%',
            height: '200%',
            background: 'radial-gradient(circle, rgba(74, 144, 226, 0.05) 0%, transparent 70%)',
            opacity: '0',
            transition: 'opacity 0.5s',
            'z-index': '1'
          },
          '&:hover::before': {
            opacity: '1'
          },
          '&:hover': {
            transform: 'translateY(-4px)',
            'box-shadow': '0 12px 40px rgba(0, 0, 0, 0.2)',
            'border-color': '#4a90e2'
          }
        }
      }

      addUtilities(newUtilities)
      addComponents(newComponents)
    }
  ]
}