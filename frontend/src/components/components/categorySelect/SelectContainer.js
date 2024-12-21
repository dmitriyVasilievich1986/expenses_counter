import classnames from "classnames/bind";
import SelectValue from "./SelectValue";
import localStyle from "./style.scss";
import classNames from "classnames";
import React from "react";

const cx = classnames.bind(localStyle);

function SelectContainer(props) {
  const [selected, setSelected] = React.useState(null);
  if (!props.objects) return null;

  const isLastContainer = Array.isArray(props.objects);
  const objects = isLastContainer ? props.objects : Object.keys(props.objects);

  return (
    <React.Fragment>
      <div className={cx("container")}>
        {objects.map((o) =>
          isLastContainer ? (
            <SelectValue {...o} key={o.id} onClick={props.onClick} />
          ) : (
            <SelectValue
              className={classNames({ isSelected: o === selected })}
              onMouseEnter={() => setSelected(o)}
              label={o}
              key={o}
            />
          ),
        )}
      </div>
      {selected !== null && (
        <SelectContainer
          objects={props.objects[selected]}
          onClick={props.onClick}
        />
      )}
    </React.Fragment>
  );
}

export default SelectContainer;
