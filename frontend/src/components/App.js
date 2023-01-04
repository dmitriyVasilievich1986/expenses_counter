import Select from "./Select/Select";
import React from "react";
import axios from "axios";

function App() {
  const [shops, setShops] = React.useState([{ id: 0, name: "null" }]);
  const [shop, setShop] = React.useState({ id: 0, name: "null" });
  const [products, setProducts] = React.useState([{ id: 0, name: "null" }]);
  const [product, setProduct] = React.useState({ id: 0, name: "null" });
  const [subCategories, setSubCategories] = React.useState([
    { id: 0, name: "null" },
  ]);
  const [subCategory, setSubCategory] = React.useState({ id: 0, name: "null" });
  const [date, setDate] = React.useState(
    new Date().toISOString().split("T")[0]
  );
  const [price, setPrice] = React.useState(0);

  React.useEffect((_) => {
    axios
      .get("/expenses/shop/")
      .then((data) => {
        setShops(data.data);
        setShop(data.data[0]);
      })
      .catch((e) => console.log(e));
    axios
      .get("/expenses/product/")
      .then((data) => {
        setProducts(data.data);
        setProduct(data.data[0]);
      })
      .catch((e) => console.log(e));
    axios
      .get("/expenses/sub_category/")
      .then((data) => {
        setSubCategories(data.data);
        setSubCategory(data.data[0]);
      })
      .catch((e) => console.log(e));
  }, []);

  const sendHandler = (e) => {
    e.preventDefault();
    const newData = {
      price: price,
      shop: shop.id,
      date: String(date),
      product: product.id,
      sub_category: subCategory.id,
    };
    axios
      .post("/expenses/transaction/", newData)
      .then((data) => {
        console.log(data.data);
      })
      .catch((e) => console.log(e));
    // console.log(newData);
  };

  return (
    <div>
      <form onSubmit={sendHandler}>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <div style={{ width: "300px" }}>
          <Select
            changeHandler={(e) => setShop(e)}
            items={shops}
            value={shop}
          />
          <Select
            changeHandler={(e) => setSubCategory(e)}
            items={subCategories}
            value={subCategory}
          />
          <Select
            changeHandler={(e) => setProduct(e)}
            items={products}
            value={product}
          />
        </div>
        <input
          onChange={(e) => setPrice(e.target.value)}
          value={price}
          type="number"
          step="any"
        />
        <button onClick={sendHandler}>send</button>
      </form>
    </div>
  );
}

export default App;
