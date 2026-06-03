# Logistics in Harmony — Design System & UI Mockup

**Document Version:** 1.0  
**Role:** Senior UI/UX Designer — Biophilic Design & Data Visualization for Enterprise SaaS  
**Product:** Logistics and Delivery Management System

---

## 1. Design Concept Statement

### Philosophy: "Logistics in Harmony"

Logistics software often feels like a control room under pressure: dense tables, harsh alerts, and a sense of constant urgency. **Logistics in Harmony** inverts that. The theme treats the interface as a **living command center**—a place where complex operations are overseen with clarity and calm, not alarm.

- **Reduced cognitive load:** Information is structured in natural “zones” (like sections of a garden) rather than wall-to-wall grids. The eye moves along organic flows, not rigid blocks.
- **Status as rhythm, not alarm:** Delays and issues are surfaced with **organic severity**—terracotta, amber, soft rust—so they demand attention without triggering stress. Success states feel like rest (sage, mist, stone).
- **Premium Organic, not kitsch:** No leaf borders or literal forests. The “nature” is in **materials and motion**: paper-like surfaces, topographic depth, growth-metaphor progress, and gentle transitions. Think high-end wellness or design-led travel apps, not nature wallpaper.
- **Usability first:** Every biophilic choice must support **WCAG 2.1 AA** (contrast, focus, semantics) and preserve **data density** where managers and drivers need it. Beauty serves clarity.

---

## 2. Visual Style Guide

### 2.1 Color Palette — "Nature-Close"

| Role | Name | HEX | Usage |
|------|------|-----|--------|
| **Primary** | Sage Mist | `#5B7B6B` | Primary actions, key headers, links |
| **Primary Light** | Meadow | `#8FA99A` | Hover, secondary emphasis |
| **Secondary** | Slate Stream | `#4A6572` | Nav, secondary buttons |
| **Neutral** | Stone Paper | `#F6F4F0` | Main background |
| **Neutral** | Sand | `#E8E4DD` | Card/surface background, dividers |
| **Neutral** | Driftwood | `#C4BDB4` | Borders, disabled states |
| **Neutral** | Charcoal Bark | `#3D3630` | Primary text (not pure black) |
| **Neutral** | Pebble | `#6B645C` | Secondary text |
| **Accent** | Terracotta | `#C17F59` | Delayed, warning, needs attention |
| **Accent** | Amber Honey | `#D4A04A` | In progress, pending |
| **Accent** | Moss | `#6B8E6B` | Delivered, success, completed |
| **Accent** | Mist Blue | `#7B9AAF` | In transit, informational |
| **Accent** | Clay | `#B8957A` | Optional highlights, tags |
| **Surface Overlay** | Frost | `#FFFFFF` (92% opacity on Stone Paper) | Modals, floating panels |

**Status mapping (organic, no neon):**

- **Delayed / At risk:** Terracotta `#C17F59`
- **In progress / Pending:** Amber Honey `#D4A04A`
- **Delivered / Success:** Moss `#6B8E6B`
- **In transit:** Mist Blue `#7B9AAF`
- **Cancelled / Inactive:** Pebble `#6B645C` with reduced opacity

**Accessibility:** Charcoal Bark on Stone Paper and Sand meets WCAG AA for body text. Sage Mist and Slate Stream on light backgrounds pass for large UI and buttons. Terracotta and Amber are used with sufficient contrast (e.g. on Sand or Frost) and never as the only differentiator.

---

### 2.2 Typography

**Principles:** Organic curves, readability at high data density, distinct hierarchy without heaviness.

| Level | Font | Weight | Size (desktop) | Use |
|-------|------|--------|------------------|-----|
| **Display** | **Fraunces** or **Instrument Serif** | 500–600 | 28–32px | Hero / section titles (sparingly) |
| **Headings** | **DM Sans** or **Outfit** | 500–600 | 18–22px | Card titles, nav labels |
| **Body** | **DM Sans** or **Outfit** | 400 | 14–16px | Tables, lists, descriptions |
| **Supporting** | **DM Sans** or **Outfit** | 400 | 12–13px | Captions, metadata, timestamps |
| **Data / Mono** | **JetBrains Mono** or **IBM Plex Mono** | 400 | 13–14px | IDs, refs, coordinates |

- **Organic touch:** Fraunces/Instrument Serif for a few key headlines adds a human, non-corporate note without reducing legibility.
- **Primary UI font:** DM Sans or Outfit for almost everything—friendly curves, clean numbers, works in dense tables and on small driver screens.
- **Line height:** 1.45–1.55 for body; 1.2–1.3 for headings.
- **Letter-spacing:** Slight positive tracking (+0.02–0.04em) on all-caps labels and tags.

---

### 2.3 Iconography

- **Style:** Outlined, 1.5–2px stroke, rounded line caps and joins. No filled “chip” icons in primary UI.
- **Library:** Phosphor (Duotone or Regular) or Lucide; restrict to one library for consistency.
- **Size scale:** 16px (inline), 20px (buttons), 24px (nav, empty states).
- **Color:** Icons inherit text color (Pebble or Charcoal Bark) or use the status palette for state (e.g. Terracotta for delay icon).
- **Nature hint:** Where it fits (e.g. “Route complete”), use a growth/check hybrid (e.g. leaf + check) only if it stays recognizable and on-brand. Prefer clarity over metaphor when in doubt.

---

### 2.4 Shapes & "Soft-UI" Kit

- **Radius:** 12px for cards and main containers; 8px for buttons, chips, inputs; 20–24px for modals and large panels. No sharp corners in primary surfaces.
- **Shadows:**  
  - Rest: `0 1px 3px rgba(61, 54, 48, 0.06)`  
  - Elevated: `0 4px 12px rgba(61, 54, 48, 0.08)`  
  - Overlay: `0 8px 24px rgba(61, 54, 48, 0.12)`  
  All in Charcoal Bark family so shadows feel earthy, not gray-blue.
- **Dividers:** Prefer **non-linear** or **textured** separators:  
  - Short, rounded “flow” lines (e.g. a 40% width line with rounded ends) between sections.  
  - Or a very subtle topographic-style gradient (Sand → Driftwood at 3–5% opacity) instead of a 1px rule.
- **Borders:** 1px solid `Driftwood` at 60–80% opacity; avoid hard black or pure gray.

---

### 2.5 Nature Elements (Backgrounds & Texture)

- **Topographic backgrounds:**  
  - Optional for dashboard or map sidebar: very light (3–6% opacity) contour-line texture over Stone Paper or Sand.  
  - Use as a single full-bleed layer; never on top of critical data.  
- **Leaf-vein / network hint:**  
  - For route or network views, consider line styles that suggest veins: slightly irregular stroke, short branching segments, or a custom dashed pattern. Keep contrast low so it supports, not competes with, the actual route lines.  
- **Weather-responsive themes (concept):**  
  - Clear: current default (Stone Paper, Sage, Slate).  
  - Overcast: slightly cooler (hint of Mist Blue in backgrounds).  
  - Evening: warmer Sand and Clay accents.  
  - Implement as optional theme tokens, not required for MVP.

---

## 3. Dashboard Layout Description — "Control Garden"

The main tracking screen is a **Control Garden**: data appears in clearly defined, calm “beds” rather than a single dense grid.

### 3.1 Overall Structure

- **Canvas:** Stone Paper `#F6F4F0` base. Optional very light topographic texture (global, low opacity).
- **Header (fixed):**  
  - Frost surface, soft shadow.  
  - Logo + product name left; primary nav (Orders, Deliveries, Routes, Fleet, Analytics) center or left-of-center; user/notifications right.  
  - Height ~56–64px, 12px radius on bottom corners if it sits above content.
- **Main area:**  
  - **Left rail (optional, ~260px):** Filters, date range, quick stats (e.g. “Today: 12 deliveries, 2 in transit”). Soft dividers, Sand cards. Collapsible on smaller viewports.  
  - **Center (~flex):** Map + list. Map is the “field”; list is the “bed” beside it.  
  - **Right rail (optional, ~320px):** Detail panel (selected order/delivery/driver), activity stream, or alerts. Same Sand/Frost treatment.

### 3.2 Map Zone — "Living Terrain"

- **Default view:** Terrain or hybrid (satellite with subtle overlay) rather than stark gray/vector streets. If API allows (e.g. Mapbox), use a **custom style**: muted greens and tans, soft roads, labels in Pebble/Charcoal Bark.
- **Markers:**  
  - Rounded or soft-teardrop shapes.  
  - Status color fill (Moss, Amber, Terracotta, Mist Blue) with a thin Driftwood outline.  
  - No pin spikes unless needed for exact address; prefer low-profile dots or small circles.
- **Routes:**  
  - Curved lines where possible.  
  - Stroke in Sage Mist or Slate Stream, 3–4px, semi-transparent.  
  - “Completed” leg can fade to Moss and thin out (growth-metaphor: finished path “rests”).
- **Clustering:** Clusters as soft circles (Sand or Meadow tint) with count in Charcoal Bark; expand with a gentle scale animation.

### 3.3 Data Widgets — "Beds"

- **Order / delivery cards:**  
  - Sand or Frost background, 12px radius, light shadow.  
  - Compact header: ID, status pill (organic palette), time.  
  - Body: address snippet, driver name (if assigned), one key metric.  
  - No heavy borders; separator is a short “flow” line or spacing.
- **KPI strips:**  
  - Horizontal band (Frost or Sand) with 4–6 metrics.  
  - Number in Charcoal Bark (or Sage for positive); label in Pebble.  
  - Optional micro “growth” bar (Moss) for share of total, or a tiny inline sparkline in Mist Blue/Clay.
- **Tables (orders, drivers):**  
  - Zebra in Sand at 30% opacity, or no zebra and row hover only.  
  - Status as colored left border (4px) or small pill, not full-row color.  
  - Plenty of padding; Driftwood dividers or “flow” lines between rows if density allows.

### 3.4 Progress & Completion — "Growth" Metaphors

- **Delivery progress:**  
  - **Vine option:** A single path (route) with a soft fill or gradient that “grows” along the path as % complete increases.  
  - **Stream option:** A horizontal bar with a gradient (Moss → Meadow) and a subtle wave or flow texture that fills left-to-right.  
- **Route completion:**  
  - Same logic: progress shown as advancing along the route line or as a “filled stream” bar.  
- **Global progress (e.g. “Day at 60%”):**  
  - One compact bar, 6–8px height, Sand track, Moss fill, rounded ends. Optional very subtle animation (e.g. a gentle pulse on the growing edge).

---

## 4. Interaction Design

### 4.1 State Changes & Transitions

- **Principle:** Gentle, continuous transitions over sudden pop-ups or hard cuts.
- **Duration:** 200–320ms for UI state (expand/collapse, tab switch, panel open); 400–500ms for “moment” changes (e.g. delivery marked Delivered).
- **Easing:** Ease-out for enter (e.g. modal, drawer); ease-in-out for state toggles. No linear for primary interactions.
- **Content:** Prefer **crossfade + light move** (e.g. 4–8px vertical) instead of scale-only to avoid a “zoom” feel.

### 4.2 Notifications & Alerts

- **Placement:** Top-right or bottom-right, stacking downward. Max 2–3 visible; older ones collapse into a “Recent” panel or list.
- **Container:** Frost surface, 12px radius, soft shadow. Left border (4px) in status color (Terracotta for delay, Amber for warning, Moss for success, Mist Blue for info).
- **Entry:** Slide-in from the right (~320ms, ease-out) + fade. No bounce.
- **Dismiss:** Fade + slight slide out, or swipe on touch. Auto-dismiss optional (e.g. 5–8s for success; longer or sticky for delays).
- **Copy:** Calm, actionable (“Delivery #1234 is running ~15 min behind” vs “URGENT: DELAY”). Avoid all-caps and exclamation marks for non-critical messages.

### 4.3 Feedback for Actions

- **Clicks / taps:** Brief scale (0.98) or a soft opacity dip (0.9) for 80–100ms. Buttons use border or background shift (e.g. Sage → Meadow) on hover.
- **Success (e.g. “Mark delivered”):**  
  - Short check animation (stroke-draw or scale) in Moss.  
  - Optional micro confetti in Moss/Clay (few, small, slow) for major milestones only.  
- **Error / validation:**  
  - Inline message in Terracotta near the field; field border in Terracotta at 60% opacity.  
  - No full-screen takeover unless it’s a critical system error.

### 4.4 Loading & Empty States

- **Loading:** Skeleton in Sand/Driftwood pulse (1.5s cycle), matching the layout of the incoming content. Or a minimal “growth” bar (Moss gradient moving left-to-right in a thin strip).
- **Empty (e.g. no orders today):**  
  - Soft illustration or icon (e.g. a single leaf or a quiet path) in Pebble/Driftwood.  
  - Short, encouraging line of copy (“No deliveries yet—today’s routes will appear here.”).  
  - One clear CTA (e.g. “Create order”) in Sage.

### 4.5 Accessibility (WCAG 2.1 AA)

- **Focus:** Visible focus ring (2px, Sage Mist or Slate Stream, offset 2px). Never remove focus visibility.
- **Motion:** Respect `prefers-reduced-motion`: disable non-essential animations and use instant state changes where motion is turned off.
- **Contrast:** All body and UI text meets 4.5:1 on background; large text and heavy buttons meet 3:1. Status is never conveyed by color alone (always icon or label).
- **Semantics:** Headings in order; lists and regions landmarked. Custom components expose roles and names (e.g. “Delivery status”, “Alert”).

---

## 5. Summary — Design Tokens (Quick Reference)

```text
# Surfaces
--bg-base:       #F6F4F0  (Stone Paper)
--bg-surface:    #E8E4DD  (Sand)
--bg-elevated:   rgba(255,255,255,0.92)  (Frost)

# Text
--text-primary:  #3D3630  (Charcoal Bark)
--text-secondary:#6B645C  (Pebble)

# Brand & Status
--brand:         #5B7B6B  (Sage Mist)
--success:       #6B8E6B  (Moss)
--warning:       #D4A04A  (Amber Honey)
--attention:     #C17F59  (Terracotta)
--info:          #7B9AAF  (Mist Blue)

# Borders & Dividers
--border:        rgba(196,189,180,0.8)  (Driftwood)
--radius-sm:     8px
--radius-md:     12px
--radius-lg:     20px
```

---

## 6. Implementation Note

The design system is implemented in the **React frontend** (`frontend/`):

- **Tokens:** `frontend/src/theme/design-tokens.css` (CSS custom properties).
- **Typography:** Google Fonts — DM Sans, Fraunces, JetBrains Mono (see `frontend/index.html`).
- **Layout:** “Control Garden” — `Layout`, `Header`, `LeftRail`, `RightRail`, center content area.
- **Components:** `StatusPill`, `Card`, `KPIStrip`, `ProgressStream` (growth metaphor), `Toast` (notifications).
- **Dashboard:** `pages/Dashboard` — KPI strip, day-progress stream, map placeholder (topographic hint), delivery list with status pills.
- **Icons:** Lucide React (outlined, 1.8 stroke).
- **Motion:** CSS transitions use `var(--duration-*)` and `var(--ease-*)`; `prefers-reduced-motion` disables non-essential animation.

Run the frontend: `cd frontend && npm install && npm run dev` → http://localhost:3000 .

*This design system supports the Logistics and Delivery Management System (see TECHNICAL_BLUEPRINT.md).*
