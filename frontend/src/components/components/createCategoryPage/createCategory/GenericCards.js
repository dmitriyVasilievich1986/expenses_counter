import { updateState } from "Reducers/mainReducer";
import { connect } from "react-redux";
import { API_URLS } from "Constants";
import Card from "../../card/Card";
import className from "classnames";
import React from "react";

function GenericCards(props) {
  const addHandler = (newObject) => {
    props.updateState({
      [props.names]: [...props.objects(), newObject.data],
    });
  };
  const updateHandler = (newObject) => {
    props.updateState({
      [props.names]: props
        .objects()
        .map((o) => (o.id === newObject.data.id ? newObject.data : o)),
    });
  };
  const deleteHandler = (id) => {
    props.updateState({
      [props.names]: props.objects().filter((o) => o.id !== id),
    });
  };

  let childrens = null;
  if (Array.isArray(props?.children)) {
    childrens = props.children;
  } else if (props?.children !== undefined) {
    childrens = [props.children];
  }

  const additionalData = {};
  if (props.url === API_URLS.sub_category || props.url === API_URLS.shop) {
    additionalData["category"] = props.parentId;
  } else if (props.url === API_URLS.product) {
    additionalData["sub_category"] = props.parentId;
  } else if (props.url === API_URLS.address) {
    additionalData["shop"] = props.parentId;
  }

  return (
    <Card
      className={className("main", props?.className)}
      name={props.name}
      createHandler={() =>
        props.setModalParams({
          url: props.url,
          submitHandler: addHandler,
          data: additionalData,
          axiosParams: {
            url: props.url,
            method: "post",
          },
        })
      }
    >
      {props.objects(props.parentId).map((o) => (
        <Card
          key={o.id}
          name={o.name}
          className={props?.className}
          deleteHandler={() =>
            props.setModalParams({
              url: props.url,
              submitHandler: () => deleteHandler(o.id),
              axiosParams: {
                url: `${props.url}${o.id}/`,
                method: "delete",
              },
            })
          }
          updateHandler={() =>
            props.setModalParams({
              name: o.name,
              url: props.url,
              data: additionalData,
              submitHandler: updateHandler,
              description: o?.description || "",
              axiosParams: {
                url: `${props.url}${o.id}/`,
                method: "put",
              },
            })
          }
        >
          {childrens &&
            childrens.map((c, i) => (
              <React.Fragment key={i}>
                {React.cloneElement(c, {
                  setModalParams: props.setModalParams,
                  parentId: o.id,
                })}
              </React.Fragment>
            ))}
        </Card>
      ))}
    </Card>
  );
}

export default connect(null, { updateState })(GenericCards);
