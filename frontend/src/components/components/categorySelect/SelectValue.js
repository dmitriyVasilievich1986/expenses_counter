import classnames from "classnames/bind";
import localStyle from "./style.scss";
import React from "react";

const cx = classnames.bind(localStyle);

function SelectValue(props) {
  const onMouseEnterHandler = () => {
    props?.onMouseEnter && props.onMouseEnter();
  };

  const clickHandler = () => {
    props?.onClick && props.onClick(props);
  };

  return (
    <div
      className={cx("value", props.className)}
      onMouseEnter={onMouseEnterHandler}
      onClick={clickHandler}
    >
      {props.iconURL && <img src={props.iconURL} />}
      {props.label}
    </div>
  );
}

export default SelectValue;
