import React, { FC } from "react";
import {
  Box,
  Button,
  Divider,
  Grid,
  List,
  ListItem,
  Typography,
  styled,
} from "@mui/material";
import { ArticleAnalysis, Counter } from "../schemas";

const StyledUl = styled("ul")(({ theme }) => ({
  paddingTop: theme.spacing(1),
  paddingLeft: theme.spacing(2),
}));

const CounterGrid: FC<{ counter: Counter }> = ({ counter }) => (
    <Grid container spacing={2}>
      <Grid container item xs={12}>
        <Grid item xs={4}>
          <Typography variant="h6">Original Point</Typography>
        </Grid>
        <Grid item xs={8}>
          <Typography variant="body1">{counter.original_view_point}</Typography>
        </Grid>
      </Grid>
      <Grid container item xs={12}>
        <Grid item xs={4}>
          <Typography variant="h6">Counter Point</Typography>
        </Grid>
        <Grid item xs={8}>
          <Typography variant="body1">{counter.counter_view_point}</Typography>
        </Grid>
      </Grid>
      <Grid container item xs={12}>
        <Grid item xs={4}>
          <Typography variant="h6">Arguments</Typography>
        </Grid>
        <Grid item xs={8}>
          <StyledUl>
            {counter.arguments.map((argument) => (
              <li>
                <Typography variant="body1">{argument}</Typography>
              </li>
            ))}
          </StyledUl>
        </Grid>
      </Grid>
    </Grid>
);

const CounterAnalysisSection: FC<{ articleAnalysis?: ArticleAnalysis }> = ({
  articleAnalysis,
}) =>
  articleAnalysis && articleAnalysis.counters ? (
    <Box sx={{ display: "flex", flexDirection: "column" }}>
      <Box
        sx={(theme) => ({
          mt: theme.spacing(1),
          backgroundColor: theme.palette.grey[200],
          borderRadius: theme.spacing(0.5),
        })}
      >
        <Typography
          sx={(theme) => ({
            my: theme.spacing(1),
            ml: theme.spacing(1),
          })}
          variant="h5"
        >
          Counters
        </Typography>
        <List component="ul">
          {articleAnalysis.counters.map((counter) => (
            <ListItem>
                <CounterGrid counter={counter} />
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  ) : (
    <Box
      sx={{ display: "flex", flexDirection: "row", justifyContent: "center" }}
    >
      <Box sx={{ display: "flex", flexDirection: "column" }}>
        <Typography variant="subtitle1">Counter analaysis not found</Typography>
        <Button variant="contained">Generate</Button>
      </Box>
    </Box>
  );

export { CounterAnalysisSection };
