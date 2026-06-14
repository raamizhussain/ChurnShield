# ChurnShield - Production React Dashboard

## Overview

A premium corporate dark-mode React.js frontend dashboard built with **Next.js 16**, **Tailwind CSS v4**, and **Lucide React** icons. This dashboard provides real-time churn intelligence and causal inference capabilities aligned with the ChurnShield Python backend.

## Architecture Alignment

The frontend is architected to integrate seamlessly with three core backend modules:

### 1. **main_api.py** (FastAPI Endpoints)
- **POST /predict/uplift**: Accepts `CustomerInferencePayload` and returns churn probability + causal uplift scores
- Real-time inference execution on customer cohorts
- Response structure: `{ status, customer_id, computed_metrics }`

### 2. **calculate_velocity_features.py** (Feature Engineering)
- Provides velocity drop metrics (login, click, feature)
- Support friction scoring & click-to-login ratios
- Market friction indexing via competitor sentiment
- Data flows directly into watchlist display logic

### 3. **alert_dispatch_system.py** (CRM Routing)
- P0/P1/P2 priority alert routing
- Retention playbook triggering with CRM sync
- Customer status transition: High-risk → Dispatched → Saved

## Dashboard Tabs & Features

### TAB 1: Executive ROI Management Hub

**Purpose**: Strategic oversight and budget impact simulation

**Components**:
- **4 KPI Cards**:
  - Total Revenue At Risk (rose accent)
  - Saved Capital / Uplift (emerald accent)
  - Campaign Outreach Efficiency (indigo accent)
  - Active Monitored Cohorts (emerald accent)

- **Budget Configuration Module**:
  - Interactive range sliders for retention cost ($50-$500)
  - Average User CLV adjustment ($1K-$10K)
  - Real-time ROI margin simulation
  - Portfolio impact projection card

**Mock Data**: 10 high-risk customers × $2,500 average CLV = $25K total at risk

---

### TAB 2: Tactical Critical Watchlist

**Purpose**: Real-time monitoring of high-risk customer cohort

**Features**:
- **Paginated Data Table** (5 rows per page, 10 total mock records)
- **Conditional Row Styling**:
  - Login velocity ≤ -0.30 → Red (critical churn risk)
  - Support friction ≥ 3.0 → Indigo highlight
  - Days inactive color coded by priority

- **Column Structure**:
  - Customer ID (monospace font)
  - Login Velocity Drop (conditional rose/slate coloring)
  - Support Friction Score (numeric 0-10)
  - Days Inactive (integer days)
  - Priority Status badge (P0/P1/P2 color coded)
  - Action Button (Trigger Retention Playbook)

- **Row Expansion**:
  - Click any row to expand a slide-over panel
  - Shows 6-panel feature breakdown matrix:
    - LOGIN_VELOCITY_DROP
    - SUPPORT_FRICTION
    - DAYS_INACTIVE
    - ESTIMATED_CLV_AT_RISK
    - RECOMMENDED_ACTION
    - CRM_ROUTING

- **Button State Management**:
  - Initial: "Trigger Retention Playbook" (indigo button)
  - Post-click: ✓ "Dispatched to CRM" (emerald badge, disabled)

---

### TAB 3: Causal Inference Sandbox

**Purpose**: Real-time customer churn simulation & uplift modeling

**Form Matrix** (aligns with `CustomerInferencePayload` Pydantic model):

| Field | Type | Default | Range | Purpose |
|-------|------|---------|-------|---------|
| customer_id | Text | CUST_12847 | Any string | Identifier |
| login_velocity_drop | Slider | -0.45 | -1.0 to 0 | Short vs long window login delta |
| click_velocity_drop | Slider | -0.22 | -1.0 to 0 | Click engagement velocity |
| feature_velocity_drop | Slider | -0.10 | -1.0 to 0 | Feature adoption velocity |
| support_friction_score | Number | 3.0 | 0-10 | Support ticket friction metric |
| click_to_login_ratio | Number | 1.25 | 0-10 | Engagement ratio |
| days_since_last_activity | Number | 4 | 0-365 | Inactivity duration |

**Submit Action**:
- "Execute Causal Inference" button (full-width, indigo)
- Loading state with spinner + "Computing causal uplift metrics..." text
- 1.5s simulated latency for realistic UX

**Response Panel** (right column, dynamic rendering):
- Status: "SUCCESS"
- Customer ID (monospace)
- **Computed Metrics**:
  - 30-Day Churn Probability (%) - rose color
  - Causal Uplift Score (float 0-1) - emerald color
  - Action Priority (HIGH/STANDARD) - conditional rose/emerald

---

## Design Language

### Color System (5 colors total)
| Role | Tailwind Class | Hex | Usage |
|------|---|---|---|
| Background | `bg-background` | #0f172a | Page background (slate-900) |
| Surface | `bg-surface` | #1e293b | Card containers (slate-800) |
| Surface Light | `bg-surface-light` | #334155 | Borders & tertiary text (slate-700) |
| Text Primary | `text-foreground` | #e2e8f0 | Main content (slate-100) |
| Emerald Accent | `text-accent-emerald` | #10b981 | Growth, positive metrics |
| Rose Accent | `text-accent-rose` | #f43f5e | Critical risk, churn danger |
| Indigo Accent | `text-accent-indigo` | #6366f1 | Interactive, CTAs, secondary |

### Typography
- **Font Family**: System sans-serif (native browser stack)
- **Headings**: font-bold, sizes from text-lg (h3) to text-4xl (h1)
- **Body**: text-foreground, leading-relaxed
- **Monospace**: Customer IDs and technical fields (font-mono)

### Layout Patterns
- **Flexbox**: Default for horizontal/vertical layouts
- **CSS Grid**: Multi-column KPI cards (grid-cols-4 responsive)
- **Responsive**: `md:`, `lg:` breakpoints for tablet/desktop

---

## Component Hierarchy

```
ChurnShieldDashboard (main component)
├── Header (branding + title)
├── Tab Navigation (3 buttons with state)
├── Tab Content Panels
│   ├── ROI Hub
│   │   ├── KPICard (×4, reusable component)
│   │   ├── Budget Config (sliders)
│   │   └── ROI Projection Card
│   ├── Watchlist
│   │   ├── Paginated Table
│   │   ├── Row Expansion Logic
│   │   ├── CustomerDetailsPanel (×5 visible rows)
│   │   └── Pagination Controls
│   └── Inference
│       ├── Form Inputs (7 fields)
│       ├── Submit Button with loading state
│       └── Response Panel (dynamic JSON rendering)
```

---

## State Management

All state managed with React hooks (`useState`):

```typescript
// Tab navigation
const [activeTab, setActiveTab] = useState<'roi' | 'watchlist' | 'inference'>('roi')

// Budget sliders
const [retentionCost, setRetentionCost] = useState(150)
const [averageClv, setAverageClv] = useState(2500)

// Watchlist pagination & expansion
const [pageIndex, setPageIndex] = useState(0)
const [expandedRowId, setExpandedRowId] = useState<string | null>(null)

// Retention dispatch tracking
const [dispatchedCustomers, setDispatchedCustomers] = useState<Set<string>>(new Set())

// Inference form & results
const [inferenceForm, setInferenceForm] = useState<InferencePayload>({...})
const [inferenceLoading, setInferenceLoading] = useState(false)
const [inferenceResult, setInferenceResult] = useState<InferenceResponse | null>(null)
```

---

## Mock Data & API Simulation

### Watchlist Mock Data
10 customer records with realistic churn signals:
```javascript
[
  { customer_id: 'CUST_00451', login_velocity_drop: -0.42, support_friction_score: 4.2, days_inactive: 12, priority_status: 'P0' },
  { customer_id: 'CUST_00892', login_velocity_drop: -0.38, support_friction_score: 3.8, days_inactive: 8, priority_status: 'P0' },
  // ... 8 more records
]
```

### Inference API Simulation
- 1.5s artificial latency (`setTimeout`)
- Simulated churn probability calculation:
  ```javascript
  simulated_churn = min(0.99, (days_since_last_activity * 0.12) + abs(login_velocity_drop * 0.35))
  simulated_lift = (abs(login_velocity_drop) * 0.45) + (support_friction_score * 0.05)
  ```
- **Action Priority**: HIGH if uplift > 0.15, else STANDARD

---

## Installation & Development

### Prerequisites
- Node.js 18+ (includes npm)
- Git

### Setup

```bash
# Clone repo
git clone https://github.com/raamizhussain/ChurnShield.git
cd ChurnShield

# Install dependencies
npm install

# Start dev server
npm run dev

# Open browser
open http://localhost:3000
```

### Build for Production

```bash
npm run build
npm start
```

---

## Integration with Backend

### Future API Endpoints

**1. Watchlist Data Fetch**
```javascript
// Replace mock data with:
const response = await fetch('/api/customers/critical-risk')
const mockWatchlistData = await response.json()
```

**2. Inference Submission**
```javascript
const response = await fetch('http://localhost:8000/predict/uplift', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(inferenceForm)
})
const result = await response.json()
setInferenceResult(result)
```

**3. Retention Dispatch**
```javascript
// POST to CRM sync endpoint
await fetch('/api/crm/dispatch-retention', {
  method: 'POST',
  body: JSON.stringify({ customer_id, action: 'trigger_retention_playbook' })
})
```

---

## Performance Optimization

- **Client-side state**: No external API calls until integration phase
- **Memoization**: `useMemo` for KPI calculations (savedValue, ROI margin)
- **Lazy rendering**: Table pagination limits DOM nodes
- **CSS**: Tailwind v4 with minimal unused selectors

---

## Accessibility

- Semantic HTML (`<header>`, `<main>`, role attributes)
- ARIA labels on interactive elements
- Keyboard navigation on sliders and buttons
- Color contrast compliance (WCAG AA) on all text

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Deployment

### Vercel (Recommended)
```bash
vercel link
vercel deploy
```

### Docker
```bash
docker build -t churnshield-frontend .
docker run -p 3000:3000 churnshield-frontend
```

### Environment Variables
None required for development. For production:
- `NEXT_PUBLIC_API_URL`: Backend FastAPI endpoint (when integrating with /predict/uplift)

---

## File Structure

```
.
├── app/
│   ├── layout.tsx           # Root layout with metadata
│   ├── globals.css          # Tailwind directives + custom CSS
│   ├── page.tsx             # Home page (renders ChurnShieldDashboard)
│   └── favicon.ico
├── components/
│   └── ChurnShieldDashboard.tsx  # Main dashboard component (621 lines, fully modularized)
├── public/                  # Static assets
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind theme extensions
├── tsconfig.json            # TypeScript configuration
├── postcss.config.js        # PostCSS + Tailwind v4 setup
├── package.json             # Dependencies & scripts
└── FRONTEND_README.md       # This file
```

---

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| next | ^16.2.9 | React framework |
| react | ^19.2.7 | UI library |
| react-dom | ^19.2.7 | DOM rendering |
| tailwindcss | ^4.3.1 | CSS utilities |
| @tailwindcss/postcss | Latest | PostCSS plugin for v4 |
| lucide-react | ^1.18.0 | Icon components |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

ISC - See LICENSE file for details.

---

## Support & Questions

For backend integration questions, refer to:
- `main_api.py` - FastAPI endpoint specifications
- `calculate_velocity_features.py` - Feature definitions
- `alert_dispatch_system.py` - CRM routing & alert structure

For frontend technical issues:
- Check Next.js docs: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com
- Lucide Icons: https://lucide.dev

---

**Last Updated**: June 14, 2026  
**Status**: Production Ready  
**Version**: 1.0.0
