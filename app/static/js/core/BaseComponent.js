/**
 * 基础组件类
 * 所有组件的父类，提供通用功能
 */
class BaseComponent {
    /**
     * @param {HTMLElement} element 组件根元素
     * @param {Object} config 组件配置
     */
    constructor(element, config = {}) {
        if (!element) {
            throw new Error('Component element is required');
        }

        this.element = element;
        this.config = this._mergeConfig(config);
        this._eventHandlers = new Map();
        this._mounted = false;
        this._destroyed = false;

        // 自动初始化
        if (this.config.autoInit) {
            this.init();
        }
    }

    /**
     * 合并默认配置和用户配置
     * @param {Object} config 用户配置
     * @returns {Object} 最终配置
     * @protected
     */
    _mergeConfig(config) {
        return {
            autoInit: true,
            debug: false,
            ...this.constructor.defaultConfig,
            ...config
        };
    }

    /**
     * 初始化组件
     * @returns {void}
     */
    init() {
        if (this._mounted) {
            console.warn('Component already initialized');
            return;
        }

        try {
            this._beforeInit();
            this._init();
            this._afterInit();
            this._mounted = true;
        } catch (error) {
            console.error('Failed to initialize component:', error);
            throw error;
        }
    }

    /**
     * 初始化前钩子
     * @protected
     */
    _beforeInit() {
        this._debug('beforeInit');
    }

    /**
     * 实际的初始化逻辑
     * @protected
     */
    _init() {
        this._debug('init');
        this._bindEvents();
    }

    /**
     * 初始化后钩子
     * @protected
     */
    _afterInit() {
        this._debug('afterInit');
    }

    /**
     * 绑定事件
     * @protected
     */
    _bindEvents() {
        this._debug('bindEvents');
    }

    /**
     * 解绑事件
     * @protected
     */
    _unbindEvents() {
        this._eventHandlers.forEach((handler, event) => {
            this.off(event, handler);
        });
        this._eventHandlers.clear();
    }

    /**
     * 绑定DOM事件
     * @param {string} event 事件名称
     * @param {string} selector 选择器
     * @param {Function} handler 事件处理函数
     */
    on(event, selector, handler) {
        const wrappedHandler = (e) => {
            const target = e.target.closest(selector);
            if (target) {
                handler.call(this, e, target);
            }
        };

        this.element.addEventListener(event, wrappedHandler);
        this._eventHandlers.set(event, wrappedHandler);
    }

    /**
     * 解绑DOM事件
     * @param {string} event 事件名称
     * @param {Function} handler 事件处理函数
     */
    off(event, handler) {
        this.element.removeEventListener(event, handler);
        this._eventHandlers.delete(event);
    }

    /**
     * 触发自定义事件
     * @param {string} name 事件名称
     * @param {*} detail 事件数据
     */
    emit(name, detail) {
        const event = new CustomEvent(name, {
            bubbles: true,
            cancelable: true,
            detail
        });
        this.element.dispatchEvent(event);
    }

    /**
     * 销毁组件
     */
    destroy() {
        if (this._destroyed) {
            return;
        }

        this._debug('destroy');
        this._unbindEvents();
        this._destroyed = true;
        this._mounted = false;
    }

    /**
     * 输出调试信息
     * @param {string} message 调试信息
     * @param {...*} args 其他参数
     * @protected
     */
    _debug(message, ...args) {
        if (this.config.debug) {
            console.log(
                `[${this.constructor.name}]`,
                message,
                ...args
            );
        }
    }

    /**
     * 获取组件数据属性
     * @param {string} name 属性名
     * @returns {string|null}
     */
    getData(name) {
        return this.element.dataset[name] || null;
    }

    /**
     * 设置组件数据属性
     * @param {string} name 属性名
     * @param {string} value 属性值
     */
    setData(name, value) {
        this.element.dataset[name] = value;
    }

    /**
     * 移除组件数据属性
     * @param {string} name 属性名
     */
    removeData(name) {
        delete this.element.dataset[name];
    }

    /**
     * 判断组件是否已挂载
     * @returns {boolean}
     */
    isMounted() {
        return this._mounted;
    }

    /**
     * 判断组件是否已销毁
     * @returns {boolean}
     */
    isDestroyed() {
        return this._destroyed;
    }
}

// 默认配置
BaseComponent.defaultConfig = {
    autoInit: true,
    debug: false
}; 