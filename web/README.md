# Galatus web (Next.js)

Static pages from [`galatus-html/`](../galatus-html/) converted to the Next.js App Router.

## Docker (from repo root)

```bash
docker compose up -d --build
```

Frontend: [http://localhost:3000](http://localhost:3000)  
Postgres: `localhost:5433`

## Develop (hot reload)

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Routes

| Path | Source HTML |
|------|-------------|
| `/` | `index.html` (Runs) |
| `/repositories` | `repositories.html` |
| `/prds` | `prds.html` |
| `/new-run` | `new-run.html` |
| `/run-detail` | `run-detail.html` |
| `/settings` | `settings.html` |

## Structure

- Shared chrome: [`src/components/AppHeader.tsx`](src/components/AppHeader.tsx)
- Runs filters (client): [`src/components/RunsList.tsx`](src/components/RunsList.tsx)
- New-run mode/switches (client): [`src/components/OutputModePicker.tsx`](src/components/OutputModePicker.tsx)
- Design CSS (from HTML): [`src/app/globals.css`](src/app/globals.css)
- Fonts: [`public/fonts/`](public/fonts/)
