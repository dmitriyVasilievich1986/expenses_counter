const path = require("path");

module.exports = {
  entry: "./src/index.js",
  output: {
    filename: "main.js",
  },
  resolve: {
    alias: {
      Assets: path.resolve(__dirname, "./src/components/assets"),
      Reducers: path.resolve(__dirname, "./src/components/reducers/"),
      Constants: path.resolve(__dirname, "./src/components/Constants.js"),
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
        use: [
          { loader: "style-loader" },
          {
            loader: "css-loader",
            options: {
              modules: {
                localIdentName: "[folder]__[local]",
              },
            },
          },
          { loader: "sass-loader" },
        ],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: "asset/resource",
      },
    ],
  },
};
