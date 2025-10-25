// Auto-generated at startup.
// 等待config.js加载完成后，将appConfig指向config实例
document.addEventListener('DOMContentLoaded', function() {
    if (window.config) {
        window.appConfig = window.config;
        window.controlledLog?.log('前端配置已加载(assets):', window.appConfig);
    } else {
        console.error('config.js未加载，无法初始化appConfig');
    }
});
