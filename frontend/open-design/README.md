# Open Design integration

This project uses **[nexu-io/open-design](https://github.com/nexu-io/open-design)** per course requirement (AI4SE §3.3).

## Design system

- **Brand**: Linear (`design-systems/linear-app`)
- **Skill**: `dashboard` (admin / analytics layout with sidebar)
- **Source**: https://github.com/nexu-io/open-design/tree/main/design-systems/linear-app

Files vendored here:

| File | Upstream |
|------|----------|
| `design-systems/linear-app/tokens.css` | Official CSS token bindings |

React components consume tokens via `src/styles/open-design/components.css` (derived from upstream `components.html`).
