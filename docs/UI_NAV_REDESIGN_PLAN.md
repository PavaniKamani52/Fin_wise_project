# UI and Navigation Redesign Plan — FinWise

This document outlines the design architecture, migration steps, typography updates, and verification criteria for transitioning the desktop layout from a left-side navigation sidebar to a sticky top navigation header bar.

---

## 1. Current Layout Structure
Currently, the application layout is defined in [AppShell.jsx](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/frontend/src/components/layout/AppShell.jsx):
* **Desktop (width ≥ 768px)**:
  * A horizontal two-column layout:
    * Left column: A fixed-width (`248px`), full-height (`100vh`) `Sidebar` navigation.
    * Right column: A scrollable, full-width `main` content viewport displaying child routes (`/dashboard`, `/loans`, `/settlement`, `/letters`).
* **Mobile (width < 768px)**:
  * A vertical three-tier layout:
    * Top: A sticky `MobileHeader` (`48px` height) with logo wordmark and logout button.
    * Center: A scrollable container with padding at the bottom.
    * Bottom: A fixed `BottomNav` bar (`60px` height) containing primary page links.

---

## 2. Files That Will Be Changed

| File Path | Target Modification |
| :--- | :--- |
| [frontend/src/components/layout/AppShell.jsx](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/frontend/src/components/layout/AppShell.jsx) | Refactor the desktop section to render a `DesktopHeader` at the top and remove the `Sidebar`. Remove the left column from the main page wrapper. |
| [frontend/src/index.css](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/frontend/src/index.css) | Change font variables to import and prioritize `Manrope` (headings) and `Inter` (body). Define specific header navigation classes (`.header-link`, `.header-link.active`) using bottom borders/underlines instead of left-border highlights. Adjust global heading weights. |
| [frontend/index.html](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/frontend/index.html) | Done (updated Google Fonts link to load Manrope). |

*Note: [Sidebar.jsx](file:///C:/Users/pavan/Downloads/Fin-Relief-main/Fin-Relief-main/frontend/src/components/layout/Sidebar.jsx) will no longer be rendered on desktop, but we will preserve it or deprecate it cleanly without breaking any dependencies. Let's keep it on disk to ensure perfect backwards compatibility, but it will not be imported by AppShell.*

---

## 3. Navigation Routes (Unchanged)
The following route structures and links must remain fully functional and unchanged to preserve existing application flow:
* `/dashboard` — Dashboard (LayoutDashboard icon)
* `/loans` — My Loans (CreditCard icon)
* `/settlement` — Settlement (Calculator icon)
* `/letters` — Letters (FileText icon)

All routes will use the identical Lucide icons, `NavLink` component bindings, and active-state routing triggers.

---

## 4. Responsive Behavior Plan
* **Desktop screens (≥ 768px)**:
  * A full-width column container (`flex flex-col`).
  * Sticky `DesktopHeader` (height: `64px`) positioned at the top of the viewport.
  * Scrollable `main` area below, expanding to `100%` width with no leftover margins or offset spaces.
* **Mobile screens (< 768px)**:
  * Remains exactly the same: sticky `MobileHeader` at the top, scrollable central main page content, and sticky `BottomNav` pinned at the bottom.
  * Rebranded wordmarks read `FinWise` consistently.

---

## 5. Risks and Mitigations

1. **Content Shifting / Layout Gaps**:
   * *Risk*: Removing the `248px` left sidebar may leave empty space if pages had hardcoded left margins.
   * *Mitigation*: We will review all page wrappers. The main container inside `AppShell` will use simple `flex: 1` width distribution.
2. **z-index Conflicts**:
   * *Risk*: The new `DesktopHeader` or other floating modals (e.g. loan drawers, toast notifications) might overlap incorrectly.
   * *Mitigation*: We will position `DesktopHeader` with `z-index: 50` or `z-index: 60`, keeping it below modals (`z-index: 100+`) but above content.
3. **CORS / API Breakages**:
   * *Risk*: Editing files could break API integrations or login tokens if state management elements are changed.
   * *Mitigation*: We will touch zero logic or hook files (e.g., AuthContext, client.js) during this refactoring phase.
