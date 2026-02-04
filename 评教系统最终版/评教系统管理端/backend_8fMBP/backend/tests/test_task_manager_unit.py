"""
任务管理器单元测试

测试任务管理器的具体业务场景、边界值和错误处理。
重点测试任务创建、配置和截止时间检查。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from typing import Dict, List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.task_manager import TaskManager
from app.models import (
    EvaluationAssignmentTask,
    MaterialSubmission,
    ScoringRecord,
    ScoringLog
)


class TestTaskManagerUnit:
    """任务管理器单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建模拟的数据库会话
        self.mock_db = Mock()
        self.task_manager = TaskManager(db=self.mock_db)
    
    # 测试任务创建和配置（Requirements 6.1, 6.2, 6.3）
    
    def test_create_task_success(self):
        """测试成功创建任务"""
        task_data = {
            'template_id': 'template_1',
            'teacher_id': 'teacher_001',
            'teacher_name': '张三',
            'required_file_types': ['教案', '教学反思'],
            'bonus_enabled': True,
            'max_bonus_score': 10,
            'auto_scoring_enabled': True,
            'deadline': datetime.utcnow() + timedelta(days=7)
        }
        
        # 模拟数据库操作
        mock_task = Mock(spec=EvaluationAssignmentTask)
        mock_task.task_id = 'task_001'
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        # 执行创建
        with patch('app.services.task_manager.EvaluationAssignmentTask') as mock_task_class:
            mock_task_class.return_value = mock_task
            result = self.task_manager.create_task(task_data)
        
        # 验证结果
        assert result == 'task_001'
        # 验证add被调用至少一次（用于创建任务和日志）
        assert self.mock_db.add.call_count >= 1
        # 验证commit被调用
        self.mock_db.commit.assert_called()
        self.mock_db.refresh.assert_called_once_with(mock_task)
    
    def test_create_task_missing_required_field(self):
        """测试创建任务时缺少必需字段"""
        task_data = {
            'template_id': 'template_1',
            'teacher_id': 'teacher_001',
            # 缺少 teacher_name
            'deadline': datetime.utcnow() + timedelta(days=7)
        }
        
        # 执行创建，应该抛出异常
        with pytest.raises(ValueError, match="缺少必需字段"):
            self.task_manager.create_task(task_data)
    
    def test_create_task_with_default_values(self):
        """测试创建任务时使用默认值"""
        task_data = {
            'template_id': 'template_1',
            'teacher_id': 'teacher_001',
            'teacher_name': '张三',
            'deadline': datetime.utcnow() + timedelta(days=7)
            # 不提供可选字段，应该使用默认值
        }
        
        # 模拟数据库操作
        mock_task = Mock(spec=EvaluationAssignmentTask)
        mock_task.task_id = 'task_001'
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        # 执行创建
        with patch('app.services.task_manager.EvaluationAssignmentTask') as mock_task_class:
            mock_task_class.return_value = mock_task
            result = self.task_manager.create_task(task_data)
        
        # 验证结果
        assert result == 'task_001'
        
        # 验证默认值被使用
        call_args = mock_task_class.call_args
        assert call_args[1]['bonus_enabled'] == True
        assert call_args[1]['max_bonus_score'] == 10
        assert call_args[1]['auto_scoring_enabled'] == True
    
    def test_update_task_config_success(self):
        """测试成功更新任务配置"""
        task_id = 'task_001'
        config_data = {
            'required_file_types': ['教案', '教学反思', '课件'],
            'max_bonus_score': 15,
            'bonus_enabled': False
        }
        
        # 模拟现有任务
        mock_task = Mock(spec=EvaluationAssignmentTask)
        mock_task.task_id = task_id
        mock_task.required_file_types = ['教案']
        mock_task.max_bonus_score = 10
        mock_task.bonus_enabled = True
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        self.mock_db.commit = Mock()
        
        # 执行更新
        result = self.task_manager.update_task_config(task_id, config_data)
        
        # 验证结果
        assert result == True
        assert mock_task.required_file_types == ['教案', '教学反思', '课件']
        assert mock_task.max_bonus_score == 15
        assert mock_task.bonus_enabled == False
        # 验证commit被调用至少一次（用于更新任务和日志）
        assert self.mock_db.commit.call_count >= 1
    
    def test_update_task_config_task_not_found(self):
        """测试更新不存在的任务配置"""
        task_id = 'nonexistent_task'
        config_data = {'max_bonus_score': 15}
        
        # 模拟任务不存在
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # 执行更新
        result = self.task_manager.update_task_config(task_id, config_data)
        
        # 验证结果
        assert result == False
    
    def test_update_task_config_partial_update(self):
        """测试部分更新任务配置"""
        task_id = 'task_001'
        config_data = {
            'max_bonus_score': 20  # 只更新这一个字段
        }
        
        # 模拟现有任务
        mock_task = Mock(spec=EvaluationAssignmentTask)
        mock_task.task_id = task_id
        mock_task.required_file_types = ['教案', '教学反思']
        mock_task.max_bonus_score = 10
        mock_task.bonus_enabled = True
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        self.mock_db.commit = Mock()
        
        # 执行更新
        result = self.task_manager.update_task_config(task_id, config_data)
        
        # 验证结果
        assert result == True
        assert mock_task.max_bonus_score == 20
        # 其他字段应该保持不变
        assert mock_task.required_file_types == ['教案', '教学反思']
        assert mock_task.bonus_enabled == True
    
    # 测试截止时间检查（Requirements 6.3, 6.5）
    
    def test_check_deadline_no_overdue_tasks(self):
        """测试检查截止时间 - 没有超时任务"""
        # 模拟没有超时任务
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # 执行检查
        result = self.task_manager.check_deadline()
        
        # 验证结果
        assert result == []
    
    def test_check_deadline_with_overdue_tasks(self):
        """测试检查截止时间 - 有超时任务"""
        # 创建超时任务
        overdue_task1 = Mock(spec=EvaluationAssignmentTask)
        overdue_task1.task_id = 'task_001'
        overdue_task1.teacher_id = 'teacher_001'
        overdue_task1.teacher_name = '张三'
        overdue_task1.deadline = datetime.utcnow() - timedelta(hours=24)
        overdue_task1.status = 'pending'
        
        overdue_task2 = Mock(spec=EvaluationAssignmentTask)
        overdue_task2.task_id = 'task_002'
        overdue_task2.teacher_id = 'teacher_002'
        overdue_task2.teacher_name = '李四'
        overdue_task2.deadline = datetime.utcnow() - timedelta(hours=48)
        overdue_task2.status = 'pending'
        
        # 模拟数据库查询
        self.mock_db.query.return_value.filter.return_value.all.return_value = [
            overdue_task1, overdue_task2
        ]
        
        # 执行检查
        result = self.task_manager.check_deadline()
        
        # 验证结果
        assert len(result) == 2
        assert result[0]['task_id'] == 'task_001'
        assert result[0]['teacher_id'] == 'teacher_001'
        assert result[1]['task_id'] == 'task_002'
        assert result[1]['teacher_id'] == 'teacher_002'
    
    def test_check_deadline_only_pending_tasks(self):
        """测试检查截止时间 - 只检查待处理任务"""
        # 创建已完成的任务（不应该被检查）
        completed_task = Mock(spec=EvaluationAssignmentTask)
        completed_task.task_id = 'task_001'
        completed_task.deadline = datetime.utcnow() - timedelta(hours=24)
        completed_task.status = 'scored'  # 已评分
        
        # 模拟数据库查询 - 只返回待处理的超时任务
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # 执行检查
        result = self.task_manager.check_deadline()
        
        # 验证结果 - 已完成的任务不应该被返回
        assert result == []
    
    def test_trigger_veto_for_overdue_success(self):
        """测试成功触发超时否决"""
        task_ids = ['task_001', 'task_002']
        
        # 创建超时任务
        task1 = Mock(spec=EvaluationAssignmentTask)
        task1.task_id = 'task_001'
        task1.teacher_id = 'teacher_001'
        task1.teacher_name = '张三'
        task1.status = 'pending'
        task1.total_score = None
        task1.scored_at = None
        
        task2 = Mock(spec=EvaluationAssignmentTask)
        task2.task_id = 'task_002'
        task2.teacher_id = 'teacher_002'
        task2.teacher_name = '李四'
        task2.status = 'pending'
        task2.total_score = None
        task2.scored_at = None
        
        # 模拟数据库查询
        def query_side_effect(*args, **kwargs):
            mock_query = Mock()
            
            def filter_side_effect(*args, **kwargs):
                mock_filter = Mock()
                
                def first_side_effect():
                    # 根据查询条件返回对应的任务
                    if 'task_001' in str(args):
                        return task1
                    elif 'task_002' in str(args):
                        return task2
                    return None
                
                mock_filter.first = first_side_effect
                return mock_filter
            
            mock_query.filter = filter_side_effect
            return mock_query
        
        self.mock_db.query.side_effect = query_side_effect
        self.mock_db.add = Mock()
        self.mock_db.flush = Mock()
        self.mock_db.commit = Mock()
        
        # 执行否决触发
        result = self.task_manager.trigger_veto_for_overdue(task_ids)
        
        # 验证结果
        assert result == True
        self.mock_db.commit.assert_called_once()
    
    def test_trigger_veto_for_overdue_task_not_found(self):
        """测试触发否决时任务不存在"""
        task_ids = ['nonexistent_task']
        
        # 模拟任务不存在
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        
        # 执行否决触发
        result = self.task_manager.trigger_veto_for_overdue(task_ids)
        
        # 验证结果 - 应该继续处理其他任务
        assert result == True
        self.mock_db.commit.assert_called_once()
    
    def test_get_task_success(self):
        """测试成功获取任务详情"""
        task_id = 'task_001'
        
        # 创建模拟任务
        mock_task = Mock(spec=EvaluationAssignmentTask)
        mock_task.task_id = task_id
        mock_task.template_id = 'template_1'
        mock_task.teacher_id = 'teacher_001'
        mock_task.teacher_name = '张三'
        mock_task.status = 'pending'
        mock_task.required_file_types = ['教案', '教学反思']
        mock_task.bonus_enabled = True
        mock_task.max_bonus_score = 10
        mock_task.auto_scoring_enabled = True
        mock_task.deadline = datetime.utcnow() + timedelta(days=7)
        mock_task.submitted_at = None
        mock_task.scored_at = None
        mock_task.created_at = datetime.utcnow()
        mock_task.updated_at = datetime.utcnow()
        
        # 模拟数据库查询
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_task
        
        # 执行获取
        result = self.task_manager.get_task(task_id)
        
        # 验证结果
        assert result is not None
        assert result['task_id'] == task_id
        assert result['teacher_id'] == 'teacher_001'
        assert result['required_file_types'] == ['教案', '教学反思']
        assert result['bonus_enabled'] == True
    
    def test_get_task_not_found(self):
        """测试获取不存在的任务"""
        task_id = 'nonexistent_task'
        
        # 模拟任务不存在
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # 执行获取
        result = self.task_manager.get_task(task_id)
        
        # 验证结果
        assert result is None
    
    def test_get_tasks_by_teacher(self):
        """测试获取教师的所有任务"""
        teacher_id = 'teacher_001'
        
        # 创建模拟任务
        task1 = Mock(spec=EvaluationAssignmentTask)
        task1.task_id = 'task_001'
        task1.template_id = 'template_1'
        task1.status = 'pending'
        task1.required_file_types = ['教案']
        task1.deadline = datetime.utcnow() + timedelta(days=7)
        task1.submitted_at = None
        task1.scored_at = None
        
        task2 = Mock(spec=EvaluationAssignmentTask)
        task2.task_id = 'task_002'
        task2.template_id = 'template_2'
        task2.status = 'scored'
        task2.required_file_types = ['教学反思']
        task2.deadline = datetime.utcnow() + timedelta(days=14)
        task2.submitted_at = datetime.utcnow()
        task2.scored_at = datetime.utcnow()
        
        # 模拟数据库查询
        self.mock_db.query.return_value.filter.return_value.all.return_value = [task1, task2]
        
        # 执行获取
        result = self.task_manager.get_tasks_by_teacher(teacher_id)
        
        # 验证结果
        assert len(result) == 2
        assert result[0]['task_id'] == 'task_001'
        assert result[0]['status'] == 'pending'
        assert result[1]['task_id'] == 'task_002'
        assert result[1]['status'] == 'scored'
    
    def test_get_pending_tasks(self):
        """测试获取所有待处理任务"""
        # 创建模拟任务
        task1 = Mock(spec=EvaluationAssignmentTask)
        task1.task_id = 'task_001'
        task1.teacher_id = 'teacher_001'
        task1.teacher_name = '张三'
        task1.deadline = datetime.utcnow() + timedelta(days=7)
        task1.required_file_types = ['教案']
        
        task2 = Mock(spec=EvaluationAssignmentTask)
        task2.task_id = 'task_002'
        task2.teacher_id = 'teacher_002'
        task2.teacher_name = '李四'
        task2.deadline = datetime.utcnow() + timedelta(days=14)
        task2.required_file_types = ['教学反思']
        
        # 模拟数据库查询
        self.mock_db.query.return_value.filter.return_value.all.return_value = [task1, task2]
        
        # 执行获取
        result = self.task_manager.get_pending_tasks()
        
        # 验证结果
        assert len(result) == 2
        assert result[0]['task_id'] == 'task_001'
        assert result[0]['teacher_id'] == 'teacher_001'
        assert result[1]['task_id'] == 'task_002'
        assert result[1]['teacher_id'] == 'teacher_002'
