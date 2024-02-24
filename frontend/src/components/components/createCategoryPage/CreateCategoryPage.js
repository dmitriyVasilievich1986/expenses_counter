import CreateCategoryModal from "./CreateCategoryModal";
import CreateCategory from "./createCategory";
import classnames from "classnames/bind";
import localStyle from "./style.scss";
import React from "react";

const cx = classnames.bind(localStyle);

function CreateCategoryPage(props) {
  const [modalParams, setModalParams] = React.useState({});

  return (
    <React.Fragment>
      <CreateCategoryModal
        {...modalParams}
        closeHandler={() => setModalParams({})}
      />
      <div className={cx("create-category-page")}>
        <div className={cx("center")}>
          <div className={cx("wrapper")}>
            <CreateCategory setModalParams={setModalParams} />
          </div>
        </div>
      </div>
    </React.Fragment>
  );
}

export default CreateCategoryPage;
