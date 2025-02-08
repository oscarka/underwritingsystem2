/**
 * CRUD功能初始化
 */
document.addEventListener('DOMContentLoaded', function () {
    // 检查页面是否需要初始化CRUD
    const crudContainer = document.querySelector('[data-crud]');
    if (!crudContainer) return;

    // 获取CRUD配置
    const crudConfig = {
        autoInit: true,
        debug: false,
        components: {
            table: '#data-table',
            form: '#crud-form',
            search: '#search-form'
        },
        endpoints: {
            list: crudContainer.dataset.listUrl || '',
            create: crudContainer.dataset.createUrl || '',
            update: crudContainer.dataset.updateUrl || '',
            delete: crudContainer.dataset.deleteUrl || '',
            view: crudContainer.dataset.viewUrl || '',
            batchDelete: crudContainer.dataset.batchDeleteUrl || ''
        }
    };

    try {
        console.log('Initializing CRUD with config:', crudConfig);
        const crud = new CrudCoordinator(crudConfig);
        crud.init();
    } catch (error) {
        console.error('Failed to initialize CRUD:', error);
    }
}); 