import React, { useState } from "react";

import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Fab from "@mui/material/Fab";

import DialogActions from "@mui/material/DialogActions";
import DialogTitle from "@mui/material/DialogTitle";
import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";

import { APIs, Methods } from "../../api";

export function FormActions(props: {
  url: APIs;
  disabledEdit?: boolean;
  objectId?: string | number;
  submitHandler: (method: Methods.post | Methods.put, url: string) => void;
}) {
  const [open, setOpen] = useState<boolean>(false);

  const handleClose = (agree?: boolean) => {
    setOpen(false);
    if (agree)
      props.submitHandler(Methods.put, `${props.url}${props!.objectId}/`);
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "end", mt: 2 }}>
      <Dialog
        open={open}
        onClose={() => handleClose()}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle textAlign="center">
          Are you sure you want to modify?
        </DialogTitle>
        <DialogActions>
          <Button onClick={() => handleClose()}>Disagree</Button>
          <Button onClick={() => handleClose(true)} autoFocus>
            Agree
          </Button>
        </DialogActions>
      </Dialog>
      <Stack spacing={2} direction="row">
        <Fab
          color="secondary"
          aria-label="EditIcon"
          disabled={props.disabledEdit}
          onClick={(_) => setOpen(true)}
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
