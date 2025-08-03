import React from 'react';

interface NewsItem {
  title: string;
  url: string;
  sentiment: number;
}

interface NewsFeedProps {
  /** List of news articles with sentiment scores */
  articles: NewsItem[];
}

/**
 * Displays a list of news articles with their corresponding
 * sentiment scores. Positive sentiment values are bullish while
 * negative values indicate bearish sentiment.
 */
const NewsFeed: React.FC<NewsFeedProps> = ({ articles }) => (
  <div className="news-feed">
    <h3>News Feed</h3>
    <ul>
      {articles.map((article, idx) => (
        <li key={idx}>
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
          </a>
          <span className="sentiment">{article.sentiment.toFixed(2)}</span>
        </li>
      ))}
    </ul>
  </div>
);

export default NewsFeed;

