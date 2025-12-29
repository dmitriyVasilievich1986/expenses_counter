import { Navbar } from '@components';
import { Home, ShopList } from '@pages';
import { Routes, Route } from 'react-router';

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/shop">
          <Route index element={<ShopList />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
