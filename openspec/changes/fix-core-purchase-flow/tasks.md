## 1. Category Name Display

- [x] 1.1 Update `ProductCard.tsx` to receive `categoria_nombre` prop and display it instead of "Cat. {categoria_id}"
- [x] 1.2 Update `ProductGrid.tsx` to pass `categoria_nombre` to each `ProductCard` by resolving from `useCategories()` hook
- [x] 1.3 Update `ProductDetailPage.tsx` to load categories via `useCategories()` and display the category name instead of "Cat. {categoria_id}"

## 2. Add to Cart on ProductCard

- [x] 2.1 Add "Agregar al carrito" button to `ProductCard.tsx` that calls `useCart().addItem()` with the product data (id, nombre, precio_unitario, imagen_url) and quantity=1
- [x] 2.2 Prevent the button click from triggering the card's link navigation (stopPropagation / separate event handling)

## 3. Add to Cart on ProductDetailPage

- [x] 3.1 Add a quantity selector (numeric input, min=1) to `ProductDetailPage.tsx`
- [x] 3.2 Add "Agregar al carrito" button that calls `useCart().addItem()` with the selected quantity
- [x] 3.3 Add visual feedback after adding (e.g., button text changes to "✓ Agregado" briefly, then reverts)

## 4. Auto-create Cliente on Registration

- [x] 4.1 In `AuthService.register()`, import and create a `Cliente` record with the same nombre, apellido, and email from the registration data, within the same `UnitOfWork` transaction
- [x] 4.2 Add rollback handling: if Cliente creation fails, the entire registration transaction rolls back

## 5. Verification

- [ ] 5.1 Verify full flow: register → see products → add to cart → cart page shows items → checkout flow is accessible (manual: requiere backend + frontend corriendo)
- [ ] 5.2 Verify profile page shows Cliente data immediately after registration (manual: requiere backend + frontend corriendo)
- [ ] 5.3 Run backend tests: `cd backend && pytest` — ensure existing tests still pass (⚠️ pytest no instalado en venv)
- [ ] 5.4 Run frontend tests: `cd frontend && npx vitest run` — ensure existing tests still pass (⚠️ node_modules incompleto por espacio en disco)
