import SelectContainer from "./SelectContainer";
import classnames from "classnames/bind";
import localStyle from "./style.scss";
import classNames from "classnames";
import React from "react";

const cx = classnames.bind(localStyle);

function CategorySelect(props) {
  const [show, setShow] = React.useState(null);

  const clickHandler = (e) => {
    setShow(false);
    props?.onClick && props.onClick(e);
  };

  return (
    <div
      onMouseLeave={() => setShow(false)}
      onMouseEnter={() => setShow(true)}
      className={cx("select-wrapper")}
    >
      <div className={cx("selected-value")}>{props.value}</div>
      {show && (
        <SelectContainer
          className={classNames("down")}
          objects={props.objects}
          onClick={clickHandler}
        />
      )}
    </div>
  );
}

export default CategorySelect;
