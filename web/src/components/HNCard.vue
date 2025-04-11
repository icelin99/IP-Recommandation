<template>
  <div class="hn-card">
    <h3 class="title">
      <a :href="article.url" target="_blank" rel="noopener">
        {{ article.title }}
      </a>
    </h3>
    <div class="meta">
      <span class="author">作者: {{ article.by }}</span>
      <span class="points">👍 {{ article.score }}</span>
    </div>
    <div class="stats">
      <span>💬 {{ article.descendants || 0 }} 评论</span>
      <span>🕒 {{ formatDate(article.time) }}</span>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
defineProps({
  article: {
    type: Object,
    required: true
  }
});

const formatDate = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleDateString('zh-CN');
};
</script>

<style scoped>
.hn-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background: white;
  transition: transform 0.2s;
}

.hn-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.title {
  margin: 0 0 12px 0;
  font-size: 1.1em;
  line-height: 1.4;
}

.title a {
  color: #2c3e50;
  text-decoration: none;
}

.title a:hover {
  color: #42b883;
}

.meta {
  display: flex;
  justify-content: space-between;
  color: #666;
  margin-bottom: 8px;
  font-size: 0.9em;
}

.stats {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 0.9em;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}
</style> 