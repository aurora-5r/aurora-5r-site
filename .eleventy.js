const fs = require("fs");
const path = require("path");


const manifestPath = path.resolve(__dirname, "dist", "scripts", "manifest.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, { encoding: "utf8" }))


module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy('src/images')
  // Add a shortcode for bundled CSS.
  eleventyConfig.addShortcode("bundledCss", function () {
    return manifest["main.css"]
      ? `<link href="${manifest["main.css"]}" rel="stylesheet" />`
      : "";
  });

  // Add a shortcode for bundled JS.
  eleventyConfig.addShortcode("bundledJs", function () {
    return manifest["main.js"]
      ? `<script src="${manifest["main.js"]}"></script>`
      : "";
  });
  return {
    dir: { input: 'src', output: 'dist', data: '_data' },
    passthroughFileCopy: true,
    templateFormats: ['njk', 'md', 'html', 'yml'],
    htmlTemplateEngine: 'njk'
  }
}
