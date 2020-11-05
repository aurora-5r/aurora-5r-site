"use strict";

var fs = require("fs");

var path = require("path");

var manifestPath = path.resolve(__dirname, "dist", "scripts", "manifest.json");
var manifest = JSON.parse(fs.readFileSync(manifestPath, {
  encoding: "utf8"
}));

var pluginSEO = require("eleventy-plugin-seo");

var embedYouTube = require("eleventy-plugin-youtube-embed");

module.exports = function (eleventyConfig) {
  eleventyConfig.addPlugin(embedYouTube, {
    embedClass: 'post-video'
  });
  eleventyConfig.addPlugin(pluginSEO, {
    title: "AuRorA-5R",
    description: "Transcubateur. AuRorA-5R accompagne les PME de la région AURA dans leurs projets innovants pour des transitions responsables",
    url: "https://aurora-5r.fr",
    author: "Laurent Maumet",
    twitter: "aurora-5r"
  });
  eleventyConfig.addPassthroughCopy('src/images');
  eleventyConfig.addPassthroughCopy('robots.txt');
  eleventyConfig.addPassthroughCopy('src/posts/images'); // Add a shortcode for bundled CSS.

  eleventyConfig.addShortcode("bundledCss", function () {
    return manifest["main.css"] ? "<link href=\"".concat(manifest["main.css"], "\" rel=\"stylesheet\" />") : "";
  }); // Add a shortcode for bundled JS.

  eleventyConfig.addShortcode("bundledJs", function () {
    return manifest["main.js"] ? "<script src=\"".concat(manifest["main.js"], "\"></script>") : "";
  });
  return {
    dir: {
      input: 'src',
      output: 'dist',
      data: '_data'
    },
    passthroughFileCopy: true,
    templateFormats: ['njk', 'md', 'html', 'yml'],
    htmlTemplateEngine: 'njk'
  };
};