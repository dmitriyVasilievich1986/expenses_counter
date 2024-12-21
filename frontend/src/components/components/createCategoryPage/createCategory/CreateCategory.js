import GenericCards from "./GenericCards";
import { connect } from "react-redux";
import { API_URLS } from "Constants";
import className from "classnames";
import React from "react";

function CreateCategory(props) {
  return (
    <GenericCards
      setModalParams={props.setModalParams}
      objects={() => props.categories}
      url={API_URLS.category}
      names="categories"
      name="Categories"
    >
      <GenericCards
        objects={(parentId = null) =>
          props.shops.filter(
            (sh) => parentId === null || sh.category === parentId,
          )
        }
        className={className("shops")}
        url={API_URLS.shop}
        names="shops"
        name="Shops"
      >
        <GenericCards
          objects={(parentId = null) =>
            props.addresses
              .filter((sa) => parentId === null || sa.shop === parentId)
              .map((sa) => ({
                ...sa,
                name: sa.address,
                description: sa.local_name,
              }))
          }
          className={className("addresses")}
          url={API_URLS.address}
          name="Shop Addresses"
          names="addresses"
        />
      </GenericCards>
      <GenericCards
        objects={(parentId = null) =>
          props.subCategories.filter(
            (sc) => parentId === null || sc.category === parentId,
          )
        }
        className={className("subCategories")}
        url={API_URLS.sub_category}
        names="subCategories"
        name="Sub Categories"
      >
        <GenericCards
          objects={(parentId = null) =>
            props.products.filter(
              (p) => parentId === null || p.sub_category === parentId,
            )
          }
          className={className("products")}
          url={API_URLS.product}
          names="products"
          name="Products"
        />
      </GenericCards>
    </GenericCards>
  );
}

const mapStateToProps = (state) => ({
  subCategories: state.main.subCategories,
  categories: state.main.categories,
  addresses: state.main.addresses,
  products: state.main.products,
  shops: state.main.shops,
});

export default connect(mapStateToProps)(CreateCategory);
