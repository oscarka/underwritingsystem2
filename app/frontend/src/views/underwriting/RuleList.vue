<template>
  <div class="rule-list">
    <div class="header">
      <h2>核保规则管理</h2>
      <div class="actions">
        <a-button type="primary" @click="handleCreate">新增规则</a-button>
      </div>
    </div>

    <div class="search-bar">
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="规则名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入规则名称" />
        </a-form-item>
        <a-form-item label="规则状态">
          <a-select v-model:value="searchForm.status" placeholder="请选择状态" style="width: 120px">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="启用">启用</a-select-option>
            <a-select-option value="禁用">禁用</a-select-option>
            <a-select-option value="已导入">已导入</a-select-option>
            <a-select-option value="草稿">草稿</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="疾病大类">
          <a-select v-model:value="searchForm.diseaseCategory" placeholder="请选择疾病大类" style="width: 200px">
            <a-select-option value="">全部</a-select-option>
            <a-select-option v-for="category in diseaseCategories" :key="category.code" :value="category.code">
              {{ category.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">搜索</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </div>

    <div v-if="!loading && (!rules || rules.length === 0)" class="empty-data">
      暂无数据
    </div>

    <a-table
      v-else
      :columns="columns"
      :data-source="rules"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
      rowKey="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="getStatusColor(record.status)">
            {{ record.status }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <BaseButton size="small" @click="handleView(record)">查看</BaseButton>
            <BaseButton size="small" @click="handleEdit(record)">编辑</BaseButton>
            <BaseButton size="small" @click="handleImport(record)">导入</BaseButton>
            <BaseButton v-if="record.has_data" size="small" @click="handleExport(record)">导出</BaseButton>
            <BaseButton size="small" type="danger" @click="handleDelete(record)">删除</BaseButton>
          </a-space>
        </template>
      </template>
    </a-table>

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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { UploadOutlined } from '@ant-design/icons-vue';
import type { UploadProps } from 'ant-design-vue';
import type { AxiosError } from 'axios';
import ruleApi from '@/api/underwriting';
import { RuleStatus } from '@/types/underwriting';
import type { Rule, DiseaseCategory } from '@/types/underwriting';
import type { PaginationData } from '@/types/api';

console.log('RuleList组件初始化');

const router = useRouter();
const loading = ref(false);
const rules = ref<Rule[]>([]);
const diseaseCategories = ref<DiseaseCategory[]>([]);

// 搜索表单
const searchForm = reactive({
  name: '',
  status: undefined as RuleStatus | undefined,
  diseaseCategory: ''
});

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: (total: number) => `共 ${total} 条`
});

// 表格列定义
const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id'
  },
  {
    title: '规则名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '版本',
    dataIndex: 'version',
    key: 'version'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status'
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at'
  },
  {
    title: '更新时间',
    dataIndex: 'updated_at',
    key: 'updated_at'
  },
  {
    title: '操作',
    key: 'action',
    width: 200
  }
];

// 导入相关
const importModalVisible = ref(false);
const importLoading = ref(false);
const fileList = ref<any[]>([]);
const fileContent = ref<any>(null);
const currentRule = ref<Rule | null>(null);

// 加载数据
const loadData = async () => {
  try {
    console.log('[RuleList] 开始加载规则列表数据:', {
      searchForm,
      pagination: {
        current: pagination.current,
        pageSize: pagination.pageSize
      }
    });
    
    loading.value = true;
    const res = await ruleApi.getRules({
      name: searchForm.name,
      status: searchForm.status,
      diseaseCategory: searchForm.diseaseCategory,
      page: pagination.current,
      pageSize: pagination.pageSize
    });
    
    console.log('[RuleList] 获取规则列表原始响应:', res);
    
    if (res.code === 200 && res.data) {
      console.log('[RuleList] 开始处理响应数据');
      rules.value = res.data.list;
      pagination.total = res.data.pagination.total;
      
      // 打印每条规则的详细信息
      rules.value.forEach((rule, index) => {
        console.log(`[RuleList] 规则 ${index + 1}:`, {
          id: rule.id,
          name: rule.name,
          status: rule.status,
          version: rule.version,
          has_data: rule.has_data,
          created_at: rule.created_at,
          updated_at: rule.updated_at
        });
      });
      
      console.log('[RuleList] 规则列表数据加载成功:', {
        rulesCount: rules.value.length,
        total: pagination.total,
        firstRule: rules.value[0],
        lastRule: rules.value[rules.value.length - 1]
      });
    } else {
      console.warn('[RuleList] 响应数据异常:', {
        code: res.code,
        message: res.message,
        hasData: !!res.data
      });
      rules.value = [];
      pagination.total = 0;
    }
  } catch (error: unknown) {
    console.error('[RuleList] 获取规则列表异常:', error);
    if (error instanceof Error) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error('[RuleList] 错误响应详情:', {
          status: axiosError.response.status,
          statusText: axiosError.response.statusText,
          data: axiosError.response.data,
          headers: axiosError.response.headers
        });
      }
    }
    rules.value = [];
    pagination.total = 0;
  } finally {
    loading.value = false;
    console.log('[RuleList] 加载完成，当前状态:', {
      loading: loading.value,
      rulesCount: rules.value.length,
      total: pagination.total
    });
  }
};

// 加载疾病大类
const loadDiseaseCategories = async () => {
  try {
    console.log('[RuleList] 开始加载疾病大类数据');
    const res = await ruleApi.getDiseaseCategories();
    console.log('[RuleList] 获取疾病大类响应:', {
      code: res.code,
      message: res.message,
      dataLength: res.data?.length
    });
    
    if (res.code === 200 && res.data) {
      diseaseCategories.value = res.data;
      console.log('[RuleList] 疾病大类数据加载成功:', {
        count: diseaseCategories.value.length,
        categories: diseaseCategories.value.map(c => ({
          code: c.code,
          name: c.name
        }))
      });
    }
  } catch (error: unknown) {
    console.error('[RuleList] 获取疾病大类异常:', error);
    if (error instanceof Error) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error('[RuleList] 错误响应:', {
          status: axiosError.response.status,
          data: axiosError.response.data
        });
      }
    }
  }
};

// 搜索
const handleSearch = () => {
  console.log('[RuleList] 执行搜索, 搜索条件:', {
    name: searchForm.name,
    status: searchForm.status,
    diseaseCategory: searchForm.diseaseCategory
  });
  pagination.current = 1;
  loadData();
};

// 重置
const handleReset = () => {
  console.log('[RuleList] 开始重置搜索条件');
  searchForm.name = '';
  searchForm.status = undefined;
  searchForm.diseaseCategory = '';
  console.log('[RuleList] 重置后的搜索条件:', {
    name: searchForm.name,
    status: searchForm.status,
    diseaseCategory: searchForm.diseaseCategory
  });
  handleSearch();
};

// 表格变化
const handleTableChange = (pag: any) => {
  console.log('[RuleList] 表格分页变化:', {
    current: pag.current,
    pageSize: pag.pageSize,
    oldCurrent: pagination.current,
    oldPageSize: pagination.pageSize
  });
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  loadData();
};

// 新增规则
const handleCreate = () => {
  console.log('点击新增规则按钮');
  router.push('/underwriting/rules/create');
};

// 编辑规则
const handleEdit = (record: Rule) => {
  console.log('点击编辑按钮, 规则:', record);
  router.push(`/underwriting/rules/${record.id}`);
};

// 导入数据
const handleImport = (record: Rule) => {
  console.log('[RuleList] 点击导入按钮:', {
    id: record.id,
    name: record.name,
    version: record.version,
    status: record.status,
    has_data: record.has_data
  });
  currentRule.value = record;
  importModalVisible.value = true;
};

// 导出数据
const handleExport = async (record: Rule) => {
  try {
    console.log('[RuleList] 开始导出规则数据:', {
      id: record.id,
      name: record.name,
      version: record.version,
      status: record.status
    });
    
    const res = await ruleApi.exportRuleData(record.id);
    console.log('[RuleList] 导出规则响应:', {
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
      link.download = `rule_${record.id}_export.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('导出成功');
      console.log('[RuleList] 规则数据导出成功:', {
        id: record.id,
        fileName: `rule_${record.id}_export.json`,
        fileSize: blob.size
      });
    }
  } catch (error: unknown) {
    console.error('[RuleList] 导出规则数据失败:', error);
    if (error instanceof Error) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error('[RuleList] 错误响应:', {
          status: axiosError.response.status,
          data: axiosError.response.data
        });
      }
    }
  }
};

// 删除规则
const handleDelete = async (record: Rule) => {
  try {
    console.log('点击删除按钮, 规则:', {
      id: record.id,
      name: record.name
    });
    
    const res = await ruleApi.deleteRule(record.id);
    if (res.code === 200) {
      message.success('删除成功');
      loadData();
    }
  } catch (error) {
    console.error('删除规则失败:', error);
  }
};

const beforeUpload: UploadProps['beforeUpload'] = (file: File) => {
  console.log('[RuleList] 上传文件前校验:', {
    fileName: file.name,
    fileType: file.type,
    fileSize: file.size
  });
  
  const isJSON = file.type === 'application/json';
  if (!isJSON) {
    message.error('只能上传JSON文件!');
    console.warn('[RuleList] 文件类型错误:', {
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
      console.log('[RuleList] 文件内容读取成功:', {
        contentLength: content.length,
        preview: content.slice(0, 100) + '...'
      });
      
      fileContent.value = JSON.parse(content);
      console.log('[RuleList] 文件内容解析成功:', {
        dataStructure: Object.keys(fileContent.value)
      });
    } catch (e) {
      message.error('文件格式错误!');
      console.error('[RuleList] 文件内容解析失败:', e);
      fileContent.value = null;
    }
  };
  return false;
};

const confirmImport = async () => {
  if (!fileContent.value) {
    message.error('请先选择文件');
    console.warn('[RuleList] 导入确认失败: 未选择文件');
    return;
  }
  
  try {
    console.log('[RuleList] 开始导入数据:', {
      ruleId: currentRule.value?.id,
      ruleName: currentRule.value?.name,
      contentKeys: Object.keys(fileContent.value)
    });
    
    importLoading.value = true;
    const res = await ruleApi.importRuleData(fileContent.value);
    console.log('[RuleList] 导入响应:', {
      code: res.code,
      message: res.message
    });
    
    if (res.code === 200) {
      message.success('导入成功');
      importModalVisible.value = false;
      await loadData();
      console.log('[RuleList] 导入成功，已重新加载数据');
    }
  } catch (error: unknown) {
    console.error('[RuleList] 导入数据失败:', error);
    if (error instanceof Error) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error('[RuleList] 错误响应:', {
          status: axiosError.response.status,
          data: axiosError.response.data
        });
      }
    }
  } finally {
    importLoading.value = false;
    fileList.value = [];
    fileContent.value = null;
    currentRule.value = null;
  }
};

const cancelImport = () => {
  console.log('取消导入');
  importModalVisible.value = false;
  fileList.value = [];
  fileContent.value = null;
  currentRule.value = null;
};

const getStatusColor = (status: string) => {
  switch (status) {
    case '启用':
      return 'success';
    case '已导入':
      return 'processing';
    case '草稿':
      return 'default';
    case '禁用':
      return 'error';
    default:
      return 'default';
  }
};

// 添加查看规则方法
const handleView = (record: Rule) => {
  console.log('[RuleList] 点击查看按钮:', {
    id: record.id,
    name: record.name,
    version: record.version
  });
  router.push(`/underwriting/rules/${record.id}/detail`);
};

onMounted(() => {
  console.log('[RuleList] 组件挂载开始');
  Promise.all([loadData(), loadDiseaseCategories()])
    .then(() => {
      console.log('[RuleList] 初始数据加载完成');
    })
    .catch((error) => {
      console.error('[RuleList] 初始数据加载失败:', error);
    });
});
</script>

<style scoped>
.rule-list {
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.search-bar {
  margin-bottom: 24px;
  padding: 24px;
  background: #fff;
  border-radius: 2px;
}

.upload-tip {
  margin-top: 8px;
  color: #666;
}
</style> 