module.exports = {
  eleventyComputed: {
    eleventyNavigation: {
      key: (data) => data.title,
      parent: (data) => data.parent,
      title: (data) => {
        if (data.titlenavigation) return data.titlenavigation;
        else return data.title;
      },
      order: (data) => {
        if (data.order) return data.order;
        else return 0;
      },
    },
  },
};
