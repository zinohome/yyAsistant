"""
Real-time Voice Chat Component

This module provides the UI components for real-time voice dialogue,
including control panels, status indicators, conversation history,
and audio visualization.
"""

import dash
from dash import html, dcc
import feffery_antd_components as fac
from typing import List, Dict, Any


class RealtimeVoiceChatComponent:
    """Real-time Voice Chat UI Component"""
    
    def __init__(self):
        """Initialize the component"""
        self.component_id = "realtime-voice-chat"
    
    def render(self) -> html.Div:
        """
        Render the real-time voice chat component
        
        Returns:
            html.Div: Complete real-time voice chat interface
        """
        return html.Div([
            # Real-time dialogue control panel
            self._create_control_panel(),
            
            # Conversation history
            self._create_conversation_history(),
            
            # Audio visualization
            self._create_audio_visualizer(),
            
            # State storage components
            *self._create_state_stores()
        ], id=self.component_id, style={"margin": "20px 0", "border": "2px solid #ff4d4f", "padding": "20px", "backgroundColor": "#fff2f0"})
    
    def _create_control_panel(self) -> fac.AntdCard:
        """Create the control panel with start/stop/mute buttons"""
        return fac.AntdCard([
            # 调试信息
            html.Div("🔴 实时语音对话组件已加载", style={"color": "red", "fontSize": "18px", "fontWeight": "bold", "textAlign": "center", "marginBottom": "10px"}),
            fac.AntdRow([
                # Start button
                fac.AntdCol([
                    fac.AntdButton(
                        id="realtime-start-btn",
                        type="primary",
                        icon=fac.AntdIcon(icon="microphone"),
                        children="开始实时对话",
                        size="large",
                        style={
                            "width": "100%", 
                            "height": "60px",
                            "fontSize": "16px",
                            "fontWeight": "bold"
                        }
                    )
                ], span=8),
                
                # Stop button
                fac.AntdCol([
                    fac.AntdButton(
                        id="realtime-stop-btn",
                        type="default",
                        icon=fac.AntdIcon(icon="stop"),
                        children="停止对话",
                        size="large",
                        disabled=True,
                        style={
                            "width": "100%", 
                            "height": "60px",
                            "fontSize": "16px",
                            "fontWeight": "bold"
                        }
                    )
                ], span=8),
                
                # Mute button
                fac.AntdCol([
                    fac.AntdButton(
                        id="realtime-mute-btn",
                        type="default",
                        icon=fac.AntdIcon(icon="sound"),
                        children="静音",
                        size="large",
                        style={
                            "width": "100%", 
                            "height": "60px",
                            "fontSize": "16px",
                            "fontWeight": "bold"
                        }
                    )
                ], span=8)
            ], gutter=16),
            
            # Real-time status indicator
            html.Div([
                fac.AntdBadge(
                    dot=True,
                    color="gray",
                    children=html.Span("等待开始对话")
                ),
                html.Span(
                    " 实时语音对话模式", 
                    style={
                        "marginLeft": "10px", 
                        "fontSize": "16px",
                        "fontWeight": "500"
                    }
                )
            ], id="realtime-status", style={
                "marginTop": "15px", 
                "textAlign": "center",
                "padding": "10px",
                "backgroundColor": "#f5f5f5",
                "borderRadius": "6px"
            })
            
        ], title="实时语音对话", style={"marginBottom": "20px"})
    
    def _create_conversation_history(self) -> html.Div:
        """Create the conversation history display"""
        return html.Div([
            html.H4("对话历史", style={"marginBottom": "10px", "fontWeight": "600"}),
            html.Div(
                id="realtime-chat-history",
                style={
                    "height": "300px",
                    "overflowY": "auto",
                    "border": "1px solid #d9d9d9",
                    "borderRadius": "6px",
                    "padding": "15px",
                    "backgroundColor": "#fafafa"
                },
                children=[
                    html.Div(
                        "暂无对话记录",
                        style={
                            "textAlign": "center",
                            "color": "#999",
                            "fontSize": "14px",
                            "marginTop": "100px"
                        }
                    )
                ]
            )
        ], style={"marginBottom": "20px"})
    
    def _create_audio_visualizer(self) -> html.Div:
        """Create the audio visualization component"""
        return html.Div([
            html.H4("音频可视化", style={"marginBottom": "10px", "fontWeight": "600"}),
            html.Canvas(
                id="audio-visualizer",
                width=800,
                height=200,
                style={
                    "border": "1px solid #d9d9d9",
                    "borderRadius": "6px",
                    "marginTop": "10px",
                    "backgroundColor": "#000",
                    "display": "block",
                    "margin": "0 auto"
                }
            ),
            # Audio controls
            html.Div([
                fac.AntdRow([
                    fac.AntdCol([
                        html.Label("音量:", style={"fontWeight": "500"}),
                        fac.AntdSlider(
                            id="audio-volume-slider",
                            min=0,
                            max=100,
                            defaultValue=80,
                            style={"marginTop": "5px"}
                        )
                    ], span=12),
                    fac.AntdCol([
                        html.Label("语速:", style={"fontWeight": "500"}),
                        fac.AntdSlider(
                            id="audio-rate-slider",
                            min=0.5,
                            max=2.0,
                            step=0.1,
                            defaultValue=1.0,
                            style={"marginTop": "5px"}
                        )
                    ], span=12)
                ], gutter=16)
            ], style={"marginTop": "15px", "padding": "15px", "backgroundColor": "#f9f9f9", "borderRadius": "6px"})
        ])
    
    def _create_state_stores(self) -> List[dcc.Store]:
        """Create the state storage components"""
        return [
            # Conversation history store
            dcc.Store(
                id="realtime-conversation-store",
                data=[]
            ),
            
            # Audio data store
            dcc.Store(
                id="realtime-audio-store",
                data=None
            ),
            
            # Status store
            dcc.Store(
                id="realtime-status-store",
                data={"status": "idle", "timestamp": 0}
            ),
            
            # Settings store
            dcc.Store(
                id="realtime-settings-store",
                data={
                    "volume": 80,
                    "rate": 1.0,
                    "voice": "alloy",
                    "muted": False
                }
            ),
            
            # Realtime voice trigger store
            dcc.Store(
                id="realtime-voice-trigger",
                data=None
            ),
            
            # Statistics store
            dcc.Store(
                id="realtime-stats-store",
                data={
                    "total_messages": 0,
                    "total_duration": 0,
                    "average_response_time": 0
                }
            )
        ]


def create_realtime_voice_chat_component() -> html.Div:
    """
    Factory function to create the real-time voice chat component
    
    Returns:
        html.Div: Complete real-time voice chat interface
    """
    component = RealtimeVoiceChatComponent()
    return component.render()


# Component configuration
REALTIME_VOICE_CHAT_CONFIG = {
    "component_id": "realtime-voice-chat",
    "button_styles": {
        "primary": {
            "backgroundColor": "#1890ff",
            "borderColor": "#1890ff",
            "color": "#fff"
        },
        "default": {
            "backgroundColor": "#fff",
            "borderColor": "#d9d9d9",
            "color": "#000"
        },
        "disabled": {
            "backgroundColor": "#f5f5f5",
            "borderColor": "#d9d9d9",
            "color": "#bfbfbf"
        }
    },
    "status_colors": {
        "idle": "gray",
        "listening": "red",
        "processing": "orange",
        "speaking": "green",
        "error": "red"
    },
    "audio_settings": {
        "default_volume": 80,
        "default_rate": 1.0,
        "default_voice": "alloy",
        "visualizer_fps": 60
    }
}
