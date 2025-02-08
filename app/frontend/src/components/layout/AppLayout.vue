<template>
  <div class="app-layout">
    <aside class="sidebar" :class="{ 'is-collapsed': collapsed }">
      <div class="sidebar-header">
        <h1 class="logo">Logo</h1>
        <button class="collapse-btn" @click="toggleCollapse">
          <span class="icon">{{ collapsed ? '→' : '←' }}</span>
        </button>
      </div>
      <nav class="menu">
        <template v-for="item in menuItems" :key="item.key">
          <!-- 带子菜单的菜单项 -->
          <div v-if="item.children" class="menu-group">
            <div class="menu-group-title" @click="toggleSubMenu(item.key)">
              <span class="icon">{{ item.icon }}</span>
              <span class="text" v-show="!collapsed">{{ item.label }}</span>
              <span class="arrow" v-show="!collapsed">{{ isSubMenuOpen(item.key) ? '▼' : '▶' }}</span>
            </div>
            <div class="sub-menu" v-show="isSubMenuOpen(item.key) && !collapsed">
              <router-link
                v-for="subItem in item.children"
                :key="subItem.key"
                :to="subItem.path"
                class="menu-item sub-menu-item"
                active-class="is-active"
              >
                <span class="icon">{{ subItem.icon }}</span>
                <span class="text">{{ subItem.label }}</span>
              </router-link>
            </div>
          </div>
          <!-- 普通菜单项 -->
          <router-link
            v-else
            :to="item.path"
            class="menu-item"
            active-class="is-active"
          >
            <span class="icon">{{ item.icon }}</span>
            <span class="text" v-show="!collapsed">{{ item.label }}</span>
          </router-link>
        </template>
      </nav>
    </aside>
    
    <div class="main-content">
      <header class="header">
        <div class="breadcrumb">
          <!-- 面包屑导航 -->
        </div>
        <div class="actions">
          <BaseThemeSwitch />
          <BaseButton>退出</BaseButton>
        </div>
      </header>
      <main class="content">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// 侧边栏折叠状态
const collapsed = ref(false)

// 子菜单展开状态
const openSubMenus = ref<Set<string>>(new Set())

// 切换子菜单
const toggleSubMenu = (key: string) => {
  if (openSubMenus.value.has(key)) {
    openSubMenus.value.delete(key)
  } else {
    openSubMenus.value.add(key)
  }
}

// 检查子菜单是否展开
const isSubMenuOpen = (key: string) => openSubMenus.value.has(key)

// 菜单项配置
const menuItems = [
  {
    key: 'dashboard',
    label: '仪表盘',
    icon: '📊',
    path: '/dashboard'
  },
  {
    key: 'product',
    label: '产品管理',
    icon: '📦',
    children: [
      {
        key: 'channels',
        label: '渠道管理',
        icon: '🔀',
        path: '/product/channels'
      },
      {
        key: 'companies',
        label: '保司管理',
        icon: '🏢',
        path: '/product/companies'
      },
      {
        key: 'config',
        label: '产品配置',
        icon: '⚙️',
        path: '/product/config'
      }
    ]
  },
  {
    key: 'underwriting',
    label: '核保管理',
    icon: '📋',
    children: [
      {
        key: 'rules',
        label: '核保规则管理',
        icon: '📜',
        path: '/underwriting/rules'
      },
      {
        key: 'questions',
        label: '问题和结论配置',
        icon: '🔍',
        path: '/underwriting/questions'
      },
      {
        key: 'config',
        label: '智核参数配置',
        icon: '⚙️',
        path: '/underwriting/ai-parameter'
      }
    ]
  }
]

// 切换折叠状态
const toggleCollapse = () => {
  collapsed.value = !collapsed.value
  // 如果折叠，关闭所有子菜单
  if (collapsed.value) {
    openSubMenus.value.clear()
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg-container);
  color: var(--color-text-primary);
}

.sidebar {
  width: 240px;
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  transition: all var(--transition-normal);
  border-right: 1px solid var(--color-border);
}

.sidebar.is-collapsed {
  width: 80px;
}

.sidebar-header {
  height: 64px;
  padding: 0 var(--spacing-md);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border);
}

.logo {
  font-size: var(--font-size-lg);
  margin: 0;
}

.collapse-btn {
  background: none;
  border: none;
  color: var(--color-text-primary);
  cursor: pointer;
  padding: var(--spacing-xs);
}

.menu {
  padding: var(--spacing-md) 0;
}

.menu-group-title {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.menu-group-title:hover {
  color: var(--color-primary);
  background: var(--color-bg-spotlight);
}

.menu-group-title .arrow {
  margin-left: auto;
  font-size: var(--font-size-sm);
}

.sub-menu {
  background: color-mix(in srgb, var(--color-bg-elevated) 50%, transparent);
}

.sub-menu-item {
  padding-left: calc(var(--spacing-md) * 2) !important;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-normal);
  white-space: nowrap;
  overflow: hidden;
}

.menu-item:hover {
  color: var(--color-primary);
  background: var(--color-bg-spotlight);
}

.menu-item.is-active {
  color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 10%, transparent);
}

.menu-item .icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--spacing-md);
  font-size: var(--font-size-lg);
}

.menu-item .text {
  transition: opacity var(--transition-normal);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-base);
}

.header {
  height: 64px;
  background: var(--color-bg-elevated);
  padding: 0 var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-sm);
}

.content {
  flex: 1;
  padding: var(--spacing-lg);
}

.actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    height: 100vh;
    z-index: 1000;
    transform: translateX(0);
  }

  .sidebar.is-collapsed {
    transform: translateX(-100%);
  }

  .main-content {
    margin-left: 0;
  }
}
</style> 