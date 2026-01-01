import { Navbar } from '@components';
import { Home, ShopList, CreateShop } from '@pages';
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
      </Routes>
    </>
  );
}

export default App;
