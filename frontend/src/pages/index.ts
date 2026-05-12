/**
 * Barrel module for the pages: re-exports {@link Home}, {@link ShopList}, {@link CreateShop}, {@link ProductList}, {@link CreateProduct}, {@link TransactionPage}, {@link Login} from `./home`, `./product`, `./shop`, `./transaction`, `./login`.
 *
 * @module pages/index
 */

import { Home } from './home';
import { Login } from './login';
import { ProductList, CreateProduct } from './product';
import { ShopList, CreateShop } from './shop';
import { TransactionPage } from './transaction';

export { Home, ShopList, CreateShop, ProductList, CreateProduct, TransactionPage, Login };
