<template>
  <!-- No changes to template section -->
</template>

<script setup>
import { onMounted, ref } from 'vue'

const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref({})
const total = ref(0)
const tableData = ref([])
const loading = ref(false)

onMounted(async () => {
    console.log('[RuleView] 组件挂载开始')
    try {
        await loadData()
        console.log('[RuleView] 初始数据加载完成')
    } catch (error) {
        console.error('[RuleView] 初始数据加载失败:', error)
    }
})

const loadData = async () => {
    console.log('[RuleView] 开始加载数据:', {
        currentPage: currentPage.value,
        pageSize: pageSize.value,
        searchQuery: searchQuery
    })
    
    try {
        loading.value = true
        const response = await getRuleList({
            page: currentPage.value,
            size: pageSize.value,
            ...searchQuery
        })
        console.log('[RuleView] 获取数据响应:', {
            status: response.status,
            headers: response.headers,
            data: response.data
        })
        
        total.value = response.data.total
        tableData.value = response.data.items
        console.log('[RuleView] 数据加载成功:', {
            total: total.value,
            itemsCount: tableData.value.length
        })
    } catch (error) {
        console.error('[RuleView] 数据加载失败:', {
            error,
            errorMessage: error.message,
            errorResponse: error.response
        })
        throw error
    } finally {
        loading.value = false
        console.log('[RuleView] 数据加载完成')
    }
}

const handleSearch = () => {
    console.log('[RuleView] 执行搜索:', searchQuery)
    currentPage.value = 1
    loadData()
}

const handleReset = () => {
    console.log('[RuleView] 重置搜索条件')
    Object.keys(searchQuery).forEach(key => {
        searchQuery[key] = ''
    })
    currentPage.value = 1
    loadData()
}

const handleEdit = (row) => {
    console.log('[RuleView] 编辑规则:', {
        ruleId: row.id,
        ruleName: row.name,
        currentData: row
    })
    // ... existing code ...
}

const handleDelete = async (row) => {
    console.log('[RuleView] 准备删除规则:', {
        ruleId: row.id,
        ruleName: row.name
    })
    try {
        // ... existing code ...
        console.log('[RuleView] 规则删除成功')
    } catch (error) {
        console.error('[RuleView] 规则删除失败:', {
            error,
            errorMessage: error.message,
            errorResponse: error.response
        })
    }
}
</script>

<style>
  /* No changes to style section */
</style> 