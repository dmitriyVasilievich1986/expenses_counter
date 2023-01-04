const webpack = require("webpack");
const path = require("path");

module.exports = {
  entry: "./src/index.js",
  output: {
    filename: "main.js",
  },
  resolve: {
    alias: {
      Reducers: path.resolve(__dirname, "src/components/reducers/"),
      Constants: path.resolve(__dirname, "src/components/Constants.js"),
    },
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: ["babel-loader"],
      },
      {
        test: /\.s[ac]ss$/i,
        use: ["style-loader", "css-loader", "sass-loader"],
      },
    ],
  },
};
