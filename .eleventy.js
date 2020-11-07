const fs = require("fs");
const path = require("path");
const livePosts = (p) => p.date <= now && !p.data.draft;
const now = new Date();

const manifestPath = path.resolve(
  __dirname,
  "dist",
  "scripts",
  "manifest.json"
);
const manifest = JSON.parse(
  fs.readFileSync(manifestPath, {
    encoding: "utf8",
  })
);
const pluginSEO = require("eleventy-plugin-seo");
const embedYouTube = require("eleventy-plugin-youtube-embed");

module.exports = function (eleventyConfig) {
  eleventyConfig.addShortcode("first_image", (post) => extractFirstImage(post));

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
  eleventyConfig.addPassthroughCopy("src/images");
  eleventyConfig.addPassthroughCopy("robots.txt");
  eleventyConfig.addPassthroughCopy("src/posts/images");

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
  eleventyConfig.addCollection("posts", (collection) => {
    return collection
      .getFilteredByGlob("./src/posts/*.md")
      .filter((_) => livePosts(_))
      .reverse();
  });
  eleventyConfig.addCollection("drafts", (collection) => {
    return collection
      .getFilteredByGlob("./src/posts/*.md")
      .filter((_) => !livePosts(_))
      .reverse();
  });
  return {
    dir: {
      input: "src",
      output: "dist",
      data: "_data",
    },
    passthroughFileCopy: true,
    templateFormats: ["njk", "md", "html", "yml"],
    htmlTemplateEngine: "njk",
  };
};

/**
 * @param {*} doc A real big object full of all sorts of information about a document.
 * @returns {String} the markup of the first image.
 */
function extractFirstImage(doc) {
  if (!doc.hasOwnProperty("templateContent")) {
    console.warn(
      "❌ Failed to extract image: Document has no property `templateContent`."
    );
    return '<img class="center-block" src="/images/5r.png" alt="5R"></img>';
  }

  const content = doc.templateContent;

  if (content.includes("<img")) {
    const imgTagBegin = content.indexOf("<img");
    const imgTagEnd = content.indexOf(">", imgTagBegin);
    const res =
      '<img class="center-block"' +
      content.substring(imgTagBegin + 4, imgTagEnd + 1);
    return res;
    return content.substring(imgTagBegin, imgTagEnd + 1);
  } else {
    return '<img class="center-block" src="/images/5R.png" alt="5R"></img>';
  }
}
