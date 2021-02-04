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
        if (data.ordernavigation) return data.ordernavigation;
        else return 0;
      },
    },
  },
};
