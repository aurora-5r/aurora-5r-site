// image minification
const dest = "./dist/images",
  fsp = require("fs").promises,
  imagemin = require("imagemin"),
  plugins = [
    require("imagemin-mozjpeg")(),
    require("imagemin-pngquant")({ strip: true }),
    require("imagemin-svgo")(),
  ];

module.exports = class {
  data() {
    return {
      permalink: false,
      eleventyExcludeFromCollections: true,
    };
  }

  // process all files
  async render() {
    console.log("optimizing images");
    // destination already exists?
    /* try {
      let dir = await fsp.stat(dest);
      if (dir.isDirectory()) {
        console.log("nothing to do");
        return true;
      }
    } catch (e) {} */

    // process images
    console.log("in progress");

    await imagemin(["src/images/*", "!src/images/*.js"], {
      destination: dest,
      plugins,
    });
    console.log("done");

    return true;
  }
};
