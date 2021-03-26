const fs = require("fs");
const path = require("path");
const livePosts = (p) => p.date <= now && !p.data.draft;
const now = new Date();
const isProduction = process.env.NODE_ENV === `production`;

const manifestPath = path.resolve(__dirname, "dist", "scripts", "webpack.json");
const manifest = JSON.parse(
  fs.readFileSync(manifestPath, {
    encoding: "utf8",
  })
);
const pluginSEO = require("eleventy-plugin-seo");
const embedYouTube = require("eleventy-plugin-youtube-embed");

const eleventyNavigationPlugin = require("@11ty/eleventy-navigation");
const readingTime = require("eleventy-plugin-reading-time");
const readerBar = require("eleventy-plugin-reader-bar");
const imagesResponsiver = require("eleventy-plugin-images-responsiver");

const pluginTOC = require("eleventy-plugin-toc");

function sortByOrder(values) {
  return values.slice().sort((a, b) => a.data.order - b.data.order)
}

module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/images");
  eleventyConfig.addFilter('sortByOrder', sortByOrder)

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
  if (process.env.ELEVENTY_ENV === "production") {
    eleventyConfig.addPlugin(imagesResponsiver, presets);
  }

  eleventyConfig.addPassthroughCopy("src/**/images/*.*");
  eleventyConfig.addPlugin(eleventyNavigationPlugin);
  eleventyConfig.addPlugin(readingTime);
  eleventyConfig.addPlugin(readerBar);
  eleventyConfig.addPlugin(embedYouTube, {
    embedClass: "post-video",
  });

  eleventyConfig.addPlugin(pluginSEO, {
    title: "AuRorA-5R",
    description:
      "AuRorA-5R accompagne les acteurs du territoire de la région AURA pour valoriser les incertitudes des marchés en rupture, en faisant l’expérience de la confiance.",
    url: "https://aurora-5r.fr",
    author: "Laurent Maumet",
  });
  eleventyConfig.addPassthroughCopy("src/robots.txt");

  eleventyConfig.addShortcode("bundledCss", function () {
    return manifest["main"]["css"]
      ? `<link href="${manifest["main"]["css"]}  " rel="stylesheet" />`
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
  eleventyConfig.addCollection("newsletters", (collection) => {
    return collection
      .getFilteredByGlob("./src/newsletters/**/*.md")
      .reverse();
  });


  eleventyConfig.addCollection("bios", (collection) => {
    return collection.getFilteredByGlob("./src/bios/**/*.md").reverse();
  });
  eleventyConfig.addCollection("recrutements", (collection) => {
    return collection.getFilteredByGlob("./src/recrutements/**/*.md").reverse();
  });
  return {
    dir: {
      input: "src",
      output: "dist",
    },
    pathPrefix: isProduction ? `/` : `/aurora5r/`,
    templateFormats: ["njk", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
};
