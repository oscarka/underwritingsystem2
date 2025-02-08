import { App } from 'vue'
import Button from './BaseButton.vue'
import Input from './BaseInput.vue'
import Select from './BaseSelect.vue'
import Modal from './BaseModal.vue'
import Pagination from './BasePagination.vue'
import ThemeSwitch from './BaseThemeSwitch.vue'
import Tabs from './BaseTabs.vue'
import TabPane from './BaseTabPane.vue'
import Upload from './BaseUpload.vue'
import { Dialog } from './Dialog'

export {
    Button as BaseButton,
    Input as BaseInput,
    Select as BaseSelect,
    Modal as BaseModal,
    Pagination as BasePagination,
    ThemeSwitch as BaseThemeSwitch,
    Tabs as BaseTabs,
    TabPane as BaseTabPane,
    Upload as BaseUpload,
    Dialog
}

const components = {
    'BaseButton': Button,
    'BaseInput': Input,
    'BaseSelect': Select,
    'BaseModal': Modal,
    'BasePagination': Pagination,
    'BaseThemeSwitch': ThemeSwitch,
    'BaseTabs': Tabs,
    'BaseTabPane': TabPane,
    'BaseUpload': Upload
}

export default {
    install(app: App) {
        Object.entries(components).forEach(([name, component]) => {
            app.component(name, component)
        })
    }
}