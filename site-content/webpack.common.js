const webpack = require("webpack");
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const AssetsPlugin = require("assets-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

module.exports = {
  entry: path.join(__dirname, "src/scripts", "index.js"),

  output: {
    path: path.join(__dirname, "dist/scripts/"),
    publicPath: "/scripts",
  },

  module: {
    rules: [
      {
        test: /\.((png)|(eot)|(woff)|(woff2)|(ttf)|(svg)|(gif))(\?v=\d+\.\d+\.\d+)?$/,
        loader: "file-loader?name=/[hash].[ext]",
      },

      { test: /\.json$/, loader: "json-loader" },

      {
        loader: "babel-loader",
        test: /\.js?$/,
        exclude: /node_modules/,
        query: { cacheDirectory: true },
      },

      {
        test: /\.(sa|sc|c)ss$/,
        exclude: /node_modules/,
        use: [
          "style-loader",
          MiniCssExtractPlugin.loader,
          "css-loader",
          "postcss-loader",
          "sass-loader",
        ],
      },
    ],
  },

  plugins: [
    new webpack.ProvidePlugin({
      fetch: "exports-loader?self.fetch!whatwg-fetch/dist/fetch.umd",
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      "window.jQuery": "jquery",
      Popper: "popper.js",
      Bootstrap: "bootstrap.js",
    }),

    new AssetsPlugin({
      filename: "webpack.json",
      path: path.join(process.cwd(), "dist/scripts"),
      prettyPrint: true,
      includeManifest: "manifest",
    }),
    new CleanWebpackPlugin({
      cleanOnceBeforeBuildPatterns: [
        "dist/**/*.js",
        "dist/**/*.css",
        "dist/scripts/*",
      ],
    }),
  ],
};
