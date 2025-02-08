/**
 * 权限控制组件
 */
class Permission {
    static defaultConfig = {
        debug: false,
        // 权限检查函数
        checkPermission: null,
        // 无权限时的处理方式
        onUnauthorized: null,
        // 权限缓存时间（毫秒）
        cacheDuration: 5 * 60 * 1000
    };

    constructor(config = {}) {
        this.config = {
            ...Permission.defaultConfig,
            ...config
        };

        this._permissionCache = new Map();
        this._init();
    }

    /**
     * 初始化
     * @private
     */
    _init() {
        this._bindGlobalEvents();
        this._setupMutationObserver();
    }

    /**
     * 绑定全局事件
     * @private
     */
    _bindGlobalEvents() {
        window.eventBus.on('auth:unauthorized', () => {
            this.clearCache();
        });

        window.eventBus.on('permission:check', async (event) => {
            const { permission, element } = event;
            const hasPermission = await this.check(permission);

            if (!hasPermission && element) {
                this._handleUnauthorized(element);
            }
        });
    }

    /**
     * 设置 DOM 变化观察器
     * @private
     */
    _setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) {
                            this._checkElementPermissions(node);
                        }
                    });
                } else if (mutation.type === 'attributes' && mutation.attributeName === 'data-permission') {
                    this._checkElementPermissions(mutation.target);
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['data-permission']
        });
    }

    /**
     * 检查元素权限
     * @param {Element} element 元素
     * @private
     */
    async _checkElementPermissions(element) {
        // 检查元素本身
        if (element.hasAttribute('data-permission')) {
            const permission = element.getAttribute('data-permission');
            const hasPermission = await this.check(permission);

            if (!hasPermission) {
                this._handleUnauthorized(element);
            }
        }

        // 检查子元素
        const children = element.querySelectorAll('[data-permission]');
        for (const child of children) {
            const permission = child.getAttribute('data-permission');
            const hasPermission = await this.check(permission);

            if (!hasPermission) {
                this._handleUnauthorized(child);
            }
        }
    }

    /**
     * 处理无权限元素
     * @param {Element} element 元素
     * @private
     */
    _handleUnauthorized(element) {
        if (typeof this.config.onUnauthorized === 'function') {
            this.config.onUnauthorized(element);
        } else {
            // 默认处理：禁用元素
            if (element instanceof HTMLButtonElement || element instanceof HTMLInputElement) {
                element.disabled = true;
                element.title = '没有操作权限';
            } else {
                element.style.display = 'none';
            }
        }
    }

    /**
     * 检查权限
     * @param {string} permission 权限标识
     * @returns {Promise<boolean>} 是否有权限
     */
    async check(permission) {
        if (!permission) return true;

        // 检查缓存
        const cached = this._permissionCache.get(permission);
        if (cached && Date.now() - cached.timestamp < this.config.cacheDuration) {
            return cached.result;
        }

        // 执行权限检查
        let result = false;
        if (typeof this.config.checkPermission === 'function') {
            try {
                result = await this.config.checkPermission(permission);
            } catch (error) {
                console.error('Permission check failed:', error);
                result = false;
            }
        }

        // 更新缓存
        this._permissionCache.set(permission, {
            result,
            timestamp: Date.now()
        });

        return result;
    }

    /**
     * 清除权限缓存
     * @param {string} [permission] 指定权限标识，不指定则清除所有
     */
    clearCache(permission) {
        if (permission) {
            this._permissionCache.delete(permission);
        } else {
            this._permissionCache.clear();
        }
    }

    /**
     * 输出调试信息
     * @param {string} message 消息
     * @param {...*} args 参数
     * @private
     */
    _debug(message, ...args) {
        if (this.config.debug) {
            console.log('[Permission]', message, ...args);
        }
    }
}

// 创建全局实例
window.permission = new Permission(); 