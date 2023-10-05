import React, { FC } from "react";
import {
  Box,
  Button,
  Divider,
  List,
  ListItem,
  Typography,
  styled,
} from "@mui/material";
import { ArticleAnalysis, Viewpoint } from "../schemas";

const StyledUl = styled("ul")(({ theme }) => ({
  paddingTop: theme.spacing(1),
  paddingLeft: theme.spacing(2),
}));

const ViewPointBox: FC<{ viewpoint: Viewpoint }> = ({ viewpoint }) => (
  <Box
    sx={(theme) => ({
      p: theme.spacing(1),
      borderRadius: theme.spacing(0.5),
      backgroundColor: theme.palette.grey[100],
      "&:hover": {
        backgroundColor: theme.palette.primary.contrastText,
      },
    })}
  >
    <Typography variant="h6">{viewpoint.point}</Typography>
    <Divider />
    <StyledUl>
      {viewpoint.arguments.map((argument) => (
        <li>
          <Typography variant="body1">{argument}</Typography>
        </li>
      ))}
    </StyledUl>
  </Box>
);

const BaseAnalysisSection: FC<{ articleAnalysis?: ArticleAnalysis }> = ({
  articleAnalysis,
}) =>
  articleAnalysis && articleAnalysis.analysis ? (
    <Box sx={{ display: "flex", flexDirection: "column" }}>
      <Box
        sx={(theme) => ({
          display: "flex",
          flexDirection: "row",
          borderRadius: theme.spacing(0.5),
          p: theme.spacing(1),
          backgroundColor: theme.palette.primary.main,
          color: theme.palette.primary.contrastText,
          "&:hover": {
            backgroundColor: theme.palette.primary.light,
          },
        })}
      >
        <Typography sx={{ alignSelf: "center" }} variant="h5">
          Subject
        </Typography>
        <Divider
          orientation="vertical"
          sx={(theme) => ({ mx: theme.spacing(1) })}
          flexItem
        />
        <Typography
          sx={{ alignSelf: "center", textAlign: "left" }}
          variant="subtitle1"
        >
          {articleAnalysis.analysis.subject}
        </Typography>
      </Box>
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
          View Points
        </Typography>
        <List component="ul">
          {articleAnalysis.analysis.view_points.map((viewpoint) => (
            <ListItem>
              <ViewPointBox viewpoint={viewpoint} />
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
        <Typography variant="subtitle1">Analaysis not found</Typography>
        <Button variant="contained">Generate</Button>
      </Box>
    </Box>
  );

export { BaseAnalysisSection };
