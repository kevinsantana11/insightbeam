import { ArticleAnalysis } from "../schemas";
const data: { analyses: Array<ArticleAnalysis> } = {
  analyses: [
    {
      source_item_uuid: 1,
      analysis: {
        subject: "Dominion Voting Systems' defamation lawsuit against Fox News",
        view_points: [
          {
            point:
              "The parties have reached a last-second settlement in the lawsuit.",
            arguments: [
              "The settlement was announced in court by Delaware Superior Court Judge Eric Davis.",
              "The settlement was reached while the trial was on the brink of opening statements.",
            ],
          },
          {
            point:
              "The settlement means the case is effectively over and won't proceed to trial.",
            arguments: [
              "Fox News executives and on-air personalities will be spared from testifying about their 2020 election coverage.",
            ],
          },
          {
            point: "Details of the settlement were not immediately available.",
            arguments: [
              "The terms of the settlement might never become public.",
            ],
          },
          {
            point:
              "In its lawsuit, Dominion sought $1.6 billion in damages from Fox News.",
            arguments: [
              "Fox News argued that this number was inflated and didn't accurately capture the potential losses Dominion could have suffered.",
            ],
          },
          {
            point:
              "Fox News and Fox Corporation deny defaming Dominion and claim the case is a meritless assault on press freedoms.",
            arguments: [
              "Fox News denies promoting election conspiracies to save their falling ratings after the 2020 election.",
            ],
          },
          {
            point:
              "Fox News is still facing a second major defamation lawsuit from Smartmatic.",
            arguments: [
              "The Smartmatic case is still in the discovery process and a trial isn't expected soon.",
            ],
          },
        ],
      },
      counters: [
        {
          counter_source_item_uuid: 2,
          original_view_point:
            "dominion succeeds, Fox news faces justice by defaming dominion on baseless claims",
          counter_view_point:
            "Fox news saids the case upholds the freedom of speech and press",
          arguments: [
            "dominion does have a faulty system",
            "dominion was trying to squash freedom of speech by sueing fox news",
          ],
        },
        {
          counter_source_item_uuid: 2,
          original_view_point:
            "dominion succeeds, Fox news faces justice by defaming dominion on baseless claims",
          counter_view_point:
            "Fox news saids the case upholds the freedom of speech and press",
          arguments: [
            "dominion does have a faulty system",
            "dominion was trying to squash freedom of speech by sueing fox news",
          ],
        },
      ],
    },
  ],
};

export default data.analyses;
