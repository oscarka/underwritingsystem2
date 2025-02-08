/**
 * 主入口文件
 * 负责初始化全局组件和配置
 */

// 创建全局事件总线
window.eventBus = new EventBus({
    debug: false
});

// 创建权限控制实例
window.permission = new Permission({
    debug: false,
    checkPermission: async (permission) => {
        try {
            const response = await fetch(`/api/permissions/check/${permission}`);
            if (!response.ok) return false;
            const data = await response.json();
            return data.hasPermission;
        } catch {
            return false;
        }
    }
});

// 创建全局 Toast 实例
window.toast = new Toast({
    position: 'top-right',
    duration: 3000,
    showProgress: true,
    pauseOnHover: true,
    maxToasts: 5
});

// 创建全局 Loading 实例
window.loading = new Loading({
    text: '加载中...',
    spinnerClass: 'spinner-border text-primary',
    zIndex: 1050
});

// 配置 Bootstrap Table 默认选项
$.extend($.fn.bootstrapTable.defaults, {
    locale: 'zh-CN',
    classes: 'table table-bordered table-hover',
    theadClasses: 'thead-light',
    toolbar: '.table-toolbar',
    showRefresh: true,
    showColumns: true,
    pagination: true,
    pageSize: 10,
    pageList: [10, 25, 50, 100],
    sidePagination: 'server',
    method: 'GET',
    contentType: 'application/json',
    queryParamsType: '',
    responseHandler: (res) => {
        return {
            total: res.total || 0,
            rows: res.rows || []
        };
    }
});

// 注册全局事件处理
document.addEventListener('DOMContentLoaded', () => {
    // 处理所有具有 data-action 属性的元素点击事件
    document.body.addEventListener('click', (e) => {
        const actionElement = e.target.closest('[data-action]');
        if (actionElement) {
            const action = actionElement.dataset.action;
            const id = actionElement.dataset.id;

            window.eventBus.emit('action:click', {
                type: action,
                id: id,
                element: actionElement
            });
        }
    });

    // 处理所有具有 data-permission 属性的元素
    document.querySelectorAll('[data-permission]').forEach(async (element) => {
        const permission = element.dataset.permission;
        const hasPermission = await window.permission.check(permission);

        if (!hasPermission) {
            if (element instanceof HTMLButtonElement) {
                element.disabled = true;
                element.title = '没有操作权限';
            } else {
                element.style.display = 'none';
            }
        }
    });

    // 处理子菜单的展开/收起
    $('.has-submenu > a').click(function (e) {
        e.preventDefault();
        $(this).parent().toggleClass('active');
        $(this).next('.submenu').slideToggle();
    });

    // 根据当前页面URL激活对应菜单
    let currentPath = window.location.pathname;
    $(`a[href="${currentPath}"]`).parents('.has-submenu').addClass('active');
    $(`a[href="${currentPath}"]`).parents('.submenu').show();

    // 初始化 Bootstrap tabs
    $('#ruleTab a').on('click', function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    // 如果URL中有hash，切换到对应的tab
    let hash = window.location.hash;
    if (hash) {
        $('#ruleTab a[href="' + hash + '"]').tab('show');
    }

    // 切换tab时更新URL hash
    $('#ruleTab a').on('shown.bs.tab', function (e) {
        window.location.hash = e.target.hash;
    });
}); 