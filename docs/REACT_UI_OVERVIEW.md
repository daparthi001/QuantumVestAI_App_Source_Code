# React UI Overview

QuantumVestAI uses a React-based frontend located under `ai-stock-platform/ui`. The UI relies on **React Router** for page navigation rather than a Python `mainloop`.

## Top Navigation Layout

The persistent menu is implemented in `src/components/layout/Layout.tsx`. It renders a `Navbar` at the top of every page and houses the navigation links. The Layout component wraps all route components so the menu is always visible.

```tsx
// simplified snippet from Layout.tsx
<Navbar expand="lg" className="px-4 py-3">
  <Container fluid>
    <Navbar.Brand as={Link} to={ROUTES.DASHBOARD}>QuantumVestAI</Navbar.Brand>
    <Nav className="ms-auto">
      {/* navigation links */}
    </Nav>
  </Container>
</Navbar>
```

Pages are registered with `react-router-dom` inside `src/main.tsx` and rendered inside `Layout`.

```tsx
<Routes>
  <Route element={<Layout />}>
    <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
    {/* other routes */}
  </Route>
</Routes>
```

Because React handles the routing and rendering cycle, there is no main loop function. The top menu persists across pages automatically.

