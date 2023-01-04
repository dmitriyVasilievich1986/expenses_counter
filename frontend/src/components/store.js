import { configureStore } from "@reduxjs/toolkit";
import mainReducer from "Reducers/mainReducer";

export default configureStore({
  reducer: {
    main: mainReducer,
  },
});
