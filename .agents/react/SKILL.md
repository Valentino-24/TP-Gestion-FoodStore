---
name: react
description: React conventions with TypeScript (2024-2026)
---

# React Conventions (React 18/19 + TypeScript)

## Core Principles

- **Components are functions**
- **Composition over inheritance**
- **Unidirectional data flow**
- **Immutable state updates**

## Modern React (18/19)

- **Server Components**: Default in Next.js App Router
- **Suspense**: For async data loading
- **Transitions**: `useTransition` for non-urgent updates
- **Actions**: Form handling with `useActionState`

## Component Structure

```tsx
// imports
import { useState, useCallback } from "react";
import type { User } from "@/types";

// types
interface Props {
  user: User;
  onUpdate: (user: User) => void;
}

// component
export function UserCard({ user, onUpdate }: Props) {
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = useCallback(() => {
    // ...
  }, []);

  return <div>{/* JSX */}</div>;
}
```

## Hooks Rules

- Only call at top level
- Only call in React functions
- Custom hooks start with `use`
- Extract complex logic to custom hooks

## State Management

- `useState` for local state
- `useReducer` for complex local state
- `useContext` for prop drilling
- Zustand/Jotai for global state (over Redux)
- TanStack Query for server state

## Performance

- `useMemo` for expensive calculations
- `useCallback` for stable function refs
- `React.memo` for pure components
- Virtualization for long lists

## Patterns

```tsx
// Compound components
<Tabs>
  <Tabs.List>
    <Tabs.Tab>One</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panels>
    <Tabs.Panel>Content</Tabs.Panel>
  </Tabs.Panels>
</Tabs>

// Render props (rare now)
<DataFetcher render={(data) => <Display data={data} />} />

// Custom hooks (preferred)
const { data, isLoading } = useUsers()
```

## File Structure

```
components/
  Button/
    Button.tsx
    Button.test.tsx
    index.ts
hooks/
  useAuth.ts
lib/
  api.ts
types/
  index.ts
```

## Testing

- Vitest + React Testing Library
- Test behavior, not implementation
- `userEvent` over `fireEvent`

## Tools

- ESLint + eslint-plugin-react-hooks
- Prettier for formatting

## Reference Docs

- React Docs: https://react.dev/
- TypeScript + React: https://react-typescript-cheatsheet.netlify.app/
- TanStack Query: https://tanstack.com/query