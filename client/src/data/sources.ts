import { Source } from "../schemas";

const data: { sources: Array<Source> } = {
  sources: [
    {
      uuid: 1,
      url: "http://rss.cnn.com/rss/cnn_topstories.rss",
      imageUrl:
        "http://i2.cdn.turner.com/cnn/2015/images/09/24/cnn.digital.png",
      lastBuildTimestamp: Date.now(),
      pubDateTimestamp: Date.now(),
      title: "CNN.com - RSS Channel - HP Hero",
    },
    {
      uuid: 2,
      url: "https://moxie.foxnews.com/google-publisher/latest.xml",
      imageUrl:
        "https://global.fncstatic.com/static/orion/styles/img/fox-news/logos/fox-news-desktop.png",
      lastBuildTimestamp: Date.now(),
      pubDateTimestamp: Date.now(),
      title: "Latest & Breaking News on Fox News",
    },
  ],
};

export default data.sources;
