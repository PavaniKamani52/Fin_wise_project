/**
 * Badge semantic variants (strict enum — no ad-hoc colors):
 *   healthy   — green, for low stress / good financial health
 *   tight     — amber, for medium stress / watch zone
 *   high      — red-orange, for high stress
 *   critical  — deep red, for critical/overdue situations
 *   ai        — info blue, for AI-generated content markers
 *   neutral   — muted gray, for informational labels
 */
const variants = {
  healthy: {
    background: 'var(--color-green-dim)',
    color: 'var(--color-green)',
    border: '1px solid var(--color-border-green)',
  },
  tight: {
    background: 'var(--color-amber-dim)',
    color: 'var(--color-amber)',
    border: '1px solid var(--color-border-amber)',
  },
  high: {
    background: 'var(--color-warning-dim)',
    color: 'var(--color-warning)',
    border: '1px solid var(--color-border-warning)',
  },
  critical: {
    background: 'var(--color-danger-dim)',
    color: 'var(--color-danger)',
    border: '1px solid var(--color-border-danger)',
  },
  ai: {
    background: 'var(--color-info-dim)',
    color: 'var(--color-info)',
    border: '1px solid var(--color-border-info)',
  },
  neutral: {
    background: 'var(--color-surface)',
    color: 'var(--color-muted)',
    border: '1px solid var(--color-border)',
  },
}

export default function Badge({ children, variant = 'neutral', className = '' }) {
  const style = variants[variant] || variants.neutral
  return (
    <span
      style={{
        ...style,
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '0.6875rem',
        fontWeight: 600,
        letterSpacing: '0.03em',
        fontFamily: 'var(--font-body)',
        whiteSpace: 'nowrap',
      }}
      className={className}
    >
      {children}
    </span>
  )
}
