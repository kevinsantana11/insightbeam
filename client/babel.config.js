const config = {
  presets: [
    [
      "@babel/preset-env",
      {
        targets: {
          firefox: 100,
        },
      },
    ],
    "@babel/preset-react",
    "@babel/preset-typescript",
  ],
};

export default config;
