import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'boxicons/css/boxicons.min.css'
import 'vue-toastification/dist/index.css'
import './assets/styles/main.scss'
import './assets/styles/theme.css'
import './assets/styles/theme-sneat.css'

import Toast, { type PluginOptions, POSITION } from 'vue-toastification'

const app = createApp(App)

const options: PluginOptions = {
    position: POSITION.TOP_RIGHT,
    timeout: 3200,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false,
    newestOnTop: true,
    transition: {
        enter: 'Vue-Toastification__fade-enter-active',
        leave: 'Vue-Toastification__fade-leave-active',
        move: 'Vue-Toastification__fade-move'
    }
}

app.use(createPinia())
app.use(router)
app.use(Toast, options)

router.isReady().then(() => {
    app.mount('#app')
})

