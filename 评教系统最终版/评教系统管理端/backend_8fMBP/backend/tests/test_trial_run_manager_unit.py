"""
试运行管理器单元测试

测试试运行模式的配置和差异记录功能
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import (
    Base, ScoringRecord, ReviewRecord, SystemScoringConfig,
    MaterialSubmission, ScoringLog, User
)
from app.services.trial_run_manager import (
    TrialRunManager, TrialRunManagerError
)


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    # 使用内存数据库
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def trial_run_manager(db_session):
    """创建试运行管理器实例"""
    return TrialRunManager(db_session)


def create_test_data(db_session):
    """创建测试数据"""
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
        submission_id="sub_001",
        teacher_id="teacher_001",
        teacher_name="Test Teacher",
        files=[{"file_id": "file_001", "file_name": "test.docx"}],
        notes="Test submission"
    )
    db_session.add(submission)
    
    # 创建测试评分记录
    scoring_record = ScoringRecord(
        id=1,
        submission_id="sub_001",
        file_id="file_001",
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
    return user, submission, scoring_record


class TestTrialRunModeToggle:
    """试运行模式开关测试"""
    
    def test_enable_trial_mode(self, db_session, trial_run_manager):
        """测试启用试运行模式"""
        result = trial_run_manager.enable_trial_mode(admin_id=1)
        assert result is True
        
        # 验证配置已保存
        config = db_session.query(SystemScoringConfig).filter(
            SystemScoringConfig.config_key == "trial_mode_enabled"
        ).first()
        assert config is not None
        assert config.config_value == "true"
        assert config.is_trial_mode is True
    
    def test_disable_trial_mode(self, db_session, trial_run_manager):
        """测试禁用试运行模式"""
        # 先启用
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 再禁用
        result = trial_run_manager.disable_trial_mode(admin_id=1)
        assert result is True
        
        # 验证配置已更新
        config = db_session.query(SystemScoringConfig).filter(
            SystemScoringConfig.config_key == "trial_mode_enabled"
        ).first()
        assert config is not None
        assert config.config_value == "false"
        assert config.is_trial_mode is False
    
    def test_is_trial_mode_enabled_when_enabled(self, db_session, trial_run_manager):
        """测试检查试运行模式是否启用（已启用）"""
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        result = trial_run_manager.is_trial_mode_enabled()
        assert result is True
    
    def test_is_trial_mode_enabled_when_disabled(self, db_session, trial_run_manager):
        """测试检查试运行模式是否启用（已禁用）"""
        trial_run_manager.disable_trial_mode(admin_id=1)
        
        result = trial_run_manager.is_trial_mode_enabled()
        assert result is False
    
    def test_is_trial_mode_enabled_default(self, db_session, trial_run_manager):
        """测试检查试运行模式是否启用（默认）"""
        # 没有配置时应该返回False
        result = trial_run_manager.is_trial_mode_enabled()
        assert result is False


class TestTrialRunDifferenceRecording:
    """试运行差异记录测试"""
    
    def test_record_trial_run_difference_when_enabled(self, db_session, trial_run_manager):
        """测试在试运行模式启用时记录差异"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        result = trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=85.0,
            preset_score=88.0,
            difference_reason="评分标准理解偏差"
        )
        assert result is True
        
        # 验证复核记录已创建
        review_record = db_session.query(ReviewRecord).filter(
            ReviewRecord.scoring_record_id == 1
        ).first()
        assert review_record is not None
        assert review_record.review_type == "trial_run"
        assert review_record.original_score == 85.0
        assert review_record.reviewed_score == 88.0
        assert review_record.is_consistent is False
    
    def test_record_trial_run_difference_when_disabled(self, db_session, trial_run_manager):
        """测试在试运行模式禁用时记录差异"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 禁用试运行模式
        trial_run_manager.disable_trial_mode(admin_id=1)
        
        # 尝试记录差异
        result = trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=85.0,
            preset_score=88.0
        )
        assert result is False
    
    def test_record_trial_run_difference_consistent(self, db_session, trial_run_manager):
        """测试记录一致的差异"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异（差异小于0.1）
        result = trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=85.0,
            preset_score=85.05
        )
        assert result is True
        
        # 验证复核记录
        review_record = db_session.query(ReviewRecord).filter(
            ReviewRecord.scoring_record_id == 1
        ).first()
        assert review_record.is_consistent is True
    
    def test_record_trial_run_difference_nonexistent_record(self, db_session, trial_run_manager):
        """测试记录不存在的评分记录的差异"""
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 尝试记录不存在的评分记录
        with pytest.raises(TrialRunManagerError):
            trial_run_manager.record_trial_run_difference(
                scoring_record_id=999,
                auto_score=85.0,
                preset_score=88.0
            )


class TestTrialRunReportGeneration:
    """试运行报告生成测试"""
    
    def test_generate_trial_run_diff_report_empty(self, db_session, trial_run_manager):
        """测试生成空的试运行差异报告"""
        result = trial_run_manager.generate_trial_run_diff_report()
        
        assert result["total_records"] == 0
        assert result["consistency_rate"] == 0.0
        assert result["report_path"] is None
    
    def test_generate_trial_run_diff_report_with_data(self, db_session, trial_run_manager):
        """测试生成有数据的试运行差异报告"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录多个差异
        for i in range(5):
            trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0 + i,
                preset_score=88.0 + i,
                difference_reason="测试差异"
            )
        
        # 生成报告
        result = trial_run_manager.generate_trial_run_diff_report()
        
        assert result["total_records"] == 5
        assert result["consistency_rate"] == 0.0
        assert result["report_path"] is not None
        
        # 验证报告文件存在
        report_path = Path(result["report_path"])
        assert report_path.exists()
        
        # 验证报告内容
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "试运行差异报告" in content
            assert "总记录数: 5" in content
    
    def test_generate_trial_run_diff_report_with_date_range(self, db_session, trial_run_manager):
        """测试生成指定日期范围的试运行差异报告"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=85.0,
            preset_score=88.0
        )
        
        # 生成报告（指定日期范围）
        today = datetime.utcnow().strftime("%Y-%m-%d")
        result = trial_run_manager.generate_trial_run_diff_report(
            start_date=today,
            end_date=today
        )
        
        assert result["total_records"] == 1


class TestConsistencyReportGeneration:
    """一致性报告生成测试"""
    
    def test_generate_consistency_report_empty(self, db_session, trial_run_manager):
        """测试生成空的一致性报告"""
        result = trial_run_manager.generate_consistency_report()
        
        assert result["total_reviews"] == 0
        assert result["consistency_rate"] == 0.0
        assert result["report_path"] is None
    
    def test_generate_consistency_report_with_data(self, db_session, trial_run_manager):
        """测试生成有数据的一致性报告"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录多个差异
        for i in range(10):
            trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0 + i,
                preset_score=85.0 + i,  # 一致
                difference_reason="一致"
            )
        
        # 生成报告
        result = trial_run_manager.generate_consistency_report()
        
        assert result["total_reviews"] == 10
        assert result["consistency_rate"] == 1.0  # 100%一致
        assert result["report_path"] is not None
        
        # 验证报告文件存在
        report_path = Path(result["report_path"])
        assert report_path.exists()
        
        # 验证报告内容
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "一致性报告" in content
            assert "总复核数: 10" in content
    
    def test_generate_consistency_report_mixed_results(self, db_session, trial_run_manager):
        """测试生成混合结果的一致性报告"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录一致的差异
        for i in range(8):
            trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=85.0,
                difference_reason="一致"
            )
        
        # 记录不一致的差异
        for i in range(2):
            trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=90.0,
                difference_reason="评分标准理解偏差"
            )
        
        # 生成报告
        result = trial_run_manager.generate_consistency_report()
        
        assert result["total_reviews"] == 10
        assert result["consistent_count"] == 8
        assert result["inconsistent_count"] == 2
        assert result["consistency_rate"] == 0.8  # 80%一致


class TestReportContent:
    """报告内容测试"""
    
    def test_trial_run_diff_report_content_structure(self, db_session, trial_run_manager):
        """测试试运行差异报告的内容结构"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=85.0,
            preset_score=88.0,
            difference_reason="评分标准理解偏差"
        )
        
        # 生成报告
        result = trial_run_manager.generate_trial_run_diff_report()
        
        # 验证报告内容
        report_path = Path(result["report_path"])
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查必要的部分
            assert "# 试运行差异报告" in content
            assert "## 概览" in content
            assert "## 分数差异统计" in content
            assert "## 差异原因分析" in content
            assert "## 详细差异列表" in content
            assert "一致性比例" in content
    
    def test_consistency_report_content_structure(self, db_session, trial_run_manager):
        """测试一致性报告的内容结构"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录差异
        trial_run_manager.record_trial_run_difference(
            scoring_record_id=1,
            auto_score=85.0,
            preset_score=88.0
        )
        
        # 生成报告
        result = trial_run_manager.generate_consistency_report()
        
        # 验证报告内容
        report_path = Path(result["report_path"])
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查必要的部分
            assert "# 一致性报告" in content
            assert "## 总体统计" in content
            assert "## 建议" in content
            assert "一致性比例" in content


class TestReportRecommendations:
    """报告建议测试"""
    
    def test_consistency_report_recommendation_high_consistency(self, db_session, trial_run_manager):
        """测试高一致性的报告建议"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录高一致性的差异
        for i in range(100):
            trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=85.0,
                difference_reason="一致"
            )
        
        # 生成报告
        result = trial_run_manager.generate_consistency_report()
        
        # 验证报告建议
        report_path = Path(result["report_path"])
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "可考虑切换到正式运行模式" in content
    
    def test_consistency_report_recommendation_low_consistency(self, db_session, trial_run_manager):
        """测试低一致性的报告建议"""
        # 创建测试数据
        user, submission, scoring_record = create_test_data(db_session)
        
        # 启用试运行模式
        trial_run_manager.enable_trial_mode(admin_id=1)
        
        # 记录低一致性的差异
        for i in range(100):
            trial_run_manager.record_trial_run_difference(
                scoring_record_id=1,
                auto_score=85.0,
                preset_score=90.0,
                difference_reason="评分标准理解偏差"
            )
        
        # 生成报告
        result = trial_run_manager.generate_consistency_report()
        
        # 验证报告建议
        report_path = Path(result["report_path"])
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "建议继续优化评分标准" in content
            assert "主要差异原因是" in content
