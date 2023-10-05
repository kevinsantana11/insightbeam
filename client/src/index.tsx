import React from "react";
import { createRoot } from "react-dom/client";
import App from "./app";
import { db } from "./db";
import { createTheme } from "@mui/material";

const theme = createTheme();

const container = document.getElementById("react_container");
const root = createRoot(container!);
root.render(<App store={db} theme={theme} />);
