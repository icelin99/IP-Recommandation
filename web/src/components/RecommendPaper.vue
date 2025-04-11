<template>
    <div class="recommendations" v-if="selectedArticle">
      <div class="recommendations-header">
        <h3>推荐论文</h3>
        <p class="selected-title">基于: {{ selectedArticle.title }}</p>
      </div>
      <div class="papers-list">
        <div v-if="loading" class="loading">加载推荐中...</div>
        <div v-else-if="relatedPapers.length === 0" class="no-papers">
          暂无推荐论文
        </div>
        <a 
          v-else
          v-for="paper in relatedPapers" 
          :key="paper.arxiv_url"
          :href="paper.arxiv_url"
          target="_blank"
          class="paper-item"
        >
          <span class="paper-title">{{ paper.paper_title }}</span>
          <span class="similarity">相似度: {{ (paper.similarity * 100).toFixed(1) }}%</span>
        </a>
      </div>
    </div>
  </template>
  
  <script setup>
  /* eslint-disable no-undef */
  defineProps({
    selectedArticle: {
      type: Object,
      default: null
    },
    relatedPapers: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  });
  </script>
  
  <style scoped>
  .recommendations {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    height: fit-content;
    position: sticky;
    top: 20px;
  }
  
  .recommendations-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
  }
  
  .recommendations-header h3 {
    margin: 0 0 10px 0;
    color: #2c3e50;
  }
  
  .selected-title {
    margin: 0;
    font-size: 0.9em;
    color: #666;
  }
  
  .papers-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .paper-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px;
    border: 1px solid #eee;
    border-radius: 6px;
    text-decoration: none;
    color: inherit;
    transition: all 0.2s;
  }
  
  .paper-item:hover {
    background: #f9f9f9;
    transform: translateY(-2px);
  }
  
  .paper-title {
    font-size: 0.95em;
    color: #2c3e50;
  }
  
  .similarity {
    font-size: 0.85em;
    color: #666;
  }
  
  .no-papers {
    text-align: center;
    padding: 20px;
    color: #666;
  }
  
  .loading {
    text-align: center;
    padding: 20px;
    color: #666;
  }
  </style>