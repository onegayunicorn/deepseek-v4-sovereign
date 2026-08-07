# SOVEREIGN AI — Color Palette & Tokens

Version 1.0

---

## 1. Core tokens

| Token | Hex | Name | Usage |
|---|---|---|---|
| `--bg-base` | `#0A0A10` | Abyss | Page background, surfaces, dark canvas. Minimum 70% of any screen. |
| `--bg-elevated` | `#101018` | Abyss Elevated | Cards, modals, dropdowns above base. |
| `--accent-primary` | `#00E5FF` | Sovereign Cyan | Primary actions, links, focus rings, active states, key data. The single action color. |
| `--accent-secondary` | `#00FFCC` | Signal Mint | Success states, positive deltas, device "on" indicators, secondary highlights. |
| `--text-primary` | `#E0E0E0` | Cloud Text | Body copy and headings on dark. |
| `--text-dim` | `#8A8A93` | Dim Text | Secondary text, captions, disabled states. (Derived, not a brand color.) |
| `--border` | `#1F1F2B` | Hairline | Borders, dividers on dark surfaces. (Derived.) |

## 2. Status tokens

| Status | Hex | Name | Notes |
|---|---|---|---|
| Success | `#00FFCC` | Mint | Reuses the secondary accent — success is the same signal as "on." |
| Warning | `#FFB800` | Amber Signal | Outside the core palette; reserved for warnings only. |
| Error | `#FF4D6D` | Red Signal | Outside the core palette; reserved for destructive or error states only. |

Status colors never appear in marketing surfaces unless the message is literally about a system state.

## 3. Usage rules

1. One cyan element per view. Two cyan CTAs = no CTA.
2. Mint is success / on-state, never a primary action.
3. Body text is `#E0E0E0`; never render body copy in cyan or mint.
4. Cyan and mint never sit directly on each other without a dark separating band (`#0A0A10` or `#101018`).
5. On light surfaces (print, white docs): text becomes `#0A0A10`, cyan darkens to `#00838F`-class, mint shifts to `#00B38C` for contrast.
6. Status colors (amber, red) stay within 20% of total pixels on any screen — they are signals, not themes.

## 4. Contrast notes

| Pair | Contrast ratio | Verdict |
|---|---|---|
| `#E0E0E0` text on `#0A0A10` | ≈ 14.4:1 | AAA — body text safe |
| `#00E5FF` on `#0A0A10` | ≈ 11.4:1 | AAA — cyan text and icons on dark safe |
| `#00FFCC` on `#0A0A10` | ≈ 12.1:1 | AAA — mint on dark safe |
| `#00E5FF` on `#FFFFFF` | ≈ 1.7:1 | Fail — never cyan text on white; use darkened cyan |
| `#00FFCC` on `#FFFFFF` | ≈ 1.5:1 | Fail — use `#00B38C` on light surfaces |
| `#8A8A93` on `#0A0A10` | ≈ 4.8:1 | AA — dim text only for captions at or above 12px, never body |
| `#FF4D6D` on `#0A0A10` | ≈ 5.6:1 | AA — error text safe on dark |
| `#FFB800` on `#0A0A10` | ≈ 9.6:1 | AAA — warning text safe on dark |

## 5. Accessibility callouts

- Focus ring: 2px cyan outline plus 2px dark gap on focus — meets WCAG 2.4.7 and stays on-brand.
- Never rely on color alone for status; pair status colors with text or glyph ("Online," "Queued," "Failed").
- Surfaces are dark-first. All light-mode surfaces are derived and must pass the contrast table above.
