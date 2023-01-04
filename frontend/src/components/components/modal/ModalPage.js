import { useSelector, useDispatch } from "react-redux";
import { setModal } from "Reducers/mainReducer";
import { MODAL_PAGES } from "Constants";
import NewProduct from "./NewProduct";
import DeletePage from "./DeletePage";
import React from "react";

function ModalPage() {
  const modal = useSelector((state) => state.main.modal);
  const modalRef = React.useRef();
  const dispatch = useDispatch();

  React.useEffect(() => {
    function handleClickOutside(event) {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        dispatch(setModal(null));
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [modalRef]);

  const ModalChoice = (_) => {
    switch (modal) {
      case MODAL_PAGES.deletePage:
        return <DeletePage />;
      case MODAL_PAGES.newProductPage:
        return <NewProduct />;
      default:
        return null;
    }
  };

  if (modal === null) return null;
  return (
    <div
      style={{
        justifyContent: "center",
        backgroundColor: "gray",
        position: "absolute",
        display: "flex",
        height: "100vh",
        width: "100vw",
        left: "0",
        top: "0",
      }}
    >
      <div
        ref={modalRef}
        style={{
          backgroundColor: "white",
          height: "max-content",
          marginTop: "5rem",
        }}
      >
        <ModalChoice />
      </div>
    </div>
  );
}

export default ModalPage;
