/**
 * 表格组件基类
 * 继承自BaseComponent，提供表格相关的通用功能
 */
class TableComponent extends BaseComponent {
    static defaultConfig = {
        ...BaseComponent.defaultConfig,
        url: '',
        method: 'GET',
        pagination: true,
        pageSize: 10,
        pageList: [10, 25, 50, 100],
        sortable: true,
        search: false,
        showRefresh: true,
        showToggle: false,
        showColumns: true,
        showExport: false,
        striped: true,
        classes: 'table table-bordered table-hover',
        theadClasses: 'thead-light',
        loadingTemplate: '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>'
    };

    constructor(element, config = {}) {
        super(element, config);
        this.$table = null;
        this._currentData = [];
    }

    /**
     * 初始化表格组件
     * @protected
     */
    _init() {
        super._init();

        // 检查依赖
        if (typeof $ === 'undefined') {
            throw new Error('jQuery is required for TableComponent');
        }
        if (typeof $.fn.bootstrapTable === 'undefined') {
            throw new Error('bootstrap-table is required for TableComponent');
        }

        this._initTable();
        this._initTableEvents();
    }

    /**
     * 初始化表格
     * @protected
     */
    _initTable() {
        const options = {
            url: this.config.url,
            method: this.config.method,
            pagination: this.config.pagination,
            pageSize: this.config.pageSize,
            pageList: this.config.pageList,
            sortable: this.config.sortable,
            search: this.config.search,
            showRefresh: this.config.showRefresh,
            showToggle: this.config.showToggle,
            showColumns: this.config.showColumns,
            showExport: this.config.showExport,
            striped: this.config.striped,
            classes: this.config.classes,
            theadClasses: this.config.theadClasses,
            loadingTemplate: this.config.loadingTemplate,
            columns: this.config.columns || [],
            queryParams: (params) => this._queryParams(params),
            responseHandler: (res) => this._responseHandler(res),
            onLoadSuccess: (data) => this._onLoadSuccess(data),
            onLoadError: (status, res) => this._onLoadError(status, res)
        };

        try {
            this.$table = $(this.element).bootstrapTable(options);
            this._debug('Table initialized with options:', options);
        } catch (error) {
            this._debug('Error initializing table:', error);
            throw error;
        }
    }

    /**
     * 初始化表格事件
     * @protected
     */
    _initTableEvents() {
        // 监听行点击事件
        this.element.addEventListener('click', (e) => {
            const actionButton = e.target.closest('[data-action]');
            if (actionButton) {
                const action = actionButton.dataset.action;
                const row = this._getRowData(actionButton);
                this._handleAction(action, row);
            }
        });

        // 监听外部事件
        window.eventBus.on('search:submitted', (data) => this.refresh(data));
        window.eventBus.on('search:reset', () => this.refresh({}));
    }

    /**
     * 处理查询参数
     * @param {Object} params 查询参数
     * @returns {Object} 处理后的参数
     * @protected
     */
    _queryParams(params) {
        const queryParams = {
            page: params.offset / params.limit + 1,
            per_page: params.limit,
            search: params.search,
            sort: params.sort,
            order: params.order
        };
        this._debug('Query params:', queryParams);
        return queryParams;
    }

    /**
     * 处理响应数据
     * @param {Object} res 响应数据
     * @returns {Object} 处理后的数据
     * @protected
     */
    _responseHandler(res) {
        this._debug('Response data:', res);
        if (res.code === 0 && res.data) {
            return {
                total: res.data.total || 0,
                rows: res.data.items || []
            };
        }
        return {
            total: 0,
            rows: []
        };
    }

    /**
     * 加载成功回调
     * @param {Object} data 加载的数据
     * @protected
     */
    _onLoadSuccess(data) {
        this._currentData = data.rows;
        this._debug('Load success:', data);
        this.emit('load:success', { data });
    }

    /**
     * 加载失败回调
     * @param {number} status HTTP状态码
     * @param {Object} res 响应数据
     * @protected
     */
    _onLoadError(status, res) {
        this._debug('Load error:', status, res);
        this.emit('load:error', { status, res });
    }

    /**
     * 获取行数据
     * @param {HTMLElement} element 触发事件的元素
     * @returns {Object} 行数据
     * @protected
     */
    _getRowData(element) {
        const tr = element.closest('tr');
        if (!tr) return null;
        const index = tr.dataset.index;
        return this._currentData[index];
    }

    /**
     * 处理行操作
     * @param {string} action 操作类型
     * @param {Object} row 行数据
     * @protected
     */
    _handleAction(action, row) {
        if (!row) return;
        this._debug('Handle action:', action, row);
        this.emit(`action:${action}`, { row });
    }

    /**
     * 刷新表格数据
     * @param {Object} params 查询参数
     * @public
     */
    refresh(params = {}) {
        this._debug('Refresh table with params:', params);
        this.$table.bootstrapTable('refresh', { query: params });
    }

    /**
     * 获取选中的行数据
     * @returns {Array} 选中的行数据
     * @public
     */
    getSelections() {
        return this.$table.bootstrapTable('getSelections');
    }

    /**
     * 销毁组件
     * @public
     */
    destroy() {
        if (this.$table) {
            this.$table.bootstrapTable('destroy');
        }
        super.destroy();
    }
} 