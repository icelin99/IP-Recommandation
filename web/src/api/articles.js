// 导入 JSON 数据
import hackerNewsData from './HackerNews_top500.json';
import documentRelations from './document_relations.json';

export const getArticles = () => {
  return new Promise((resolve) => {
    // 模拟异步加载
    setTimeout(() => {
      resolve(hackerNewsData);
    }, 100);
  });
};

export const getRelatedPapers = (articleId) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log("articleId", articleId)
        const relation = documentRelations["document_relations"].find(r => r["hackernews_id"] == String(articleId));
        resolve(relation ? relation.related_arxiv : []);
      }, 100);
    });
  };