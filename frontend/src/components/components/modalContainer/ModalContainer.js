import crossIcon from "Assets/cross.png";
import classnames from "classnames/bind";
import localStyle from "./style.scss";
import React from "react";

const cx = classnames.bind(localStyle);

function ModalContainer(props) {
  const closeHandler = () => {
    document.body.style.overflow = "auto";
    props?.closeHandler && props.closeHandler();
  };

  if (props?.isClosed) return null;
  document.body.style.overflow = "hidden";
  return (
    <div className={cx("modal-page")}>
      <div className={cx("modal-wrapper")}>
        <div className={cx("cross")}>
          <div onClick={closeHandler}>
            <img src={crossIcon} />
          </div>
        </div>
        {props.children}
      </div>
    </div>
  );
}

export default ModalContainer;
