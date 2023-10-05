import sources from "./data/sources";
import sourceItems from "./data/source-items";
import sourceItemAnalyses from "./data/source-items-analysis";
import { Source, SourceItem, ArticleAnalysis } from "./schemas";

interface Store {
  sources: Array<Source>;
  sourceItems: Array<SourceItem>;
  sourceItemAnalyses: Array<ArticleAnalysis>;
}

const db: Store = {
  sources,
  sourceItems,
  sourceItemAnalyses,
};

export { Store, db };
