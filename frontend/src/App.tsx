import { Navbar } from '@components';
import { Home, ShopList, CreateShop } from '@pages';
import { ProductList, CreateProduct } from '@pages/product';
import { Routes, Route } from 'react-router';

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
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
      </Routes>
    </>
  );
}

export default App;
