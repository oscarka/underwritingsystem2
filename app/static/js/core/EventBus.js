/**
 * 事件总线系统
 * 用于组件间通信
 */
class EventBus {
    constructor() {
        this._events = {};
        this._lastEvent = null;
        this._debug = false;
    }

    /**
     * 订阅事件
     * @param {string} event 事件名称
     * @param {Function} callback 回调函数
     * @returns {Function} 取消订阅的函数
     */
    on(event, callback) {
        if (!this._events[event]) {
            this._events[event] = new Set();
        }
        this._events[event].add(callback);

        // 返回取消订阅函数
        return () => this.off(event, callback);
    }

    /**
     * 取消订阅事件
     * @param {string} event 事件名称
     * @param {Function} callback 回调函数
     */
    off(event, callback) {
        if (this._events[event]) {
            this._events[event].delete(callback);
            if (this._events[event].size === 0) {
                delete this._events[event];
            }
        }
    }

    /**
     * 发送事件
     * @param {string} event 事件名称
     * @param {*} data 事件数据
     */
    emit(event, data) {
        this._lastEvent = {
            event,
            data,
            timestamp: Date.now()
        };

        if (this._debug) {
            console.log(`[EventBus] Emit ${event}:`, data);
        }

        if (this._events[event]) {
            this._events[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`[EventBus] Error in ${event} handler:`, error);
                }
            });
        }
    }

    /**
     * 获取最后一次事件
     * @returns {Object|null} 最后一次事件信息
     */
    getLastEvent() {
        return this._lastEvent;
    }

    /**
     * 清除事件监听
     * @param {string} [event] 事件名称，如果不传则清除所有
     */
    clear(event) {
        if (event) {
            delete this._events[event];
        } else {
            this._events = {};
        }
    }

    /**
     * 获取事件监听器数量
     * @param {string} [event] 事件名称，如果不传则返回所有事件的监听器总数
     * @returns {number} 监听器数量
     */
    listenerCount(event) {
        if (event) {
            return this._events[event]?.size || 0;
        }
        return Object.values(this._events).reduce((acc, set) => acc + set.size, 0);
    }

    /**
     * 设置调试模式
     * @param {boolean} enabled 是否启用调试模式
     */
    setDebug(enabled) {
        this._debug = enabled;
    }

    /**
     * 获取所有已注册的事件
     * @returns {string[]} 事件名称列表
     */
    getRegisteredEvents() {
        return Object.keys(this._events);
    }
}

// 创建全局事件总线实例
window.eventBus = window.eventBus || new EventBus();

// 导出 EventBus 类
window.EventBus = EventBus;