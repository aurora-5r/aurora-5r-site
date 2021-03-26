"use strict";

var fs = require("fs");

var path = require("path");

var livePosts = function livePosts(p) {
  return p.date <= now && !p.data.draft;
};

var now = new Date();
var isProduction = process.env.NODE_ENV === "production";
var manifestPath = path.resolve(__dirname, "dist", "scripts", "webpack.json");
var manifest = JSON.parse(fs.readFileSync(manifestPath, {
  encoding: "utf8"
}));

var pluginSEO = require("eleventy-plugin-seo");

var embedYouTube = require("eleventy-plugin-youtube-embed");

var eleventyNavigationPlugin = require("@11ty/eleventy-navigation");

var readingTime = require("eleventy-plugin-reading-time");

var readerBar = require("eleventy-plugin-reader-bar");

var imagesResponsiver = require("eleventy-plugin-images-responsiver");

var pluginTOC = require("eleventy-plugin-toc");

function sortByOrder(values) {
  return values.slice().sort(function (a, b) {
    return a.data.order - b.data.order;
  });
}

module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/images");
  eleventyConfig.addFilter('sortByOrder', sortByOrder);
  var presets = {
    "default": {
      sizes: "(max-width: 340px) 250px, 50vw",
      minWidth: 250,
      maxWidth: 1200,
      fallbackWidth: 725,
      attributes: {
        loading: "lazy"
      }
    },
    "small-img": {
      fallbackWidth: 250,
      minWidth: 250,
      maxWidth: 250,
      steps: 1,
      sizes: "250px",
      attributes: {
        loading: "lazy"
      }
    }
  };

  if (process.env.ELEVENTY_ENV === "production") {
    eleventyConfig.addPlugin(imagesResponsiver, presets);
  }

  eleventyConfig.addPassthroughCopy("src/**/images/*.*");
  eleventyConfig.addPlugin(eleventyNavigationPlugin);
  eleventyConfig.addPlugin(readingTime);
  eleventyConfig.addPlugin(readerBar);
  eleventyConfig.addPlugin(embedYouTube, {
    embedClass: "post-video"
  });
  eleventyConfig.addPlugin(pluginSEO, {
    title: "AuRorA-5R",
    description: "AuRorA-5R accompagne les acteurs du territoire de la région AURA pour valoriser les incertitudes des marchés en rupture, en faisant l’expérience de la confiance.",
    url: "https://aurora-5r.fr",
    author: "Laurent Maumet"
  });
  eleventyConfig.addPassthroughCopy("src/robots.txt");
  eleventyConfig.addShortcode("bundledCss", function () {
    return manifest["main"]["css"] ? "<link href=\"".concat(manifest["main"]["css"], "  \" rel=\"stylesheet\" />") : "";
  });
  eleventyConfig.addShortcode("bundledJs", function () {
    return manifest["main"]["js"] ? "<script src=\"".concat(manifest["main"]["js"], "\" async></script>") : "";
  });
  eleventyConfig.addCollection("posts", function (collection) {
    return collection.getFilteredByGlob("./src/posts/**/*.md").filter(function (_) {
      return livePosts(_);
    }).reverse();
  });
  eleventyConfig.addCollection("newsletters", function (collection) {
    return collection.getFilteredByGlob("./src/newsletters/**/*.md").reverse();
  });
  eleventyConfig.addCollection("bios", function (collection) {
    return collection.getFilteredByGlob("./src/bios/**/*.md").reverse();
  });
  eleventyConfig.addCollection("recrutements", function (collection) {
    return collection.getFilteredByGlob("./src/recrutements/**/*.md").reverse();
  });
  return {
    dir: {
      input: "src",
      output: "dist"
    },
    pathPrefix: isProduction ? "/" : "/aurora5r/",
    templateFormats: ["njk", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};