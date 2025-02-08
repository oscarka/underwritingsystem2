<template>
  <div class="rule-detail">
    <div class="header">
      <h2>规则详情</h2>
      <div class="actions">
        <a-button @click="goBack">返回</a-button>
      </div>
    </div>
    
    <!-- 导入数据对话框 -->
    <a-modal
      v-model:visible="importModalVisible"
      title="导入数据"
      @ok="confirmImport"
      @cancel="cancelImport"
      :confirmLoading="importLoading"
    >
      <a-upload
        v-model:fileList="fileList"
        :beforeUpload="beforeUpload"
        :maxCount="1"
      >
        <a-button>
          <upload-outlined />
          选择文件
        </a-button>
      </a-upload>
      <div class="upload-tip">请上传JSON格式的规则数据文件</div>
    </a-modal>

    <!-- 现有内容 -->
    <div class="content">
      <template v-if="rule">
        <div class="info-item">
          <span class="label">规则ID:</span>
          <span class="value">{{ rule.id }}</span>
        </div>
        <div class="info-item">
          <span class="label">规则名称:</span>
          <span class="value">{{ rule.name }}</span>
        </div>
        <div class="info-item">
          <span class="label">版本:</span>
          <span class="value">{{ rule.version }}</span>
        </div>
        <div class="info-item">
          <span class="label">状态:</span>
          <span class="value">{{ rule.status }}</span>
        </div>
        <div class="info-item">
          <span class="label">描述:</span>
          <span class="value">{{ rule.description }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message, Upload, Modal, Button } from 'ant-design-vue';
import { UploadOutlined } from '@ant-design/icons-vue';
import type { UploadProps } from 'ant-design-vue';
import type { AxiosError } from 'axios';
import ruleApi from '@/api/underwriting';
import type { Rule } from '@/types/underwriting';

const route = useRoute();
const router = useRouter();
const rule = ref<Rule | null>(null);

// 导入相关
const importModalVisible = ref(false);
const importLoading = ref(false);
const fileList = ref<any[]>([]);
const fileContent = ref<any>(null);

// 获取规则ID
const getRuleId = () => {
  const id = route.params.id as string;
  console.log('[RuleDetail] 当前规则ID:', id);
  return id;
};

// 加载数据
const loadData = async () => {
  try {
    console.log('[RuleDetail] 开始加载规则详情');
    const res = await ruleApi.getRuleDetail(getRuleId());
    console.log('[RuleDetail] 获取规则详情响应:', {
      code: res.code,
      message: res.message,
      data: res.data ? {
        id: res.data.id,
        name: res.data.name,
        version: res.data.version,
        status: res.data.status
      } : null
    });
    
    if (res.code === 200 && res.data) {
      rule.value = res.data;
      console.log('[RuleDetail] 规则详情加载成功:', {
        id: rule.value.id,
        name: rule.value.name,
        version: rule.value.version,
        status: rule.value.status,
        hasQuestions: Boolean(rule.value.questions?.length),
        hasAnswers: Boolean(rule.value.answers?.length)
      });
    }
  } catch (error: unknown) {
    console.error('[RuleDetail] 获取规则详情失败:', error);
    if (error instanceof Error) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error('[RuleDetail] 错误响应:', {
          status: axiosError.response.status,
          data: axiosError.response.data
        });
      }
    }
  }
};

// 返回列表
const goBack = () => {
  console.log('[RuleDetail] 返回列表页');
  router.push('/underwriting/rules');
};

// 导出功能
const handleExport = async () => {
  try {
    const ruleId = getRuleId();
    console.log('[RuleDetail] 开始导出规则数据:', {
      id: ruleId,
      rule: rule.value ? {
        name: rule.value.name,
        version: rule.value.version,
        status: rule.value.status
      } : null
    });
    
    const res = await ruleApi.exportRuleData(ruleId);
    console.log('[RuleDetail] 导出规则响应:', {
      code: res.code,
      message: res.message,
      dataSize: res.data ? JSON.stringify(res.data).length : 0
    });
    
    if (res.code === 200 && res.data) {
      // 创建下载
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `rule_${ruleId}_export.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('导出成功');
      console.log('[RuleDetail] 规则数据导出成功:', {
        id: ruleId,
        fileName: `rule_${ruleId}_export.json`,
        fileSize: blob.size
      });
    } else {
      message.error(res.message || '导出失败');
      console.error('[RuleDetail] 导出失败:', {
        code: res.code,
        message: res.message
      });
    }
  } catch (error: unknown) {
    console.error('[RuleDetail] 导出失败:', error);
    if (error instanceof Error) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        const responseData = axiosError.response.data as { message?: string };
        console.error('[RuleDetail] 错误响应:', {
          status: axiosError.response.status,
          data: responseData
        });
        message.error(`导出失败: ${responseData.message || '未知错误'}`);
      } else {
        message.error('导出失败: 网络错误');
      }
    } else {
      message.error('导出失败: 未知错误');
    }
  }
};

// 导入功能
const handleImport = async () => {
  if (!fileContent.value) {
    message.error('请先选择文件');
    console.warn('[RuleDetail] 导入确认失败: 未选择文件');
    return;
  }
  
  try {
    console.log('[RuleDetail] 开始导入数据:', {
      ruleId: getRuleId(),
      contentKeys: Object.keys(fileContent.value)
    });
    
    importLoading.value = true;
    const res = await ruleApi.importRuleData(fileContent.value);
    console.log('[RuleDetail] 导入响应:', {
      code: res.code,
      message: res.message
    });
    
    if (res.code === 200) {
      message.success('导入成功');
      importModalVisible.value = false;
      await loadData();
      console.log('[RuleDetail] 导入成功，已重新加载数据');
    }
  } catch (error: unknown) {
    console.error('[RuleDetail] 导入失败:', error);
    if (error instanceof Error) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error('[RuleDetail] 错误响应:', {
          status: axiosError.response.status,
          data: axiosError.response.data
        });
      }
    }
  } finally {
    importLoading.value = false;
    fileList.value = [];
    fileContent.value = null;
  }
};

const beforeUpload: UploadProps['beforeUpload'] = (file: File) => {
  console.log('[RuleDetail] 上传文件前校验:', {
    fileName: file.name,
    fileType: file.type,
    fileSize: file.size
  });
  
  const isJSON = file.type === 'application/json';
  if (!isJSON) {
    message.error('只能上传JSON文件!');
    console.warn('[RuleDetail] 文件类型错误:', {
      expectedType: 'application/json',
      actualType: file.type
    });
    return false;
  }
  
  // 读取文件内容
  const reader = new FileReader();
  reader.readAsText(file);
  reader.onload = () => {
    try {
      const content = reader.result as string;
      console.log('[RuleDetail] 文件内容读取成功:', {
        contentLength: content.length,
        preview: content.slice(0, 100) + '...'
      });
      
      fileContent.value = JSON.parse(content);
      console.log('[RuleDetail] 文件内容解析成功:', {
        dataStructure: Object.keys(fileContent.value)
      });
    } catch (e) {
      message.error('文件格式错误!');
      console.error('[RuleDetail] 文件内容解析失败:', e);
      fileContent.value = null;
    }
  };
  return false;
};

const confirmImport = async () => {
  if (!fileContent.value) {
    message.error('请先选择文件');
    console.warn('[RuleDetail] 导入确认失败: 未选择文件');
    return;
  }
  
  try {
    console.log('[RuleDetail] 开始导入数据:', {
      ruleId: getRuleId(),
      contentKeys: Object.keys(fileContent.value)
    });
    
    importLoading.value = true;
    const res = await ruleApi.importRuleData(fileContent.value);
    console.log('[RuleDetail] 导入响应:', {
      code: res.code,
      message: res.message
    });
    
    if (res.code === 200) {
      message.success('导入成功');
      importModalVisible.value = false;
      await loadData();
      console.log('[RuleDetail] 导入成功，已重新加载数据');
    }
  } catch (error: unknown) {
    console.error('[RuleDetail] 导入失败:', error);
    if (error instanceof Error) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error('[RuleDetail] 错误响应:', {
          status: axiosError.response.status,
          data: axiosError.response.data
        });
      }
    }
  } finally {
    importLoading.value = false;
    fileList.value = [];
    fileContent.value = null;
  }
};

const cancelImport = () => {
  console.log('[RuleDetail] 取消导入');
  importModalVisible.value = false;
  fileList.value = [];
  fileContent.value = null;
};

onMounted(() => {
  console.log('[RuleDetail] 组件挂载');
  loadData();
});
</script>

<style scoped>
.rule-detail {
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.actions {
  display: flex;
  gap: 8px;
}

.upload-tip {
  margin-top: 8px;
  color: #666;
}

.content {
  background: #fff;
  padding: 24px;
  border-radius: 2px;
}

.info-item {
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
}

.label {
  width: 100px;
  color: #666;
  text-align: right;
  padding-right: 12px;
}

.value {
  flex: 1;
}
</style>