/**
 * 语音通话配置文件
 */
window.VoiceConfig = {
    // VAD (Voice Activity Detection) 参数
    vad: {
        // 音量阈值 - 低于此值认为是静音
        threshold: 0.01,
        // 最大静音持续时间 (ms) - 超过此时间认为说话结束
        maxSilenceDuration: 800,
        // 静音持续时间增量 (ms)
        silenceIncrement: 50,
        // 非零样本比例阈值 - 低于此比例认为是静音
        nonZeroRatioThreshold: 0.05
    },
    
    // 音频处理参数
    audio: {
        // 音频块大小 (样本数) - 约375ms @ 24kHz
        chunkSize: 12288,
        // 音频发送间隔 (ms)
        sendInterval: 300,
        // 音频增益倍数
        gainFactor: 2.0,
        // 最小音频时长 (ms) - OpenAI要求至少100ms
        minDuration: 100
    },
    
    // 静音检测参数
    silence: {
        // 原始音量阈值 - 低于此值认为是静音
        volumeThreshold: 0.000001,
        // 非零样本数量阈值 - 低于此值认为是静音
        nonZeroSamplesThreshold: 5,
        // 非零样本比例阈值 - 低于此值认为是静音
        nonZeroRatioThreshold: 0.0001
    }
};
