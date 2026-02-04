"""
试运行管理器属性测试

使用Hypothesis进行属性测试，验证试运行模式的通用正确性属性
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import (
    Base, ScoringRecord, ReviewRecord, SystemScoringConfig,
    MaterialSubmission, User
)
from app.services.trial_run_manager import TrialRunManager


@pytest.fixture(scope="function")
def fresh_db_session():
    """为每个测试创建一个新的数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture(scope="function")
def fresh_trial_run_manager(fresh_db_session):
    """为每个测试创建一个新的试运行管理器实例"""
    return TrialRunManager(fresh_db_session)


def create_test_scoring_record(db_session, record_id=1):
    """创建测试评分记录"""
    # 创建测试用户
    user = User(
        id=1,
        username="test_admin",
        email="admin@example.com",
        hashed_password="hashed",
        full_name="Test Admin",
        role="admin"
    )
    db_session.add(user)
    
    # 创建测试提交记录
    submission = MaterialSubmission(
        submission_id=f"sub_{record_id:03d}",
        teacher_id=f"teacher_{record_id:03d}",
        teacher_name=f"Test Teacher {record_id}",
        files=[{"file_id": f"file_{record_id:03d}", "file_name": "test.docx"}],
        notes="Test submission"
    )
    db_session.add(submission)
    
    # 创建测试评分记录
    scoring_record = ScoringRecord(
        id=record_id,
        submission_id=f"sub_{record_id:03d}",
        file_id=f"file_{record_id:03d}",
        file_type="lesson_plan",
        file_name="test.docx",
        base_score=85.0,
        bonus_score=5.0,
        final_score=90.0,
        grade="优秀",
        score_details="{}",
        veto_triggered=False,
        veto_reason="",
        scoring_type="auto",
        scored_by=None,
        scored_at=datetime.utcnow()
    )
    db_session.add(scoring_record)
    db_session.commit()
    
    return scoring_record


class TestTrialRunModeToggleProperties:
    """试运行模式开关属性测试"""
    
    @given(admin_id=st.integers(min_value=1, max_value=1000))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_enable_trial_mode_idempotent(self, fresh_db_session, fresh_trial_run_manager, admin_id):
        """
        Property: 启用试运行模式应该是幂等的
        
        For any 管理员ID，多次启用试运行模式应该产生相同的结果
        
        **Validates: Requirements 14.1**
        """
        # 第一次启用
        result1 = fresh_trial_run_manager.enable_trial_mode(admin_id=admin_id)
        assert result1 is True
        
        # 第二次启用
        result2 = fresh_trial_run_manager.enable_trial_mode(admin_id=admin_id)
        assert result2 is True
        
        # 验证状态一致
        assert fresh_trial_run_manager.is_trial_mode_enabled() is True
    
    @given(admin_id=st.integers(min_value=1, max_value=1000))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_disable_trial_mode_idempotent(self, fresh_db_session, fresh_trial_run_manager, admin_id):
        """
        Property: 禁用试运行模式应该是幂等的
        
        For any 管理员ID，多次禁用试运行模式应该产生相同的结果
        
        **Validates: Requirements 14.1**
        """
        # 先启用
        fresh_trial_run_manager.enable_trial_mode(admin_id=admin_id)
        
        # 第一次禁用
        result1 = fresh_trial_run_manager.disable_trial_mode(admin_id=admin_id)
        assert result1 is True
        
        # 第二次禁用
        result2 = fresh_trial_run_manager.disable_trial_mode(admin_id=admin_id)
        assert result2 is True
        
        # 验证状态一致
        assert fresh_trial_run_manager.is_trial_mode_enabled() is False
    
    @given(admin_id=st.integers(min_value=1, max_value=1000))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_trial_mode_toggle_consistency(self, fresh_db_session, fresh_trial_run_manager, admin_id):
        """
        Property: 试运行模式的启用和禁用应该是互补的
        
        For any 管理员ID，启用后禁用应该回到初始状态
        
        **Validates: Requirements 14.1**
        """
        # 初始状态
        initial_state = fresh_trial_run_manager.is_trial_mode_enabled()
        
        # 启用
        fresh_trial_run_manager.enable_trial_mode(admin_id=admin_id)
        assert fresh_trial_run_manager.is_trial_mode_enabled() is True
        
        # 禁用
        fresh_trial_run_manager.disable_trial_mode(admin_id=admin_id)
        assert fresh_trial_run_manager.is_trial_mode_enabled() is False


class TestTrialRunDifferenceRecordingProperties:
    """试运行差异记录属性测试"""
    
    @given(
        auto_score=st.floats(min_value=0, max_value=100),
        preset_score=st.floats(min_value=0, max_value=100)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_difference_consistency_threshold(self, fresh_db_session, fresh_trial_run_manager, 
                                             auto_score, preset_score):
        """
        Property: 差异小于0.1分的记录应该被标记为一致
        
        For any 自动评分和预设标准，如果差异小于0.1分，应该标记为一致
        
        **Validates: Requirements 14.2**
        """
        # 创建测试数据
        create_test_scoring_record(fresh_db_session, record_id=1)
        
        # 启用试运行模式
        fresh_trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        fresh_trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=auto_score,
            preset_score=preset_score
        )
        
        # 验证一致性标记
        review_record = fresh_db_session.query(ReviewRecord).filter(
            ReviewRecord.scoring_record_id == 1
        ).first()
        
        difference = abs(auto_score - preset_score)
        if difference < 0.1:
            assert review_record.is_consistent is True
        else:
            assert review_record.is_consistent is False
    
    @given(
        auto_score=st.floats(min_value=0, max_value=100),
        preset_score=st.floats(min_value=0, max_value=100)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_difference_calculation_accuracy(self, fresh_db_session, fresh_trial_run_manager,
                                            auto_score, preset_score):
        """
        Property: 记录的差异应该准确反映自动评分和预设标准的差异
        
        For any 自动评分和预设标准，记录的差异应该等于两者的绝对值差
        
        **Validates: Requirements 14.2**
        """
        # 创建测试数据
        create_test_scoring_record(fresh_db_session, record_id=1)
        
        # 启用试运行模式
        fresh_trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        fresh_trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=auto_score,
            preset_score=preset_score
        )
        
        # 验证差异计算
        review_record = fresh_db_session.query(ReviewRecord).filter(
            ReviewRecord.scoring_record_id == 1
        ).first()
        
        expected_difference = abs(auto_score - preset_score)
        actual_difference = abs(review_record.original_score - review_record.reviewed_score)
        
        assert abs(actual_difference - expected_difference) < 0.01


class TestTrialRunReportGenerationProperties:
    """试运行报告生成属性测试"""
    
    @given(num_records=st.integers(min_value=1, max_value=50))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_report_consistency_rate_calculation(self, fresh_db_session, fresh_trial_run_manager, num_records):
        """
        Property: 报告中的一致性比例应该准确反映一致记录的比例
        
        For any 记录数量，报告中的一致性比例应该等于一致记录数/总记录数
        
        **Validates: Requirements 14.3, 14.4**
        """
        # 创建测试数据
        create_test_scoring_record(fresh_db_session, record_id=1)
        
        # 启用试运行模式
        fresh_trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录一致的差异
        consistent_count = num_records // 2
        for i in range(consistent_count):
            fresh_trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=85.0
            )
        
        # 记录不一致的差异
        for i in range(num_records - consistent_count):
            fresh_trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=90.0
            )
        
        # 生成报告
        result = fresh_trial_run_manager.generate_trial_run_diff_report()
        
        # 验证一致性比例
        expected_rate = consistent_count / num_records
        assert abs(result["consistency_rate"] - expected_rate) < 0.01
    
    @given(num_records=st.integers(min_value=1, max_value=50))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_report_total_records_count(self, fresh_db_session, fresh_trial_run_manager, num_records):
        """
        Property: 报告中的总记录数应该等于记录的差异数量
        
        For any 记录数量，报告中的总记录数应该准确反映
        
        **Validates: Requirements 14.3**
        """
        # 创建测试数据
        create_test_scoring_record(fresh_db_session, record_id=1)
        
        # 启用试运行模式
        fresh_trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        for i in range(num_records):
            fresh_trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0 + i,
                preset_score=88.0 + i
            )
        
        # 生成报告
        result = fresh_trial_run_manager.generate_trial_run_diff_report()
        
        # 验证总记录数
        assert result["total_records"] == num_records
    
    def test_report_file_creation(self, fresh_db_session, fresh_trial_run_manager):
        """
        Property: 生成的报告应该创建一个有效的文件
        
        For any 报告生成请求，应该创建一个可读的Markdown文件
        
        **Validates: Requirements 14.2**
        """
        # 创建测试数据
        create_test_scoring_record(fresh_db_session, record_id=1)
        
        # 启用试运行模式
        fresh_trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        fresh_trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=85.0,
            preset_score=88.0
        )
        
        # 生成报告
        result = fresh_trial_run_manager.generate_trial_run_diff_report()
        
        # 验证文件存在且可读
        if result["report_path"]:
            report_path = Path(result["report_path"])
            assert report_path.exists()
            assert report_path.is_file()
            
            # 验证文件内容可读
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0
                assert "试运行差异报告" in content


class TestConsistencyReportGenerationProperties:
    """一致性报告生成属性测试"""
    
    @given(num_records=st.integers(min_value=1, max_value=50))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_consistency_report_total_reviews_count(self, fresh_db_session, fresh_trial_run_manager, num_records):
        """
        Property: 一致性报告中的总复核数应该等于记录的复核数量
        
        For any 复核数量，报告中的总复核数应该准确反映
        
        **Validates: Requirements 14.4**
        """
        # 创建测试数据
        create_test_scoring_record(fresh_db_session, record_id=1)
        
        # 启用试运行模式
        fresh_trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        for i in range(num_records):
            fresh_trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=85.0
            )
        
        # 生成报告
        result = fresh_trial_run_manager.generate_consistency_report()
        
        # 验证总复核数
        assert result["total_reviews"] == num_records
    
    @given(num_records=st.integers(min_value=1, max_value=50))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_consistency_report_consistency_rate_calculation(self, fresh_db_session, fresh_trial_run_manager, num_records):
        """
        Property: 一致性报告中的一致性比例应该准确反映一致复核的比例
        
        For any 复核数量，报告中的一致性比例应该等于一致复核数/总复核数
        
        **Validates: Requirements 14.4**
        """
        # 创建测试数据
        create_test_scoring_record(fresh_db_session, record_id=1)
        
        # 启用试运行模式
        fresh_trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录一致的复核
        consistent_count = num_records // 2
        for i in range(consistent_count):
            fresh_trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=85.0
            )
        
        # 记录不一致的复核
        for i in range(num_records - consistent_count):
            fresh_trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=90.0
            )
        
        # 生成报告
        result = fresh_trial_run_manager.generate_consistency_report()
        
        # 验证一致性比例
        expected_rate = consistent_count / num_records
        assert abs(result["consistency_rate"] - expected_rate) < 0.01
    
    def test_consistency_report_file_creation(self, fresh_db_session, fresh_trial_run_manager):
        """
        Property: 生成的一致性报告应该创建一个有效的文件
        
        For any 报告生成请求，应该创建一个可读的Markdown文件
        
        **Validates: Requirements 14.5**
        """
        # 创建测试数据
        create_test_scoring_record(fresh_db_session, record_id=1)
        
        # 启用试运行模式
        fresh_trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        fresh_trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=85.0,
            preset_score=88.0
        )
        
        # 生成报告
        result = fresh_trial_run_manager.generate_consistency_report()
        
        # 验证文件存在且可读
        if result["report_path"]:
            report_path = Path(result["report_path"])
            assert report_path.exists()
            assert report_path.is_file()
            
            # 验证文件内容可读
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0
                assert "一致性报告" in content
