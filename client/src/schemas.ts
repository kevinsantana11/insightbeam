interface Source {
  uuid: number;
  title: string;
  url: string;
  imageUrl: string;
  lastBuildTimestamp: number;
  pubDateTimestamp: number;
}

interface SourceItem {
  uuid: number;
  title: string;
  content: string;
  url: string;
  postedTimestamp: number;
  updatedTimestamp: number;
  authors: Array<string>;
  source_uuid: number;
}

type ArticleAnalysis = {
  source_item_uuid: number;
  error?: string;
} & BaseAnalysis &
  CounterAnalysis;

interface BaseAnalysis {
  analysis?: Analysis;
}

interface Analysis {
  subject: string;
  view_points: Array<Viewpoint>;
}

interface Viewpoint {
  point: string;
  arguments: Array<string>;
}

interface CounterAnalysis {
  counters?: Array<Counter>;
}

interface Counter {
  counter_source_item_uuid: number;
  original_view_point: string;
  counter_view_point: string;
  arguments: Array<string>;
}

export { Source, SourceItem, ArticleAnalysis, Viewpoint, Counter };
