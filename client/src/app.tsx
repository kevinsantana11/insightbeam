import React from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  ThemeProvider,
  Theme,
  styled,
  Divider,
} from "@mui/material";
import { ChevronRight } from "@mui/icons-material";
import { SourceDrawer } from "./components/source-drawer";
import { SourceItemsView } from "./components/source-items-view";
import { SourceItemDetails } from "./components/source-item-details";
import { Store } from "./db";
import { ArticleAnalysis, SourceItem } from "./schemas";

interface AppProps {
  store: Store;
  theme: Theme;
}

interface MainProps {
  open: boolean;
  width: number;
}

const Main = styled("main", {
  shouldForwardProp: (prop) => prop !== "open" && prop !== "width",
})<MainProps>(({ theme, open, width }) => ({
  marginLeft: open ? `${width}px` : "auto",
  padding: theme.spacing(0, 1),
}));

const ToolbarSpacer = styled("div")(({ theme }) => ({
  ...theme.mixins.toolbar,
}));

const App = ({ store, theme }: AppProps) => {
  const [drawerOpen, setDrawerOpen] = React.useState(false); // TODO: change be to false
  const [detailsOpen, setDetailsOpen] = React.useState(false);
  const [currentItem, setCurrentItem] = React.useState({
    article: store.sourceItems[0],
    analysis: store.sourceItemAnalyses[0] as ArticleAnalysis | undefined,
  });
  const drawerWidth = 225;

  const sourceItemSelectedHandler = (item: SourceItem) => {
    setCurrentItem({
      article: { ...item },
      analysis: store.sourceItemAnalyses[0],
    });
    setDetailsOpen(true);
  };

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          display: "flex",
        }}
      >
        <SourceDrawer
          sources={store.sources}
          width={drawerWidth}
          open={drawerOpen}
          actions={{
            onClose: () => setDrawerOpen(false),
          }}
        />
        <AppBar position="fixed">
          <Toolbar
            sx={{
              marginLeft: drawerOpen ? `${drawerWidth}px` : "0px",
              width: drawerOpen ? `calc(100% - ${drawerWidth}px)` : "100%",
            }}
          >
            <IconButton
              onClick={(_) => setDrawerOpen(true)}
              edge="start"
              sx={{
                display: drawerOpen ? "none" : "auto",
              }}
            >
              <ChevronRight />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              Insight Beam
            </Typography>
          </Toolbar>
        </AppBar>
        <Main open={drawerOpen} width={drawerWidth}>
          <ToolbarSpacer />
          <Box
            sx={{
              display: "flex",
              flexDirection: "row",
              alignContent: "space-between",
              justifyItems: "center",
            }}
          >
            <Box flex="1"></Box>
            <Box display="flex" flex="2">
              <Divider orientation="vertical" variant="middle" flexItem />
              <SourceItemsView
                sources={store.sources}
                items={store.sourceItems}
                onMoreDetail={sourceItemSelectedHandler}
                sx={{ flex: "1" }}
              />
              <Divider orientation="vertical" variant="middle" flexItem />
            </Box>
            <Box flex="1"></Box>
          </Box>
          <SourceItemDetails
            key={currentItem.article.uuid}
            item={currentItem}
            onClose={() => setDetailsOpen(false)}
            open={detailsOpen}
          />
        </Main>
      </Box>
    </ThemeProvider>
  );
};

export default App;
