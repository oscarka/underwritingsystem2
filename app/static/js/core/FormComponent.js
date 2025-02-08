/**
 * 表单组件基类
 * 继承自BaseComponent，提供表单相关的通用功能
 */
class FormComponent extends BaseComponent {
    static defaultConfig = {
        ...BaseComponent.defaultConfig,
        validateOnSubmit: true,
        validateOnChange: false,
        validateOnBlur: true,
        resetOnSubmit: false,
        submitOnEnter: true
    };

    constructor(element, config = {}) {
        super(element, config);
        this.form = this.element.tagName === 'FORM' ? this.element : this.element.querySelector('form');

        if (!this.form) {
            throw new Error('Form element not found');
        }
    }

    /**
     * 初始化表单组件
     * @protected
     */
    _init() {
        super._init();
        this._initValidation();
        this._initFormEvents();
    }

    /**
     * 初始化表单验证
     * @protected
     */
    _initValidation() {
        // 添加自定义验证规则
        this.form.querySelectorAll('[data-validate]').forEach(input => {
            const rules = input.dataset.validate.split(',');
            rules.forEach(rule => {
                const [name, param] = rule.split(':');
                this._addValidationRule(input, name, param);
            });
        });
    }

    /**
     * 初始化表单事件
     * @protected
     */
    _initFormEvents() {
        // 提交事件
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this._handleSubmit(e);
        });

        // 回车提交
        if (this.config.submitOnEnter) {
            this.form.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    const target = e.target;
                    if (target.tagName !== 'TEXTAREA') {
                        e.preventDefault();
                        this._handleSubmit(e);
                    }
                }
            });
        }

        // 字段变化验证
        if (this.config.validateOnChange) {
            this.form.addEventListener('change', (e) => {
                this._validateField(e.target);
            });
        }

        // 失去焦点验证
        if (this.config.validateOnBlur) {
            this.form.addEventListener('blur', (e) => {
                this._validateField(e.target);
            }, true);
        }
    }

    /**
     * 处理表单提交
     * @param {Event} e 事件对象
     * @protected
     */
    _handleSubmit(e) {
        if (this.config.validateOnSubmit && !this.validate()) {
            return;
        }

        const formData = this.getFormData();
        this.emit('form:submit', {
            type: 'submit',
            data: formData
        });

        if (this.config.resetOnSubmit) {
            this.reset();
        }
    }

    /**
     * 验证表单
     * @returns {boolean} 验证结果
     */
    validate() {
        let isValid = true;
        const fields = this.form.elements;

        for (let i = 0; i < fields.length; i++) {
            const field = fields[i];
            if (field.tagName !== 'BUTTON' && !this._validateField(field)) {
                isValid = false;
            }
        }

        return isValid;
    }

    /**
     * 验证单个字段
     * @param {HTMLElement} field 字段元素
     * @returns {boolean} 验证结果
     * @protected
     */
    _validateField(field) {
        if (!field.checkValidity()) {
            field.classList.add('is-invalid');
            return false;
        }

        field.classList.remove('is-invalid');
        return true;
    }

    /**
     * 添加验证规则
     * @param {HTMLElement} input 输入元素
     * @param {string} rule 规则名称
     * @param {string} param 规则参数
     * @protected
     */
    _addValidationRule(input, rule, param) {
        switch (rule) {
            case 'required':
                input.required = true;
                break;
            case 'pattern':
                input.pattern = param;
                break;
            case 'minlength':
                input.minLength = param;
                break;
            case 'maxlength':
                input.maxLength = param;
                break;
            // 可以添加更多验证规则
        }
    }

    /**
     * 获取表单数据
     * @returns {Object} 表单数据对象
     */
    getFormData() {
        const formData = new FormData(this.form);
        return Object.fromEntries(formData.entries());
    }

    /**
     * 设置表单数据
     * @param {Object} data 数据对象
     */
    setFormData(data) {
        Object.entries(data).forEach(([name, value]) => {
            const field = this.form.elements[name];
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = Boolean(value);
                } else if (field.type === 'radio') {
                    const radio = this.form.querySelector(`input[name="${name}"][value="${value}"]`);
                    if (radio) {
                        radio.checked = true;
                    }
                } else {
                    field.value = value;
                }
            }
        });
    }

    /**
     * 重置表单
     */
    reset() {
        this.form.reset();
        this.form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
    }

    /**
     * 禁用表单
     */
    disable() {
        this.form.querySelectorAll('input, select, textarea, button').forEach(element => {
            element.disabled = true;
        });
    }

    /**
     * 启用表单
     */
    enable() {
        this.form.querySelectorAll('input, select, textarea, button').forEach(element => {
            element.disabled = false;
        });
    }

    /**
     * 序列化表单数据
     * @returns {string} 序列化后的字符串
     */
    serialize() {
        const formData = new FormData(this.form);
        return new URLSearchParams(formData).toString();
    }

    /**
     * 反序列化数据到表单
     * @param {string} data 序列化的表单数据
     */
    deserialize(data) {
        const params = new URLSearchParams(data);
        this.setFormData(Object.fromEntries(params.entries()));
    }
} 