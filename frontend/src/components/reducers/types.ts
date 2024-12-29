import { ProductTypeDetailed } from "../pages/productsPage/types";
import { ShopAddressTypeNumber } from "../pages/shopsPage/types";
import { CategoryTypeNumber } from "../pages/categoryPage/types";
import { messageType } from "../components/alert/types";

export type mainStateType = {
  isLoading: boolean;
  message: messageType | null;
  products: ProductTypeDetailed[];
  categories: CategoryTypeNumber[];
  addresses: ShopAddressTypeNumber[];
};

export type mainStateOptionalType = Partial<mainStateType>;
