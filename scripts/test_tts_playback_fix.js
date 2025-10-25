/**
 * 测试TTS播放修复
 * 验证播放状态指示器不会在TTS播放完成前消失
 */

function testTtsPlaybackFix() {
    console.log('🧪 开始测试TTS播放修复...');
    
    // 检查关键组件是否存在
    const components = [
        'voice_player_enhanced',
        'enhancedPlaybackStatus',
        'voiceWebSocketManager'
    ];
    
    let allComponentsReady = true;
    components.forEach(component => {
        if (window[component]) {
            console.log(`✅ ${component} 已加载`);
        } else {
            console.log(`❌ ${component} 未找到`);
            allComponentsReady = false;
        }
    });
    
    if (!allComponentsReady) {
        console.log('❌ 部分组件未加载，无法进行测试');
        return;
    }
    
    // 检查播放状态指示器
    const statusIndicator = document.querySelector('.enhanced-playback-status');
    if (statusIndicator) {
        console.log('✅ 播放状态指示器已找到');
        console.log('指示器状态:', {
            visible: statusIndicator.style.display !== 'none',
            opacity: statusIndicator.style.opacity,
            transform: statusIndicator.style.transform
        });
    } else {
        console.log('❌ 播放状态指示器未找到');
    }
    
    // 检查音频可视化器
    const audioVisualizer = document.getElementById('audio-visualizer');
    if (audioVisualizer) {
        console.log('✅ 音频可视化器已找到');
        console.log('可视化器状态:', {
            visible: audioVisualizer.style.display !== 'none',
            width: audioVisualizer.width,
            height: audioVisualizer.height
        });
    } else {
        console.log('❌ 音频可视化器未找到');
    }
    
    // 检查状态管理器
    if (window.voiceStateManager) {
        const currentState = window.voiceStateManager.getCurrentState();
        console.log('✅ 语音状态管理器状态:', currentState);
    }
    
    // 检查播放器状态
    if (window.voice_player_enhanced) {
        const player = window.voice_player_enhanced;
        console.log('✅ 语音播放器状态:', {
            isTtsPlaying: player.isTtsPlaying,
            simplePlaying: player.simplePlaying,
            streamStates: player.streamStates ? player.streamStates.size : 0,
            simpleQueue: player.simpleQueue ? player.simpleQueue.length : 0
        });
    }
    
    console.log('🧪 TTS播放修复测试完成');
}

// 运行测试
testTtsPlaybackFix();
