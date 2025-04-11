<template>
  <div class="app">
    <header>
      <h1>Hacker News 文章</h1>
    </header>
    <HomePage />
  </div>
</template>

<script>
import HomePage from './components/HomePage.vue';

export default {
  name: 'App',
  components: {
    HomePage
  }
}
</script>

<style>
body {
  margin: 0;
  background: #f5f5f5;
  font-family: Arial, sans-serif;
}

.app {
  min-height: 100vh;
}

header {
  background: #42b883;
  color: white;
  padding: 20px;
  text-align: center;
}

h1 {
  margin: 0;
}
</style>
