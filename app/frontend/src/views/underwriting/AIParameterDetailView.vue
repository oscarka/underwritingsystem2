# 智核参数详情页面
<template>
  <div class="ai-parameter-detail-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <BaseButton @click="router.back()">返回</BaseButton>
        <h1>智核参数详情</h1>
      </div>
      <div class="header-actions">
        <BaseButton type="primary" @click="handleEdit">编辑</BaseButton>
      </div>
    </div>

    <!-- 详情内容 -->
    <div class="detail-container">
      <div class="detail-section">
        <h2>基本信息</h2>
        <div class="detail-grid">
          <div class="detail-item">
            <label>参数名称</label>
            <span>{{ parameter.name }}</span>
          </div>
          <div class="detail-item">
            <label>参数类型</label>
            <span>{{ parameter.parameter_type_name }}</span>
          </div>
          <div class="detail-item">
            <label>核保规则</label>
            <span>{{ parameter.rule_name }}</span>
          </div>
          <div class="detail-item">
            <label>参数值</label>
            <span>{{ parameter.value }}</span>
          </div>
          <div class="detail-item">
            <label>状态</label>
            <BaseTag :type="parameter.status === 'enabled' ? 'success' : 'danger'">
              {{ parameter.status === 'enabled' ? '启用' : '禁用' }}
            </BaseTag>
          </div>
          <div class="detail-item">
            <label>创建时间</label>
            <span>{{ parameter.created_at }}</span>
          </div>
          <div class="detail-item">
            <label>更新时间</label>
            <span>{{ parameter.updated_at }}</span>
          </div>
        </div>
      </div>

      <div class="detail-section">
        <h2>参数描述</h2>
        <p class="description">{{ parameter.description || '暂无描述' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from '@/composables/useMessage'
import { getParameter } from '@/api/underwriting'
import type { Parameter } from '@/types/underwriting'

const router = useRouter()
const route = useRoute()
const message = useMessage()

const parameter = ref<Parameter>({
  id: 0,
  name: '',
  parameter_type_id: 0,
  parameter_type_name: '未知',
  rule_id: 0,
  rule_name: '未知',
  value: '',
  description: '',
  status: '',
  created_at: '',
  updated_at: ''
})

// 加载参数详情
const loadParameterDetail = async () => {
  console.log('开始加载参数详情, ID:', route.params.id);
  try {
    const res = await getParameter(Number(route.params.id));
    console.log('参数详情加载成功:', res.data);
    parameter.value = res.data;
  } catch (error) {
    console.error('获取参数详情失败:', error);
    message.error('获取参数详情失败');
  }
}

// 编辑
const handleEdit = () => {
  console.log('点击编辑按钮, 参数ID:', route.params.id);
  const editPath = `/underwriting/ai-parameter/${route.params.id}/edit`;
  console.log('跳转路径:', editPath);
  router.push(editPath);
}

onMounted(() => {
  console.log('AIParameterDetailView组件加载完成');
  loadParameterDetail();
})
</script>

<style lang="scss" scoped>
.ai-parameter-detail-page {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      h1 {
        margin: 0;
        font-size: 24px;
      }
    }
  }

  .detail-container {
    background: #fff;
    border-radius: 4px;
    padding: 24px;

    .detail-section {
      & + .detail-section {
        margin-top: 32px;
      }

      h2 {
        margin: 0 0 16px;
        font-size: 18px;
        font-weight: 500;
      }
    }

    .detail-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24px;
    }

    .detail-item {
      label {
        display: block;
        color: #666;
        margin-bottom: 8px;
      }

      span {
        color: #333;
        font-size: 14px;
      }
    }

    .description {
      color: #333;
      font-size: 14px;
      line-height: 1.6;
      margin: 0;
    }
  }
}
</style> 