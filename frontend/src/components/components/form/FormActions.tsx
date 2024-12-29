import React from "react";

import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Fab from "@mui/material/Fab";

import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";

import { API_URLS } from "../../Constants";

export function FormActions(props: {
  url: API_URLS;
  disabledEdit?: boolean;
  objectId?: string | number;
  submitHandler: (method: "post" | "put", url: string) => void;
}) {
  return (
    <Box sx={{ display: "flex", justifyContent: "end", mt: 2 }}>
      <Stack spacing={2} direction="row">
        <Fab
          color="secondary"
          aria-label="EditIcon"
          disabled={props.disabledEdit}
          onClick={(_) =>
            props.submitHandler("put", `${props.url}${props!.objectId}/`)
          }
        >
          <EditIcon />
        </Fab>
        <Fab
          color="primary"
          aria-label="add"
          onClick={(_) => props.submitHandler("post", props.url)}
        >
          <AddIcon />
        </Fab>
      </Stack>
    </Box>
  );
}
