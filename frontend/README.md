# Frontend Development Guide

## Getting Started

### Prerequisites

- Node.js 18+
- npm or pnpm
- Clerk account

### Installation

```bash
cd frontend

# Install dependencies
npm install
```

### Configuration

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Required environment variables:

| Variable                            | Description           |
| ----------------------------------- | --------------------- |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `CLERK_SECRET_KEY`                  | Clerk secret key      |
| `NEXT_PUBLIC_API_URL`               | Backend API URL       |

### Running Development Server

```bash
npm run dev
```

Visit `http://localhost:3000`

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home page with guest optimizer
│   ├── dashboard/         # Authenticated dashboard
│   ├── sign-in/           # Clerk sign-in
│   └── sign-up/           # Clerk sign-up
├── components/
│   ├── ui/                # Shadcn/UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── header.tsx         # Navigation header
│   ├── footer.tsx         # Site footer
│   ├── prompt-optimizer.tsx  # Main optimizer form
│   ├── score-card.tsx     # Score display component
│   └── optimized-prompt.tsx  # Result display
├── lib/
│   ├── api.ts             # API client
│   └── utils.ts           # Utility functions
└── middleware.ts          # Clerk auth middleware
```

## Components

### PromptOptimizer

The main component for submitting prompts:

```tsx
import { PromptOptimizer } from "@/components/prompt-optimizer";

// Guest mode (no project)
<PromptOptimizer />

// Authenticated with project
<PromptOptimizer
  projectId="uuid-here"
  onResult={(result) => console.log(result)}
/>
```

### ScoreCard

Displays the evaluation score:

```tsx
import { ScoreCard } from "@/components/score-card";

<ScoreCard result={optimizeResponse} />;
```

### OptimizedPrompt

Shows original vs optimized prompt:

```tsx
import { OptimizedPrompt } from "@/components/optimized-prompt";

<OptimizedPrompt originalPrompt="..." optimizedPrompt="..." />;
```

## API Client

The `api.ts` client handles all backend communication:

```typescript
import { api } from "@/lib/api";

// Set auth token (from Clerk)
api.setToken(token);

// Optimize a prompt
const result = await api.optimizePrompt({
  prompt: "...",
  goal: "...",
  force_agent: null, // or "coding", "creative", etc.
  project_id: null, // optional
});

// List agents
const agents = await api.listAgents();

// Project operations (authenticated)
const projects = await api.listProjects();
const project = await api.createProject("My Project");
const history = await api.getPromptHistory(projectId);
```

## Styling

This project uses:

- **Tailwind CSS** for utility-first styling
- **Shadcn/UI** for pre-built components
- **CSS Variables** for theming

### Adding Shadcn Components

Shadcn components are already set up. To add more:

```bash
npx shadcn@latest add <component-name>
```

### Theme Customization

Edit `src/app/globals.css` to customize colors:

```css
:root {
  --primary: 262.1 83.3% 57.8%;
  /* ... */
}

.dark {
  --primary: 263.4 70% 50.4%;
  /* ... */
}
```

## Authentication

Clerk handles all authentication. Protected routes are configured in `middleware.ts`:

```typescript
const isProtectedRoute = createRouteMatcher(["/dashboard(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});
```

### Using Auth in Components

```tsx
"use client";
import { useUser, useAuth } from "@clerk/nextjs";

function MyComponent() {
  const { user, isSignedIn } = useUser();
  const { getToken } = useAuth();

  // Get JWT token for API calls
  const token = await getToken();
}
```

## Building for Production

```bash
npm run build
npm start
```

### Environment Variables

Make sure to set in your hosting platform:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `NEXT_PUBLIC_API_URL` (production backend URL)

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import to Vercel
3. Set environment variables
4. Deploy

### Docker

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```
