<template>
    <div class="container">
        <div v-if="loading" class="loading">
            加载中...
        </div>
        <div v-else class="main-layout">
            <!-- 左侧文章列表 -->
            <div class="articles-section">
                <div class="articles-grid">
                    <HNCard v-for="article in displayedArticles" :key="article.id" :article="article"
                        @click="selectArticle(article)" :class="{ 'selected': selectedArticle?.id === article.id }" />
                </div>

                <div class="pagination">
                    <button :disabled="currentPage === 1" @click="currentPage--">
                        上一页
                    </button>
                    <span>{{ currentPage }} / {{ totalPages }}</span>
                    <button :disabled="currentPage === totalPages" @click="currentPage++">
                        下一页
                    </button>
                </div>
            </div>

            <!-- 右侧推荐论文 -->
            <RecommendedPapers :selected-article="selectedArticle" :related-papers="relatedPapers"
                :loading="loadingRecommendations" />
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import HNCard from '../components/HNCard.vue';
import RecommendedPapers from '../components/RecommendPaper.vue';
import { getArticles, getRelatedPapers } from '../api/articles';


const articles = ref([]);
const loading = ref(true);
const loadingRecommendations = ref(false);
const currentPage = ref(1);
const itemsPerPage = 9;
const selectedArticle = ref(null);
const relatedPapers = ref([]);

// 计算总页数
const totalPages = computed(() => Math.ceil(articles.value.length / itemsPerPage));

// 计算当前页显示的文章
const displayedArticles = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return articles.value.slice(start, end);
});

const selectArticle = async (article) => {
  selectedArticle.value = article;
  loadingRecommendations.value = true;
  try {
    console.log("article", article.id)
    const papers = await getRelatedPapers(article.id);
    relatedPapers.value = papers;
    console.log("relatedPapers", relatedPapers.value)
  } catch (error) {
    console.error('Failed to fetch related papers:', error);
    relatedPapers.value = [];
  } finally {
    loadingRecommendations.value = false;
  }
};

// 模拟获取数据
const fetchArticles = async () => {
    try {
        loading.value = true;
        const data = await getArticles();
        articles.value = data;
    } catch (error) {
        console.error('Failed to fetch articles:', error);
    } finally {
        loading.value = false;
    }
};

onMounted(fetchArticles);
</script>

<style scoped>
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.articles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
}

button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background: #42b883;
    color: white;
    cursor: pointer;
}

button:disabled {
    background: #ccc;
    cursor: not-allowed;
}
</style>