<template>
  <div class="dashboard">
    <h1>仪表盘</h1>
    <div class="stats">
      <div class="stat-card">
        <h3>总用户</h3>
        <p class="number">1,234</p>
      </div>
      <div class="stat-card">
        <h3>今日活跃</h3>
        <p class="number">123</p>
      </div>
      <div class="stat-card">
        <h3>总订单</h3>
        <p class="number">456</p>
      </div>
      <div class="stat-card">
        <h3>待处理</h3>
        <p class="number">78</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 24px;
}

h1 {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 500;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.stat-card {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin: 0 0 16px;
  color: #666;
  font-size: 16px;
}

.number {
  margin: 0;
  font-size: 32px;
  font-weight: 500;
  color: #1890ff;
}
</style> 