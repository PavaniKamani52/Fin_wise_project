import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  CreditCard,
  Calculator,
  FileText,
  LogOut,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import Button from '../ui/Button'
import BottomNav from './BottomNav'

const NAV = [
  { to: '/dashboard',  label: 'Dashboard',  Icon: LayoutDashboard },
  { to: '/loans',      label: 'My Loans',   Icon: CreditCard },
  { to: '/settlement', label: 'Settlement',  Icon: Calculator },
  { to: '/letters',    label: 'Letters',     Icon: FileText },
]

function Initials({ name }) {
  const parts = (name || 'U').trim().split(/\s+/)
  const init = parts.length >= 2
    ? parts[0][0] + parts[parts.length - 1][0]
    : parts[0].slice(0, 2)
  return init.toUpperCase()
}

/**
 * DesktopHeader — sticky top navigation bar visible only on desktop (>=768px).
 * Replaces the left sidebar for a cleaner, modern full-width layout.
 */
function DesktopHeader() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        height: 64,
        background: 'white',
        borderBottom: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-card)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        width: '100%',
        flexShrink: 0,
      }}
    >
      {/* Brand logo/wordmark */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span
          style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.4rem',
            fontWeight: 700,
            color: 'var(--color-ink)',
            letterSpacing: '-0.02em',
          }}
        >
          FinWise
        </span>
        <span
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.6875rem',
            fontWeight: 700,
            color: 'var(--color-amber)',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
          }}
        >
          AI
        </span>
      </div>

      {/* Main navigation links */}
      <nav style={{ display: 'flex', gap: 8, height: '100%', alignItems: 'center' }}>
        {NAV.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `header-link${isActive ? ' active' : ''}`}
          >
            {({ isActive }) => (
              <>
                <Icon size={16} strokeWidth={isActive ? 2 : 1.75} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Profile info + Logout action */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              background: 'var(--color-amber-dim)',
              border: '1px solid var(--color-amber)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'var(--color-amber)',
              fontFamily: 'var(--font-body)',
              flexShrink: 0,
            }}
            aria-label={`User: ${user?.name}`}
          >
            <Initials name={user?.name} />
          </div>
          <span
            style={{
              fontSize: '0.875rem',
              fontWeight: 500,
              color: 'var(--color-ink)',
              maxWidth: 150,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
            title={user?.name}
          >
            {user?.name || 'User'}
          </span>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleLogout}
          title="Log out"
          aria-label="Log out"
          style={{ padding: '6px 12px', display: 'flex', gap: 6, alignItems: 'center', fontSize: '0.8125rem' }}
        >
          <LogOut size={16} strokeWidth={1.75} />
          <span className="hidden lg:inline">Log out</span>
        </Button>
      </div>
    </header>
  )
}

/**
 * MobileHeader — slim top bar visible only on mobile (<768px).
 * Contains wordmark on left and logout icon on right.
 */
function MobileHeader() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 60,
        height: 48,
        background: 'white',
        borderBottom: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 16px',
        flexShrink: 0,
      }}
    >
      {/* Mobile logo */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
        <span
          style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.1rem',
            fontWeight: 700,
            color: 'var(--color-ink)',
            letterSpacing: '-0.02em',
          }}
        >
          FinWise
        </span>
        <span
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.625rem',
            fontWeight: 700,
            color: 'var(--color-amber)',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
          }}
        >
          AI
        </span>
      </div>

      <Button
        variant="ghost"
        onClick={handleLogout}
        title="Log out"
        aria-label="Log out"
        style={{
          width: 44,
          height: 44,
          padding: 0,
          marginRight: -8,
          flexShrink: 0,
        }}
        onTouchStart={(e) => (e.currentTarget.style.background = 'var(--color-surface)')}
        onTouchEnd={(e) => (e.currentTarget.style.background = 'none')}
      >
        <LogOut size={18} strokeWidth={1.75} />
      </Button>
    </header>
  )
}

/**
 * AppShell — responsive layout wrapper for authenticated pages.
 * Desktop (≥768px): sticky DesktopHeader at top + full-width main content container.
 * Mobile (<768px):  sticky MobileHeader at top + scrollable content + fixed BottomNav.
 */
export default function AppShell({ children }) {
  return (
    <>
      {/* Desktop layout — hidden on mobile */}
      <div
        className="hidden md:flex md:flex-col"
        style={{ minHeight: '100vh', background: 'var(--color-cream)' }}
      >
        <DesktopHeader />
        <main
          style={{
            flex: 1,
            minWidth: 0,
            overflowY: 'auto',
            background: 'var(--color-cream)',
          }}
        >
          {children}
        </main>
      </div>

      {/* Mobile layout — hidden on desktop */}
      <div
        className="flex flex-col md:hidden"
        style={{
          minHeight: '100vh',
          background: 'var(--color-cream)',
        }}
      >
        <MobileHeader />
        <main
          style={{
            flex: 1,
            /* 60px BottomNav + safe-area — matches BottomNav height */
            paddingBottom: 'calc(60px + env(safe-area-inset-bottom, 0px))',
          }}
        >
          {children}
        </main>
        <BottomNav />
      </div>
    </>
  )
}
