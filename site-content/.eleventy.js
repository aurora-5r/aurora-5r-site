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

module.exports = function (eleventyConfig) {
  // eleventyConfig.addPassthroughCopy("src/images");
  // eleventyConfig.addPassthroughCopy("src/posts/images");
  eleventyConfig.addPlugin(eleventyNavigationPlugin);
  eleventyConfig.addPassthroughCopy("src/newposts/**/*.png");
  eleventyConfig.addPassthroughCopy("src/offres/**/*.png");

  eleventyConfig.addNunjucksAsyncShortcode(
    "MyResponsiveImage",
    async (src, alt) => {
      if (alt == undefined) {
        // You bet we throw an error on missing alt (alt="" works okay)
        throw new Error("Missing alt on myResponsiveImage from: ${src}");
      }
      let stats = await Image(src, {
        widths: [25, 320, 640, 960, 1200, 1800, 2400],
        formats: ["jpeg", "webp"],
        urlPath: "/images/",
        outputDir: "./dist/images/",
      });
      //let lowestSrc = stats[outputFormat][0];
      let lowestSrc = stats["jpeg"][0];

      let sizes = "100vw"; // Make sure you customize this!

      // Iterate over formats and widths
      return `<picture>
     ${Object.values(stats)
       .map((imageFormat) => {
         return `  <source type="image/${
           imageFormat[0].format
         }" srcset="${imageFormat
           .map((entry) => `${entry.url} ${entry.width}w`)
           .join(", ")}" sizes="${sizes}">`;
       })
       .join("\n")}
        <img
          src="${lowestSrc.url}"
          width="${lowestSrc.width}"
          height="${lowestSrc.height}"
          alt="${alt}">
          </picture>`;
    }
  );

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
  eleventyConfig.addPassthroughCopy("robots.txt");

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
      .getFilteredByGlob("./src/newposts/**/*.md")
      .filter((_) => livePosts(_))
      .reverse();
  });
  eleventyConfig.addCollection("drafts", (collection) => {
    return collection
      .getFilteredByGlob("./src/newposts/**/*.md")
      .filter((_) => !livePosts(_))
      .reverse();
  });
  eleventyConfig.addCollection("offres", (collection) => {
    return collection.getFilteredByGlob("./src/offres/**/*.md").reverse();
  });
  return {
    dir: {
      input: "src",
      output: "dist",
      // data: "_data",
    },
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
