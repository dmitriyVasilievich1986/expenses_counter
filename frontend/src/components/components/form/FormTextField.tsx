import React from "react";

import TextField from "@mui/material/TextField";

export function FormTextField(props: {
  onChange?: (value: string) => void;
  isChanged?: boolean;
  value?: string;
  label: string;
}) {
  const onChangeHandler = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (props?.onChange) {
      props.onChange(e.target.value);
    }
  };

  return (
    <TextField
      onChange={onChangeHandler}
      label={props.label}
      value={props.value}
      fullWidth
      color={props.isChanged ? "warning" : "primary"}
      focused={props.isChanged ? true : undefined}
    />
  );
}
