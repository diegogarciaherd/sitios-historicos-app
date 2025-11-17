import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import "leaflet/dist/leaflet.css";
import L from 'leaflet'


const app = createApp(App)

app.use(router)

app.mount('#app')
