import { useSelector, useDispatch } from "react-redux";
import { setModal } from "Reducers/mainReducer";
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
      case "Delete":
        return <DeletePage />;
      case "newProduct":
      default:
        return <NewProduct />;
    }
  };

  if (modal === null) return null;
  return (
    <div
      style={{
        justifyContent: "center",
        alignItems: "center",
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
          maxHeight: "500px",
          maxWidth: "500px",
        }}
      >
        <ModalChoice />
      </div>
    </div>
  );
}

export default ModalPage;
