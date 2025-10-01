# Guide Hero-Style Header - Implementation

## Overview
Replaced plain title/subtitle with a hero-style header featuring gradient backgrounds and subtle animated accent shapes, similar to the main hero carousel but simplified for guide pages.

## Visual Features

### Gradient Background
- **Base gradient**: Linear gradient from dark blue-purple to deeper blue
- **Accent gradients**: Two radial gradients creating colorful "orbs"
  - Purple orb (top-left, 20% 20%)
  - Cyan orb (bottom-right, 80% 30%)
- **Animation**: Slow 15-second gradient shift for subtle movement

### Animated Accent Shapes
Two pseudo-elements (`::before` and `::after`) create floating decorative shapes:
- **Purple accent** (top-left): Floats up/down with 20s animation
- **Cyan accent** (bottom-right): Floats with 7s delay for varied motion
- **Blur effect**: 80px blur for soft, dreamy aesthetic
- **Opacity**: 0.4 for subtle presence

### Styling Details
- **Border radius**: 16px for modern, soft corners
- **Padding**: 
  - Mobile: 3rem 1rem
  - Desktop: 4rem 2rem
- **Min height**:
  - Mobile: 320px
  - Desktop: 380px
- **Text alignment**: Centered
- **Max width**: 900px inner container

## File Changes

### 1. Variables (`static/scss/_variables.scss`)
Added new tokens:
```scss
$guide-hero-bg-base: linear-gradient(135deg, #1a1b26 0%, #202a3a 100%)
$guide-hero-padding-mobile: 3rem 1rem
$guide-hero-padding-desktop: 4rem 2rem
$guide-hero-min-height-mobile: 320px
$guide-hero-min-height-desktop: 380px
```

### 2. Styles (`static/scss/layout/_guides.scss`)
Added `.hero--guide` component with:
- Gradient background layers
- Animated pseudo-elements for accent shapes
- Responsive sizing
- Two keyframe animations:
  - `guide-hero-gradient`: Background position shift
  - `guide-hero-float`: Floating accent shapes

### 3. Template (`templates/guides/guide_base.html`)
Wrapped existing header in hero container:
```html
<div class="hero--guide animation-ready fade-in">
  <div class="hero--guide__inner">
    <header class="guide__header">
      <h1 class="guide__title">...</h1>
      <p class="guide__subtitle">...</p>
    </header>
  </div>
</div>
```

## Structure

```
.hero--guide (container with gradient + animations)
  └── .hero--guide__inner (content wrapper, centered, max-width)
      └── .guide__header (existing header styles)
          ├── .guide__title
          └── .guide__subtitle
```

## Color Palette Used
- **Purple accent**: rgba(139, 92, 246, 0.35)
- **Cyan accent**: rgba(34, 211, 238, 0.28)
- **Base gradient**: #1a1b26 → #202a3a

## Accessibility
✅ **Respects prefers-reduced-motion**:
- Disables all animations
- Reduces accent shape opacity to 0.2 (static)
- Content remains fully readable

## Animations
1. **Gradient shift** (15s loop)
   - Smooth background position change
   - Creates subtle color movement
   
2. **Floating shapes** (20s loop each)
   - Gentle vertical movement (-30px)
   - Slight scale change (1.0 → 1.05)
   - Staggered timing (7s delay on second shape)

## Browser Compatibility
- Modern browsers with CSS animations
- Graceful fallback: static gradient background
- No JavaScript required

## Future Guide Pages
All future guide pages automatically inherit this hero header through `guide_base.html`. No additional changes needed per guide.

## Comparison to Main Hero
| Feature | Main Hero | Guide Hero |
|---------|-----------|------------|
| Images | ✅ Background images | ❌ No images |
| Carousel | ✅ 3 slides | ❌ Static |
| CTA Buttons | ✅ Hero CTAs | ❌ Separate CTA section |
| Height | 100vh - 100px | 320-380px |
| Navigation | ✅ Dots + arrows | ❌ N/A |
| Complexity | High | Low |
| Purpose | Homepage impact | Content framing |

## Testing
- [x] Gradient renders correctly
- [x] Animations smooth and subtle
- [x] Responsive sizing works mobile → desktop
- [x] prefers-reduced-motion disables animations
- [x] Content remains readable over gradient
- [x] Scroll animations trigger properly

## Performance Notes
- CSS-only animations (GPU accelerated)
- No images to load
- Minimal DOM impact (2 pseudo-elements)
- No JavaScript overhead
