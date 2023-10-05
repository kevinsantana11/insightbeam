import path from "path";
import process from "process";
import HtmlWebpackPlugin from "html-webpack-plugin";

const build_path = path.resolve(process.cwd(), "./dist");

const config = {
  entry: "./src/index.tsx",
  mode: "development",
  output: {
    path: build_path,
    filename: "index.js",
  },
  devServer: {
    static: {
      directory: build_path,
    },
  },
  module: {
    rules: [
      {
        test: /\.[tsx|jsx|js|ts]+/,
        use: "babel-loader",
      },
    ],
  },
  resolve: {
    extensions: [".js", ".ts", ".tsx"],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: "./public/index.html",
    }),
  ],
};

export default config;
