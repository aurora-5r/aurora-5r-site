module.exports = {
  eleventyComputed: {
    cover: (data) => {
      if (data.cover) return data.cover;
      else return "/images/5r.svg";
    },
  },
};
