/**
 * Root application shell: navigation bar, React Router routes, and lazy-loaded page bundles behind Suspense.
 */
import { Navbar } from '@components';
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router';

const Home = lazy(() => import('@pages/home').then((m) => ({ default: m.Home })));
const Login = lazy(() => import('@pages/login').then((m) => ({ default: m.Login })));
const ShopList = lazy(() => import('@pages/shop').then((m) => ({ default: m.ShopList })));
const CreateShop = lazy(() => import('@pages/shop').then((m) => ({ default: m.CreateShop })));
const ProductList = lazy(() => import('@pages/product').then((m) => ({ default: m.ProductList })));
const CreateProduct = lazy(() =>
  import('@pages/product').then((m) => ({ default: m.CreateProduct }))
);
const TransactionPage = lazy(() =>
  import('@pages/transaction').then((m) => ({ default: m.TransactionPage }))
);

/**
 * Wires URL paths to page components: home, login, nested shop/product CRUD routes, and transaction views.
 *
 * @returns {JSX.Element} Navbar plus routed lazy content (no visible Suspense fallback).
 */
function App() {
  return (
    <>
      <Navbar />
      <Suspense fallback={null}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/shop">
            <Route index element={<ShopList />} />
            <Route path="create" element={<CreateShop />} />
            <Route path=":shopId" element={<CreateShop />} />
          </Route>
          <Route path="/product">
            <Route index element={<ProductList />} />
            <Route path="create" element={<CreateProduct />} />
            <Route path=":productId" element={<CreateProduct />} />
          </Route>
          <Route path="/transaction">
            <Route index element={<TransactionPage />} />
            <Route path=":transactionId" element={<TransactionPage />} />
          </Route>
        </Routes>
      </Suspense>
    </>
  );
}

export default App;
