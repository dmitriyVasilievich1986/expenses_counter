import React from "react";
import dayjs from "dayjs";

import MoreVertIcon from "@mui/icons-material/MoreVert";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import CardHeader from "@mui/material/CardHeader";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import Avatar from "@mui/material/Avatar";
import Grid from "@mui/material/Grid2";
import Card from "@mui/material/Card";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { Params } from "../../components/link";
import { roundToTwo } from "../../support";

import { TransactionTypeNumber } from "../../pages/transactionsPage/types";
import { ShopAddressTypeNumber } from "../shopsPage/types";

export function ShopCard(props: {
  address: ShopAddressTypeNumber;
  transactions: TransactionTypeNumber[];
}) {
  const params = new Params();

  return (
    <Card sx={{ my: 4 }}>
      <CardHeader
        avatar={
          props.address?.icon ? (
            <img
              src={props.address.icon}
              style={{ height: "30px", width: "30px" }}
            />
          ) : (
            <Avatar>props.address.local_name[0]</Avatar>
          )
        }
        action={
          <IconButton aria-label="settings">
            <MoreVertIcon />
          </IconButton>
        }
        title={props.address.local_name}
        subheader={dayjs(params.currentDate, "YYYY-MM-DD").format(
          "dddd, MMMM D, YYYY",
        )}
      />
      <CardContent>
        <List>
          {props.transactions.map((t) => (
            <Grid container spacing={2} key={t.id} sx={{ my: 1 }}>
              <Grid size={8} sx={{ pl: "1rem" }}>
                <Typography variant="subtitle2">{t.product.name}</Typography>
              </Grid>
              <Grid size={4}>
                {roundToTwo(t.price)}€ * {roundToTwo(t.count)}
              </Grid>
            </Grid>
          ))}
        </List>
      </CardContent>
      <CardActions>
        <Box sx={{ m: "0 5rem 2rem auto" }}>
          <Typography variant="h6">
            Summary:{" "}
            {roundToTwo(
              props.transactions.reduce((acc, t) => acc + t.price * t.count, 0),
            )}
            €
          </Typography>
        </Box>
      </CardActions>
    </Card>
  );
}
