/**
 * CRUD协调器
 * 用于协调表单、表格等组件的交互
 */
class CrudCoordinator {
    static defaultConfig = {
        debug: false,
        autoInit: true,
        components: {
            table: null,
            form: null,
            search: null
        },
        endpoints: {
            list: '',
            create: '',
            update: '',
            delete: '',
            view: '',
            batchDelete: '',
            import: '',
            export: ''
        },
        messages: {
            createSuccess: '创建成功',
            updateSuccess: '更新成功',
            deleteSuccess: '删除成功',
            createError: '创建失败',
            updateError: '更新失败',
            deleteError: '删除失败',
            loadError: '加载数据失败',
            deleteConfirm: '确定要删除吗？',
            saveSuccess: '保存成功',
            saveError: '保存失败',
            validationError: '请检查输入是否正确',
            networkError: '网络连接错误',
            unauthorized: '没有操作权限',
            sessionExpired: '会话已过期，请重新登录',
            batchDeleteSuccess: '批量删除成功',
            batchDeleteError: '批量删除失败',
            exportSuccess: '导出成功',
            exportError: '导出失败',
            importSuccess: '导入成功',
            importError: '导入失败'
        }
    };

    /**
     * @param {Object} config 配置项
     */
    constructor(config = {}) {
        this.config = this._mergeConfig(config);
        this.state = {
            mode: 'list', // list, create, edit, view
            currentItem: null,
            loading: false
        };

        if (this.config.autoInit) {
            this.init();
        }
    }

    /**
     * 合并配置
     * @param {Object} config 用户配置
     * @returns {Object} 最终配置
     * @private
     */
    _mergeConfig(config) {
        return {
            ...CrudCoordinator.defaultConfig,
            ...config,
            endpoints: {
                ...CrudCoordinator.defaultConfig.endpoints,
                ...config.endpoints
            },
            messages: {
                ...CrudCoordinator.defaultConfig.messages,
                ...config.messages
            }
        };
    }

    /**
     * 初始化
     */
    init() {
        this._debug('Initializing CRUD coordinator');
        this._bindEvents();
    }

    /**
     * 绑定事件
     * @private
     */
    _bindEvents() {
        // 表格事件
        window.eventBus.on('table:action', (event) => {
            this._handleTableAction(event);
        });

        // 表单事件
        window.eventBus.on('form:submit', (event) => {
            this._handleFormSubmit(event);
        });

        // 搜索事件
        window.eventBus.on('search:submitted', (event) => {
            this._handleSearch(event);
        });

        window.eventBus.on('search:reset', () => {
            this._handleSearchReset();
        });

        // 批量删除事件
        window.eventBus.on('table:batchDelete', (event) => {
            const { ids } = event;
            this.batchDelete(ids);
        });

        // 导入事件
        window.eventBus.on('import:start', (event) => {
            const { file } = event;
            this.importData(file);
        });

        // 导出事件
        window.eventBus.on('export:start', (event) => {
            const { params } = event;
            this.exportData(params);
        });
    }

    /**
     * 处理表格动作
     * @param {Object} event 事件对象
     * @private
     */
    async _handleTableAction(event) {
        const { type, data } = event;
        switch (type) {
            case 'view':
                await this.view(data.id);
                break;
            case 'edit':
                await this.edit(data.id);
                break;
            case 'delete':
                await this.delete(data.id);
                break;
        }
    }

    /**
     * 处理表单提交
     * @param {Object} event 事件对象
     * @private
     */
    async _handleFormSubmit(event) {
        const { data } = event;

        // 表单验证
        if (!this._validateForm(data)) {
            return;
        }

        try {
            if (this.state.mode === 'create') {
                await this.create(data);
            } else if (this.state.mode === 'edit') {
                await this.update(this.state.currentItem.id, data);
            }
            this._showSuccess(this.config.messages.saveSuccess);
        } catch (error) {
            this._showError(this.config.messages.saveError);
            throw error;
        }
    }

    /**
     * 处理搜索
     * @param {Object} event 事件对象
     * @private
     */
    _handleSearch(event) {
        const { data } = event;
        this.refresh(data);
    }

    /**
     * 处理搜索重置
     * @private
     */
    _handleSearchReset() {
        this.refresh({});
    }

    /**
     * 创建
     * @param {Object} data 数据
     */
    async create(data) {
        try {
            this._setState({ loading: true });
            const response = await this._request(this.config.endpoints.create, {
                method: 'POST',
                data
            });

            this._showSuccess(this.config.messages.createSuccess);
            this.refresh();
            this._closeForm();
            return response;
        } catch (error) {
            this._showError(this.config.messages.createError);
            throw error;
        } finally {
            this._setState({ loading: false });
        }
    }

    /**
     * 更新
     * @param {number|string} id ID
     * @param {Object} data 数据
     */
    async update(id, data) {
        try {
            this._setState({ loading: true });
            const response = await this._request(this._getUrl(this.config.endpoints.update, { id }), {
                method: 'PUT',
                data
            });

            this._showSuccess(this.config.messages.updateSuccess);
            this.refresh();
            this._closeForm();
            return response;
        } catch (error) {
            this._showError(this.config.messages.updateError);
            throw error;
        } finally {
            this._setState({ loading: false });
        }
    }

    /**
     * 删除
     * @param {number|string} id ID
     */
    async delete(id) {
        if (!confirm(this.config.messages.deleteConfirm)) {
            return;
        }

        try {
            this._setState({ loading: true });
            await this._request(this._getUrl(this.config.endpoints.delete, { id }), {
                method: 'DELETE'
            });

            this._showSuccess(this.config.messages.deleteSuccess);
            this.refresh();
        } catch (error) {
            this._showError(this.config.messages.deleteError);
            throw error;
        } finally {
            this._setState({ loading: false });
        }
    }

    /**
     * 查看
     * @param {number|string} id ID
     */
    async view(id) {
        try {
            this._setState({ loading: true, mode: 'view' });
            const data = await this._request(this._getUrl(this.config.endpoints.view, { id }));
            this._setState({ currentItem: data });
            this._openForm('view', data);
            return data;
        } catch (error) {
            this._showError(this.config.messages.loadError);
            throw error;
        } finally {
            this._setState({ loading: false });
        }
    }

    /**
     * 编辑
     * @param {number|string} id ID
     */
    async edit(id) {
        try {
            this._setState({ loading: true, mode: 'edit' });
            const data = await this._request(this._getUrl(this.config.endpoints.view, { id }));
            this._setState({ currentItem: data });
            this._openForm('edit', data);
            return data;
        } catch (error) {
            this._showError(this.config.messages.loadError);
            throw error;
        } finally {
            this._setState({ loading: false });
        }
    }

    /**
     * 刷新
     * @param {Object} params 查询参数
     */
    refresh(params = {}) {
        window.eventBus.emit('table:refresh', { params });
    }

    /**
     * 打开表单
     * @param {string} mode 模式
     * @param {Object} data 数据
     * @private
     */
    _openForm(mode, data = null) {
        this._setState({ mode });
        window.eventBus.emit('modal:open', { mode, data });
    }

    /**
     * 关闭表单
     * @private
     */
    _closeForm() {
        this._setState({ mode: 'list', currentItem: null });
        window.eventBus.emit('modal:close');
    }

    /**
     * 发送请求
     * @param {string} url 请求地址
     * @param {Object} options 请求选项
     * @returns {Promise} Promise对象
     * @private
     */
    async _request(url, options = {}) {
        // 检查网络状态
        if (!navigator.onLine) {
            this._showError(this.config.messages.networkError);
            throw new Error('Network offline');
        }

        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        const requestOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        if (requestOptions.data) {
            requestOptions.body = JSON.stringify(requestOptions.data);
            delete requestOptions.data;
        }

        try {
            const response = await fetch(url, requestOptions);

            // 处理HTTP错误
            if (response.status === 401) {
                this._showError(this.config.messages.unauthorized);
                window.eventBus.emit('auth:unauthorized');
                throw new Error('Unauthorized');
            }

            if (response.status === 403) {
                this._showError(this.config.messages.unauthorized);
                throw new Error('Forbidden');
            }

            if (response.status === 404) {
                this._showError('请求的资源不存在');
                throw new Error('Not Found');
            }

            if (response.status === 500) {
                this._showError('服务器内部错误');
                throw new Error('Internal Server Error');
            }

            if (!response.ok) {
                // 尝试解析错误信息
                let errorMessage;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.message || errorData.error || response.statusText;
                } catch {
                    errorMessage = response.statusText;
                }

                this._showError(errorMessage);
                throw new Error(errorMessage);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            // 处理网络错误
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                this._showError(this.config.messages.networkError);
                throw new Error('Network Error');
            }

            throw error;
        }
    }

    /**
     * 获取URL
     * @param {string} url URL模板
     * @param {Object} params 参数
     * @returns {string} 最终URL
     * @private
     */
    _getUrl(url, params = {}) {
        let finalUrl = url;
        Object.entries(params).forEach(([key, value]) => {
            finalUrl = finalUrl.replace(`{${key}}`, value);
        });
        return finalUrl;
    }

    /**
     * 更新状态
     * @param {Object} newState 新状态
     * @private
     */
    _setState(newState) {
        this.state = {
            ...this.state,
            ...newState
        };
        this._debug('State updated:', this.state);
    }

    /**
     * 显示成功提示
     * @param {string} message 消息
     * @param {Object} options 选项
     * @private
     */
    _showSuccess(message, options = {}) {
        window.eventBus.emit('toast:success', { message, ...options });
    }

    /**
     * 显示错误提示
     * @param {string} message 消息
     * @param {Object} options 选项
     * @private
     */
    _showError(message, options = {}) {
        window.eventBus.emit('toast:error', { message, ...options });
    }

    /**
     * 显示警告提示
     * @param {string} message 消息
     * @param {Object} options 选项
     * @private
     */
    _showWarning(message, options = {}) {
        window.eventBus.emit('toast:warning', { message, ...options });
    }

    /**
     * 显示信息提示
     * @param {string} message 消息
     * @param {Object} options 选项
     * @private
     */
    _showInfo(message, options = {}) {
        window.eventBus.emit('toast:info', { message, ...options });
    }

    /**
     * 输出调试信息
     * @param {string} message 消息
     * @param {...*} args 参数
     * @private
     */
    _debug(message, ...args) {
        if (this.config.debug) {
            console.log('[CrudCoordinator]', message, ...args);
        }
    }

    /**
     * 处理表单验证
     * @param {Object} data 表单数据
     * @returns {boolean} 是否验证通过
     * @private
     */
    _validateForm(data) {
        // 基本验证
        if (!data) {
            this._showError(this.config.messages.validationError);
            return false;
        }

        // 必填字段验证
        const requiredFields = this.config.form?.requiredFields || [];
        for (const field of requiredFields) {
            if (!data[field.name]) {
                this._showError(`${field.label || field.name}不能为空`);
                return false;
            }
        }

        // 自定义验证
        if (typeof this.config.form?.validate === 'function') {
            try {
                const result = this.config.form.validate(data);
                if (result !== true) {
                    this._showError(result || this.config.messages.validationError);
                    return false;
                }
            } catch (error) {
                this._showError(error.message || this.config.messages.validationError);
                return false;
            }
        }

        return true;
    }

    /**
     * 批量删除
     * @param {Array} ids ID列表
     */
    async batchDelete(ids) {
        if (!ids || ids.length === 0) {
            this._showWarning('请选择要删除的项目');
            return;
        }

        if (!confirm(this.config.messages.deleteConfirm)) {
            return;
        }

        try {
            this._setState({ loading: true });
            await this._request(this.config.endpoints.batchDelete, {
                method: 'POST',
                data: { ids }
            });

            this._showSuccess(this.config.messages.batchDeleteSuccess);
            this.refresh();
        } catch (error) {
            this._showError(this.config.messages.batchDeleteError);
            throw error;
        } finally {
            this._setState({ loading: false });
        }
    }

    /**
     * 导出数据
     * @param {Object} params 导出参数
     */
    async exportData(params = {}) {
        try {
            this._setState({ loading: true });

            // 构建查询参数
            const queryParams = new URLSearchParams(params).toString();
            const url = `${this.config.endpoints.export}${queryParams ? '?' + queryParams : ''}`;

            // 发送请求
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/octet-stream'
                }
            });

            if (!response.ok) {
                throw new Error(response.statusText);
            }

            // 获取文件名
            const filename = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'export.xlsx';

            // 下载文件
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(downloadUrl);

            this._showSuccess(this.config.messages.exportSuccess);
        } catch (error) {
            this._showError(this.config.messages.exportError);
            throw error;
        } finally {
            this._setState({ loading: false });
        }
    }

    /**
     * 导入数据
     * @param {File} file 文件对象
     */
    async importData(file) {
        if (!file) {
            this._showWarning('请选择要导入的文件');
            return;
        }

        try {
            this._setState({ loading: true });

            // 创建 FormData
            const formData = new FormData();
            formData.append('file', file);

            // 发送请求
            const response = await fetch(this.config.endpoints.import, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(response.statusText);
            }

            const result = await response.json();

            // 显示导入结果
            if (result.success) {
                this._showSuccess(this.config.messages.importSuccess);
                // 如果有详细信息，显示为信息提示
                if (result.details) {
                    this._showInfo(result.details);
                }
            } else {
                throw new Error(result.message || '导入失败');
            }

            // 刷新表格
            this.refresh();
        } catch (error) {
            this._showError(error.message || this.config.messages.importError);
            throw error;
        } finally {
            this._setState({ loading: false });
        }
    }
}