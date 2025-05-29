import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia' // <<< ADD THIS IMPORT
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia()) // <<< ADD THIS LINE to install Pinia
app.use(router)

app.mount('#app')
