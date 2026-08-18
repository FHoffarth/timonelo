# 06_UI_PRINCIPLES — Design Freeze v1 & Visual Language

## 1. Design Freeze v1 Status

> **Canonical Rule**: The visual language defined in Figma Design Freeze v1 is **frozen**.  
> Future tasks extend platform features. They do not redesign or reinvent the visual language.

---

## 2. Core Design Tokens

### Color Palette
- **Canvas (Background)**: `#FBF8F3` (Warm ivory / cream)
- **Primary Ink (Text)**: `#0C1B2A` (Midnight navy)
- **Brand Accent**: `#C58A46` (Warm gold / amber)
- **Card Surfaces**: `#FFFFFF` (Pure white with `border-[#0C1B2A]/10`)
- **Key Facts Surfaces**: `#0C1B2A` (Deep navy with pure white text and gold tags)
- **Muted Text**: `#5B6570` (Balanced slate)

### Typography Hierarchy
1. **Editorial Display Headlines**: `"Newsreader Variable", "Newsreader", "Georgia", serif`
   - Hero headlines: `clamp(2.75rem, 6vw, 4.5rem)`
   - Section titles: `clamp(2.00rem, 4vw, 3.00rem)`
2. **Body & Controls**: `"Inter Variable", "Inter", sans-serif`
   - Body copy: `1rem` / line-height `1.5`
   - Controls & badges: `0.75rem` – `0.875rem`
3. **Eyebrows & Section Markers**:
   - `0.6875rem` (`11px`), `font-mono` or geometric sans, uppercase, `letter-spacing: 0.14em`, `#C58A46`.

### Elevation & Radii
- **Standard Card Radius**: `1.25rem` (`20px`)
- **Hero & Key Facts Radius**: `1.75rem` (`28px`)
- **Pill Radius**: `9999px`
- **Subtle Card Shadow**: `0 12px 32px -4px rgba(12, 27, 42, 0.06)`

---

## 3. Component Hierarchy

```
Main Application Shell
├── MainNavbar (Brand serif + gold eyebrow + 5 navigation links + Search trigger)
├── Page View (Composed exclusively of reusable atoms/cards)
│   ├── Hero Section
│   ├── SubTabBar (Underlined tab selector)
│   ├── Content Grid (2:1 or 3-column layout)
│   │   ├── Primary Column (Editorial text / Living Deck canvas / Trajectory map)
│   │   └── Sidebar Column (KeyFactsCard navy / QuickFactsCard light / WeatherCard)
└── Footer (4-column colophon with standards citations)
```
