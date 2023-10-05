import React, { FC } from "react";
import { Source, SourceItem } from "../schemas";
import {
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  Typography,
  Theme,
  SxProps,
  CardActions,
  Button,
  Box,
  Chip,
  Divider,
} from "@mui/material";
import { Bolt } from "@mui/icons-material";
import moment from 'moment';

interface SourceItemsViewProps {
  sources: Array<Source>;
  items: Array<SourceItem>;
  onMoreDetail: (item: SourceItem) => void;
  sx?: SxProps<Theme>;
}

const AuthorChips: FC<{ authors: Array<string> }> = ({ authors }) => (
  <Box
    component="div"
    sx={{
      display: "flex",
      flexDirection: "row",
    }}
  >
    {authors.map((author) => (
      <Chip
        key={authors.indexOf(author)}
        sx={(theme) => ({
          mr: theme.spacing(1),
        })}
        label={author}
        variant="filled"
      />
    ))}
  </Box>
);

const Subheader: FC<{
  authors: Array<string>;
  sourceName: string;
  posted: number;
  updated: number;
}> = ({ authors, sourceName, posted, updated }) => (
  <Box
    sx={{
      display: "flex",
      flexDirection: "row",
    }}
  >
    <Typography
      sx={(theme) => ({
        textAlign: "center",
        alignSelf: "center",
        mr: theme.spacing(1)
      })}
      variant="subtitle1"
    >
      Authors
    </Typography>
    <AuthorChips authors={authors} />
    <Divider
      sx={(theme) => ({
        mx: theme.spacing(1),
      })}
      orientation="vertical"
      flexItem
    />
    <Typography
      sx={{
        textAlign: "center",
        alignSelf: "center",
      }}
      variant="subtitle1"
    >
      {sourceName}
    </Typography>
    <Divider
      sx={(theme) => ({
        mx: theme.spacing(1),
      })}
      orientation="vertical"
      flexItem
    />
    <Typography
      sx={(theme) => ({
        textAlign: "center",
        alignSelf: "center",
        mr: theme.spacing(1)
      })}
      variant="subtitle1"
    >
      Posted
    </Typography>
    <Typography
      sx={{
        textAlign: "center",
        alignSelf: "center",
      }}
      variant="subtitle2"
    >
      {moment(posted).format()}
    </Typography>
    <Divider
      sx={(theme) => ({
        mx: theme.spacing(1),
      })}
      orientation="vertical"
      flexItem
    />
    <Typography
      sx={(theme) => ({
        textAlign: "center",
        alignSelf: "center",
        ml: theme.spacing(1),
        mr: theme.spacing(1)
      })}
      variant="subtitle1"
    >
      Updated
    </Typography>
    <Typography
      sx={{
        textAlign: "center",
        alignSelf: "center",
      }}
      variant="subtitle2"
    >
      {moment(updated).format()}
    </Typography>
  </Box>
);

const SourceItemCard: FC<{
  item: SourceItem;
  source: Source;
  onMoreDetail: (item: SourceItem) => void;
}> = ({ item, source, onMoreDetail }) => (
  <Card>
    <CardHeader
      title={item.title}
      subheader={
        <Subheader
          authors={item.authors}
          sourceName={source.title}
          posted={item.postedTimestamp}
          updated={item.updatedTimestamp}
        />
      }
    />
    <CardContent>
      <Typography variant="body1">{item.content}</Typography>
    </CardContent>
    <CardActions>
      <Button variant="contained" onClick={(_) => onMoreDetail(item)}>
        <Bolt />
        Analysis
      </Button>
    </CardActions>
  </Card>
);

const SourceItemsView = ({
  sources,
  items,
  onMoreDetail,
  sx,
}: SourceItemsViewProps) => {
  return (
    <Box>
      <List sx={sx}>
        {items.map((item) => {
          let source = sources.filter(
            (src) => src.uuid === item.source_uuid,
          )[0];

          return (
            <ListItem key={item.uuid}>
              <SourceItemCard
                source={source}
                item={item}
                onMoreDetail={onMoreDetail}
              />
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
};

export { SourceItemsView, SourceItemsViewProps };
