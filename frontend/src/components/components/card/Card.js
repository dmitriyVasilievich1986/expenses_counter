import classnames from "classnames/bind";
import downIcon from "Assets/down.png";
import localStyle from "./style.scss";
import binIcon from "Assets/bin.png";
import penIcon from "Assets/pen.png";
import addIcon from "Assets/add.png";
import React from "react";

const cx = classnames.bind(localStyle);

function ActionButton(props) {
  if (!props?.action) return null;
  return <img src={props.icon} onClick={props.action} className={cx("icon")} />;
}

function Card(props) {
  const [hide, setHide] = React.useState(true);

  return (
    <div className={cx("card", ...(props?.className?.split(" ") || []))}>
      <div className={cx("head", { hide })}>
        <div className={cx("open")} onClick={() => setHide((h) => !h)}>
          {props?.children && (
            <img src={downIcon} className={cx("icon", { hide: !hide })} />
          )}
        </div>
        <div className={cx("name")}>{props.name}</div>
        <div className={cx("actions")}>
          <ActionButton action={props.updateHandler} icon={penIcon} />
          <ActionButton action={props.deleteHandler} icon={binIcon} />
        </div>
      </div>
      <div className={cx("inner", { hide })}>
        <React.Fragment>{props.children}</React.Fragment>
        <div className={cx("create")}>
          <ActionButton action={props.createHandler} icon={addIcon} />
        </div>
      </div>
    </div>
  );
}

export default Card;
