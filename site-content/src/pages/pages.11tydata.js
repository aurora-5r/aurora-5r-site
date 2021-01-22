module.exports = {
  eleventyComputed: {
    eleventyNavigation: {
      key: (data) => data.title,
      parent: (data) => {
        if (data.navigation) return data.navigation;
        else return "main";
      },
    },
  },
};
