import React from "react";

import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Fab from "@mui/material/Fab";

import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";

import { APIs, Methods } from "../../api";

export function FormActions(props: {
  url: APIs;
  disabledEdit?: boolean;
  objectId?: string | number;
  submitHandler: (method: Methods.post | Methods.put, url: string) => void;
}) {
  return (
    <Box sx={{ display: "flex", justifyContent: "end", mt: 2 }}>
      <Stack spacing={2} direction="row">
        <Fab
          color="secondary"
          aria-label="EditIcon"
          disabled={props.disabledEdit}
          onClick={(_) =>
            props.submitHandler(Methods.put, `${props.url}${props!.objectId}/`)
          }
        >
          <EditIcon />
        </Fab>
        <Fab
          color="primary"
          aria-label="add"
          onClick={(_) => props.submitHandler(Methods.post, props.url)}
        >
          <AddIcon />
        </Fab>
      </Stack>
    </Box>
  );
}
