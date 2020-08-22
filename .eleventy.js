module.exports = function (eleventyConfig) {
    // Add a filter using the Config API
    eleventyConfig.addFilter("myFilter", function () {});
    eleventyConfig.addPassthroughCopy("src/images");
    eleventyConfig.addPassthroughCopy("src/content");

    eleventyConfig.addPassthroughCopy("src/scss");
    eleventyConfig.addPassthroughCopy("src/css");

    eleventyConfig.addPassthroughCopy("src/fonts");
    eleventyConfig.addPassthroughCopy("src/js");

    // You can return your Config object (optional).
    return {
        passthroughFileCopy: true,
        markdownTemplateEngine: "njk",
        templateFormats: ["html", "njk", "md"],
        dir: {
            input: "src",
            output: "_site",
            include: "includes",
        },
    };
};
