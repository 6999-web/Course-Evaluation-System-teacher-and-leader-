"""
任务管理器属性测试

使用 Hypothesis 进行基于属性的测试，验证任务管理器的通用正确性属性。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings
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


class TestTaskManagerProperties:
    """任务管理器属性测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建模拟的数据库会话
        self.mock_db = Mock()
        self.task_manager = TaskManager(db=self.mock_db)
    
    # Feature: auto-scoring-system, Property 13: 任务创建后自动分发
    @given(
        teacher_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5, deadline=5000)
    def test_task_auto_distribution_property(self, teacher_count):
        """
        Property 13: For any 创建完成的考评任务，系统应该自动推送给相关教师。
        
        **Validates: Requirements 6.4**
        """
        task_id = "task_001"
        teacher_ids = [f"teacher_{i}" for i in range(teacher_count)]
        
        # 创建原始任务
        original_task = Mock(spec=EvaluationAssignmentTask)
        original_task.task_id = task_id
        original_task.template_id = "template_1"
        original_task.required_file_types = ["教案", "教学反思"]
        original_task.bonus_enabled = True
        original_task.max_bonus_score = 10
        original_task.auto_scoring_enabled = True
        original_task.deadline = datetime.utcnow() + timedelta(days=7)
        
        # 模拟数据库查询
        self.mock_db.query.return_value.filter.return_value.first.return_value = original_task
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        
        # 执行分配
        result = self.task_manager.assign_task(task_id, teacher_ids)
        
        # 验证分配成功
        assert result == True
        
        # 验证commit被调用
        self.mock_db.commit.assert_called()
    
    # Feature: auto-scoring-system, Property 14: 超时未提交触发否决
    @given(
        deadline_offset_hours=st.integers(min_value=-48, max_value=-1)
    )
    @settings(max_examples=5, deadline=5000)
    def test_check_deadline_property(self, deadline_offset_hours):
        """
        Property 14: For any 截止时间到达且教师未提交文件的情况，
        系统应该能够检查并识别超时任务。
        
        **Validates: Requirements 6.5**
        """
        # 创建超时的任务
        task = Mock(spec=EvaluationAssignmentTask)
        task.task_id = "task_001"
        task.teacher_id = "teacher_001"
        task.teacher_name = "Teacher 001"
        task.deadline = datetime.utcnow() + timedelta(hours=deadline_offset_hours)
        task.status = 'pending'
        
        # 模拟数据库查询 - 返回超时任务
        self.mock_db.query.return_value.filter.return_value.all.return_value = [task]
        
        # 执行检查
        result = self.task_manager.check_deadline()
        
        # 验证检查成功
        assert len(result) == 1
        assert result[0]['task_id'] == 'task_001'
        assert result[0]['teacher_id'] == 'teacher_001'
