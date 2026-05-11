/**
 * Barrel module for the product pages: re-exports {@link ProductList} and {@link CreateProduct} from `./productList` and `./createProduct`.
 *
 * @module pages/product/index
 */

import { CreateProduct } from './createProduct';
import { ProductList } from './productList';

export { ProductList, CreateProduct };
