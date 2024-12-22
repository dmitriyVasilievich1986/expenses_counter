import React, { ReactElement } from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";

import { FormTextField } from "./FormTextField";
import { FormActions } from "./FormActions";

export function Form(props: {
  title?: string;
  children: ReactElement<typeof FormTextField | typeof FormActions>[];
}) {
  return (
    <Paper elevation={4} sx={{ p: 2 }}>
      {props?.title && (
        <Typography variant="h5" align="center" sx={{ mb: 3 }}>
          {props.title}
        </Typography>
      )}
      <Stack spacing={2}>
        {props.children.filter(
          (c) => c.type === FormTextField || c.type === Autocomplete,
        )}
      </Stack>
      {props.children.find((c) => c.type === FormActions)}
    </Paper>
  );
}
