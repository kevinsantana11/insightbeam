import React from "react";
import { Source } from "../schemas";
import {
  Box,
  Button,
  Divider,
  Drawer,
  Icon,
  IconButton,
  List,
  ListItem,
  TextField,
  Toolbar,
  Typography,
} from "@mui/material";
import {
  Add,
  Article,
  Cancel,
  Check,
  ChevronLeft,
  Download,
} from "@mui/icons-material";

interface SourceActions {
  add: () => void;
  confirm: (url: string) => void;
  cancel: () => void;
}

interface DisplayActions {
  onClose: () => void;
}

interface SourceDrawerProps {
  sources: Array<Source>;
  width: number;
  open: boolean;
  actions: DisplayActions;
}

interface DrawerContentProps {
  sources: Array<Source>;
}

interface DrawerHeaderProps {
  adding: boolean;
  sourceActions: SourceActions;
  displayActions: DisplayActions;
}

const DrawerHeader = ({
  adding,
  displayActions,
  sourceActions,
}: DrawerHeaderProps) => {
  let [url, setUrl] = React.useState("");

  return (
    <>
      <Toolbar
        sx={{
          justifyContent: "flex-end",
          bgcolor: "primary.contrastText",
        }}
      >
        <IconButton edge="end" onClick={displayActions.onClose}>
          <ChevronLeft />
        </IconButton>
      </Toolbar>
      <Divider />
      <Box
        component="div"
        sx={{
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Box
          component="div"
          sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "space-between",
          }}
        >
          <Typography
            sx={{
              m: "5px",
              flex: "4",
            }}
            variant="h6"
          >
            Sources
          </Typography>
          {adding ? (
            <>
              <Button
                onClick={(_) => {
                  sourceActions.confirm(url);
                  setUrl((_) => "");
                }}
              >
                <Check />
              </Button>
              <Button onClick={() => sourceActions.cancel()}>
                <Cancel />
              </Button>
            </>
          ) : (
            <Button>
              <Add onClick={() => sourceActions.add()} />
            </Button>
          )}
        </Box>
        <TextField
          label="URL"
          variant="outlined"
          value={url}
          onChange={(e) => setUrl((_) => e.target.value)}
          sx={{
            m: "5px",
            display: adding ? "flex" : "none",
          }}
        />
      </Box>
    </>
  );
};

const DrawerContent = ({ sources }: DrawerContentProps) => {
  return (
    <List>
      {sources.map((source) => (
        <ListItem
          disableGutters
          key={source.uuid}
          sx={{
            display: "flex",
            justifyContent: "space-between",
            "&:hover": {
              bgcolor: "primary.light",
              color: "primary.contrastText",
              cursor: "pointer",
            },
          }}
        >
          <Icon>
            <Article />
          </Icon>
          <Typography variant="body1" color="text.secondary">
            {source.title}
          </Typography>
          <Button>
            <Download />
          </Button>
        </ListItem>
      ))}
    </List>
  );
};

const SourceDrawer = ({ sources, width, open, actions }: SourceDrawerProps) => {
  let [adding, setAdding] = React.useState(false);

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        "&.MuiDrawer-paper": {
          width,
        },
      }}
    >
      <DrawerHeader
        adding={adding}
        displayActions={{
          onClose: actions.onClose,
        }}
        sourceActions={{
          add: () => setAdding(true),
          confirm: (url: string) => {
            console.log(`We want to add the following url: ${url}`);
            setAdding(false);
          },
          cancel: () => setAdding(false),
        }}
      />
      <DrawerContent sources={sources} />
    </Drawer>
  );
};

export { SourceDrawer, SourceDrawerProps };
