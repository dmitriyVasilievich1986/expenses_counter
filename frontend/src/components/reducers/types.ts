import { TransactionTypeNumber } from "../pages/transactionsPage/types";
import { ProductTypeDetailed } from "../pages/productsPage/types";
import { CategoryTypeNumber } from "../pages/categoryPage/types";
import { messageType } from "../components/alert/types";
import {
  ShopAddressTypeNumber,
  ShopTypeNumber,
} from "../pages/shopsPage/types";

export type mainStateType = {
  message: messageType | null;
  isLoading: boolean;
  transactions: TransactionTypeNumber[];
  addresses: ShopAddressTypeNumber[];
  categories: CategoryTypeNumber[];
  products: ProductTypeDetailed[];
  shops: ShopTypeNumber[];
};

export type mainStateOptionalType = Partial<mainStateType>;
export type mainSelectorType = { main: mainStateType };
