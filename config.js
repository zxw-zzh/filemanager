// config.js
// 你可以通过修改localStorage.setItem('API_BASE_URL', 'http://你的ip:端口')来动态切换
window.API_BASE_URL = localStorage.getItem('API_BASE_URL') || 'http://127.0.0.1:5002'; 