import SelectContainer from "./SelectContainer";
import classnames from "classnames/bind";
import localStyle from "./style.scss";
import classNames from "classnames";
import React from "react";

const cx = classnames.bind(localStyle);

function CategorySelect(props) {
  const [show, setShow] = React.useState(null);
  const cat = {
    cat1: {
      subCat1: [
        { id: 1, name: "subCat1" },
        { id: 2, name: "subCat2" },
        { id: 3, name: "subCat3" },
      ],
    },
    cat2: [
      { id: 1, name: "obj2.1" },
      { id: 2, name: "obj2.2" },
      { id: 3, name: "obj2.3" },
    ],
  };

  return (
    <div
      className={cx("select-wrapper")}
      onMouseLeave={() => setShow(false)}
      onMouseEnter={() => setShow(true)}
    >
      <div>asdasdasd</div>
      {show && (
        <SelectContainer
          objects={cat}
          className={classNames("down")}
          onClick={(e) => console.log("click", e)}
        />
      )}
    </div>
  );
}

export default CategorySelect;
