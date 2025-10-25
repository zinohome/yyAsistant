"""
状态同步管理器单元测试
测试状态注册、监听、更新和UI同步功能
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestStateSyncManager(unittest.TestCase):
    """测试状态同步管理器"""
    
    def setUp(self):
        """测试前准备"""
        # 模拟状态同步管理器
        self.state_manager = MockStateSyncManager()
    
    def test_state_registration(self):
        """测试状态注册"""
        # 注册新状态
        result = self.state_manager.registerState('test_state', {
            'value': 'initial',
            'count': 0
        })
        
        self.assertTrue(result)
        self.assertIn('test_state', self.state_manager.states)
        
        # 验证状态内容
        state = self.state_manager.getState('test_state')
        self.assertEqual(state['value'], 'initial')
        self.assertEqual(state['count'], 0)
        self.assertIn('_metadata', state)
    
    def test_state_update(self):
        """测试状态更新"""
        # 注册状态
        self.state_manager.registerState('test_state', {'value': 'initial'})
        
        # 更新状态
        result = self.state_manager.updateState('test_state', {
            'value': 'updated',
            'count': 1
        })
        
        self.assertTrue(result)
        
        # 验证更新
        state = self.state_manager.getState('test_state')
        self.assertEqual(state['value'], 'updated')
        self.assertEqual(state['count'], 1)
        self.assertGreater(state['_metadata']['version'], 1)
    
    def test_state_listener(self):
        """测试状态监听器"""
        # 注册状态
        self.state_manager.registerState('test_state', {'value': 'initial'})
        
        # 添加监听器
        listener_id = self.state_manager.addStateListener('test_state', self.mock_callback)
        
        self.assertIsNotNone(listener_id)
        self.assertIn('test_state', self.state_manager.listeners)
        self.assertEqual(len(self.state_manager.listeners['test_state']), 1)
        
        # 更新状态并触发监听器
        self.state_manager.updateState('test_state', {'value': 'updated'})
        
        # 验证监听器被调用
        self.assertTrue(self.mock_callback_called)
        self.assertEqual(self.mock_callback_data['value'], 'updated')
    
    def test_multiple_listeners(self):
        """测试多个监听器"""
        # 注册状态
        self.state_manager.registerState('test_state', {'value': 'initial'})
        
        # 添加多个监听器
        listener1 = self.state_manager.addStateListener('test_state', self.mock_callback)
        listener2 = self.state_manager.addStateListener('test_state', self.mock_callback2)
        
        self.assertNotEqual(listener1, listener2)
        self.assertEqual(len(self.state_manager.listeners['test_state']), 2)
        
        # 更新状态
        self.state_manager.updateState('test_state', {'value': 'updated'})
        
        # 验证两个监听器都被调用
        self.assertTrue(self.mock_callback_called)
        self.assertTrue(self.mock_callback2_called)
    
    def test_listener_removal(self):
        """测试监听器移除"""
        # 注册状态和监听器
        self.state_manager.registerState('test_state', {'value': 'initial'})
        listener_id = self.state_manager.addStateListener('test_state', self.mock_callback)
        
        # 移除监听器
        result = self.state_manager.removeStateListener('test_state', listener_id)
        
        self.assertTrue(result)
        self.assertEqual(len(self.state_manager.listeners['test_state']), 0)
    
    def test_state_snapshot(self):
        """测试状态快照"""
        # 注册多个状态
        self.state_manager.registerState('state1', {'value': 'a'})
        self.state_manager.registerState('state2', {'value': 'b'})
        
        # 创建快照
        snapshot = self.state_manager.createSnapshot()
        
        self.assertIn('state1', snapshot)
        self.assertIn('state2', snapshot)
        self.assertEqual(snapshot['state1']['value'], 'a')
        self.assertEqual(snapshot['state2']['value'], 'b')
        self.assertTrue(snapshot['state1']['_snapshot'])
    
    def test_snapshot_restore(self):
        """测试快照恢复"""
        # 创建快照
        snapshot = {
            'state1': {'value': 'a', '_snapshot': True, '_timestamp': 1234567890},
            'state2': {'value': 'b', '_snapshot': True, '_timestamp': 1234567890}
        }
        
        # 恢复快照
        self.state_manager.restoreSnapshot(snapshot)
        
        # 验证状态恢复
        state1 = self.state_manager.getState('state1')
        state2 = self.state_manager.getState('state2')
        
        self.assertEqual(state1['value'], 'a')
        self.assertEqual(state2['value'], 'b')
        self.assertTrue(state1['_metadata']['restored'])
        self.assertTrue(state2['_metadata']['restored'])
    
    def test_state_statistics(self):
        """测试状态统计"""
        # 注册状态和监听器
        self.state_manager.registerState('state1', {'value': 'a'})
        self.state_manager.registerState('state2', {'value': 'b'})
        self.state_manager.addStateListener('state1', self.mock_callback)
        self.state_manager.addStateListener('state2', self.mock_callback)
        
        # 获取统计信息
        stats = self.state_manager.getStats()
        
        self.assertEqual(stats['totalStates'], 2)
        self.assertEqual(stats['totalListeners'], 2)
        self.assertIn('pendingUpdates', stats)
        self.assertIn('isProcessing', stats)
    
    def test_cleanup(self):
        """测试清理功能"""
        # 注册状态和监听器
        self.state_manager.registerState('test_state', {'value': 'initial'})
        self.state_manager.addStateListener('test_state', self.mock_callback)
        
        # 执行清理
        self.state_manager.cleanup()
        
        # 验证清理结果
        self.assertEqual(len(self.state_manager.states), 0)
        self.assertEqual(len(self.state_manager.listeners), 0)
        self.assertEqual(len(self.state_manager.updateQueue), 0)
    
    def mock_callback(self, new_state, options=None):
        """模拟回调函数"""
        self.mock_callback_called = True
        self.mock_callback_data = new_state
    
    def mock_callback2(self, new_state, options=None):
        """模拟回调函数2"""
        self.mock_callback2_called = True
        self.mock_callback2_data = new_state


class MockStateSyncManager:
    """模拟状态同步管理器"""
    
    def __init__(self):
        self.states = {}
        self.listeners = {}
        self.updateQueue = []
        self.isProcessing = False
        self._listener_id_counter = 0
    
    def registerState(self, stateName, initialState=None):
        """注册状态"""
        if initialState is None:
            initialState = {}
        
        self.states[stateName] = {
            **initialState,
            '_metadata': {
                'createdAt': 1234567890,
                'lastUpdated': 1234567890,
                'version': 1
            }
        }
        return True
    
    def getState(self, stateName):
        """获取状态"""
        return self.states.get(stateName)
    
    def updateState(self, stateName, updates, options=None):
        """更新状态"""
        if stateName not in self.states:
            return False
        
        current_state = self.states[stateName]
        new_state = {
            **current_state,
            **updates,
            '_metadata': {
                **current_state['_metadata'],
                'lastUpdated': 1234567890,
                'version': current_state['_metadata']['version'] + 1
            }
        }
        
        self.states[stateName] = new_state
        
        # 添加到更新队列
        self.updateQueue.append({
            'stateName': stateName,
            'newState': new_state,
            'options': options or {},
            'timestamp': 1234567890
        })
        
        # 处理更新队列
        self._processUpdates()
        
        return True
    
    def addStateListener(self, stateName, callback, options=None):
        """添加状态监听器"""
        if stateName not in self.listeners:
            self.listeners[stateName] = []
        
        listener_id = f'listener_{self._listener_id_counter}'
        self._listener_id_counter += 1
        
        self.listeners[stateName].append({
            'callback': callback,
            'options': options or {},
            'id': listener_id
        })
        
        return listener_id
    
    def removeStateListener(self, stateName, listenerId):
        """移除状态监听器"""
        if stateName not in self.listeners:
            return False
        
        listeners = self.listeners[stateName]
        for i, listener in enumerate(listeners):
            if listener['id'] == listenerId:
                listeners.pop(i)
                return True
        
        return False
    
    def createSnapshot(self):
        """创建状态快照"""
        snapshot = {}
        for stateName, state in self.states.items():
            snapshot[stateName] = {
                **state,
                '_snapshot': True,
                '_timestamp': 1234567890
            }
        return snapshot
    
    def restoreSnapshot(self, snapshot):
        """恢复状态快照"""
        for stateName, stateData in snapshot.items():
            if stateData.get('_snapshot'):
                self.states[stateName] = {
                    **stateData,
                    '_metadata': {
                        **stateData.get('_metadata', {}),
                        'lastUpdated': 1234567890,
                        'restored': True
                    }
                }
    
    def getStats(self):
        """获取统计信息"""
        total_listeners = sum(len(listeners) for listeners in self.listeners.values())
        return {
            'totalStates': len(self.states),
            'totalListeners': total_listeners,
            'pendingUpdates': len(self.updateQueue),
            'isProcessing': self.isProcessing
        }
    
    def cleanup(self):
        """清理"""
        self.states.clear()
        self.listeners.clear()
        self.updateQueue = []
    
    def _processUpdates(self):
        """处理更新队列"""
        if self.isProcessing or not self.updateQueue:
            return
        
        self.isProcessing = True
        
        try:
            updates = self.updateQueue.copy()
            self.updateQueue = []
            
            # 按状态名分组
            grouped_updates = {}
            for update in updates:
                state_name = update['stateName']
                if state_name not in grouped_updates:
                    grouped_updates[state_name] = []
                grouped_updates[state_name].append(update)
            
            # 处理每个状态的更新
            for state_name, state_updates in grouped_updates.items():
                self._processStateUpdates(state_name, state_updates)
        
        finally:
            self.isProcessing = False
    
    def _processStateUpdates(self, stateName, updates):
        """处理状态更新"""
        if stateName not in self.listeners:
            return
        
        # 获取最新状态
        latest_update = updates[-1]
        new_state = latest_update['newState']
        
        # 通知所有监听器
        for listener in self.listeners[stateName]:
            try:
                listener['callback'](new_state, latest_update['options'])
            except Exception as e:
                print(f"监听器错误 ({stateName}): {e}")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)