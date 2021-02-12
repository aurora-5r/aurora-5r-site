const fs = require("fs");
const path = require("path");
const livePosts = (p) => p.date <= now && !p.data.draft;
const now = new Date();

const manifestPath = path.resolve(__dirname, "dist", "scripts", "webpack.json");
const manifest = JSON.parse(
  fs.readFileSync(manifestPath, {
    encoding: "utf8",
  })
);
const pluginSEO = require("eleventy-plugin-seo");
const embedYouTube = require("eleventy-plugin-youtube-embed");
const Image = require("@11ty/eleventy-img");
const sharp = require("sharp");
const eleventyNavigationPlugin = require("@11ty/eleventy-navigation");
const readingTime = require("eleventy-plugin-reading-time");
const readerBar = require("eleventy-plugin-reader-bar");
const imagesResponsiver = require("eleventy-plugin-images-responsiver");
const markdownIt = require("markdown-it");
const markdownItAnchor = require("markdown-it-anchor");

const pluginTOC = require("eleventy-plugin-toc");

module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/images");
  const presets = {
    default: {
      sizes: `(max-width: 340px) 250px, 50vw`,
      minWidth: 250,
      maxWidth: 1200,
      fallbackWidth: 725,
      attributes: {
        loading: "lazy",
      },
    },
    "small-img": {
      fallbackWidth: 250,
      minWidth: 250,
      maxWidth: 250,
      steps: 1,
      sizes: "250px",
      attributes: {
        loading: "lazy",
      },
    },
  };
  eleventyConfig.addPlugin(imagesResponsiver, presets);
  eleventyConfig.addPassthroughCopy("src/*/*/images/*.*");
  eleventyConfig.setLibrary("md", markdownIt().use(markdownItAnchor));
  eleventyConfig.addPlugin(eleventyNavigationPlugin);
  eleventyConfig.addPlugin(pluginTOC, {
    tags: ["h2", "h3"],
    wrapper: "div",
  });

  eleventyConfig.addPlugin(readingTime);
  eleventyConfig.addPlugin(readerBar);

  eleventyConfig.addPlugin(embedYouTube, {
    embedClass: "post-video",
  });

  eleventyConfig.addPlugin(pluginSEO, {
    title: "AuRorA-5R",
    description:
      "Transcubateur. AuRorA-5R accompagne les PME de la région AURA dans leurs projets innovants pour des transitions responsables",
    url: "https://aurora-5r.fr",
    author: "Laurent Maumet",
    twitter: "aurora-5r",
  });
  eleventyConfig.addPassthroughCopy("src/robots.txt");

  eleventyConfig.addShortcode("bundledCss", function () {
    return manifest["main"]["css"]
      ? `<link href="${manifest["main"]["css"]}" rel="stylesheet" />`
      : "";
  });

  eleventyConfig.addShortcode("bundledJs", function () {
    return manifest["main"]["js"]
      ? `<script src="${manifest["main"]["js"]}" async></script>`
      : "";
  });
  eleventyConfig.addCollection("posts", (collection) => {
    return collection
      .getFilteredByGlob("./src/posts/**/*.md")
      .filter((_) => livePosts(_))
      .reverse();
  });
  eleventyConfig.addCollection("drafts", (collection) => {
    return collection
      .getFilteredByGlob("./src/posts/**/*.md")
      .filter((_) => !livePosts(_))
      .reverse();
  });
  eleventyConfig.addCollection("offres", (collection) => {
    return collection.getFilteredByGlob("./src/offres/**/*.md").reverse();
  });
  eleventyConfig.addCollection("bios", (collection) => {
    return collection.getFilteredByGlob("./src/bios/**/*.md").reverse();
  });
  return {
    dir: {
      input: "src",
      output: "dist",
    },
  };
};
