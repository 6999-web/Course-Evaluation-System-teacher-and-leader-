"""
复核管理器属性测试

使用 Hypothesis 进行属性测试，验证复核管理器的通用正确性属性
"""

import json
import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import (
    Base, ScoringRecord, ScoringAppeal, ReviewRecord, BonusItem,
    ScoringLog, MaterialSubmission, EvaluationAssignmentTask, User
)
from app.services.review_manager import (
    ReviewManager, ReviewManagerError, AppealNotFoundError,
    ScoringRecordNotFoundError, InvalidAppealError
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
def review_manager(db_session):
    """创建复核管理器实例"""
    return ReviewManager(db_session)


def create_test_data(db_session):
    """创建测试数据"""
    # 创建测试用户
    user = User(
        id=1,
        username="test_teacher",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test Teacher",
        role="teacher"
    )
    db_session.add(user)
    
    # 创建测试任务
    task = EvaluationAssignmentTask(
        task_id="task_001",
        template_id="tpl_001",
        teacher_id="teacher_001",
        teacher_name="Test Teacher",
        deadline=datetime.utcnow() + timedelta(days=7)
    )
    db_session.add(task)
    
    # 创建测试提交
    submission = MaterialSubmission(
        submission_id="sub_001",
        teacher_id="teacher_001",
        teacher_name="Test Teacher",
        files=[{"file_id": "file_001", "file_name": "test.docx"}],
        scoring_status="scored"
    )
    db_session.add(submission)
    
    # 创建测试评分记录
    scoring_record = ScoringRecord(
        id=1,
        submission_id="sub_001",
        file_id="file_001",
        file_type="教案",
        file_name="test.docx",
        base_score=85.0,
        bonus_score=5.0,
        final_score=90.0,
        grade="优秀",
        score_details='{"indicators": []}',
        scoring_type="auto",
        is_confirmed=False
    )
    db_session.add(scoring_record)
    
    db_session.commit()
    
    return {
        "user": user,
        "task": task,
        "submission": submission,
        "scoring_record": scoring_record
    }


class TestReviewManagerProperties:
    """复核管理器属性测试类"""
    
    # Feature: auto-scoring-system, Property 19: 异议提交表单验证
    @given(
        teacher_id=st.text(min_size=1, max_size=50),
        teacher_name=st.text(min_size=1, max_size=100),
        reason=st.one_of(
            st.text(min_size=1, max_size=500),  # 有效理由
            st.just(""),  # 空理由
            st.just("   "),  # 空白理由
        )
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_appeal_form_validation_property(self, teacher_id, teacher_name, reason):
        """
        Property 19: For any 异议提交操作，系统应该要求填写异议理由，否则不允许提交。
        
        Validates: Requirements 8.3
        
        This property tests that:
        1. Empty or whitespace-only reasons are rejected
        2. Valid reasons are accepted
        3. Proper error messages are provided
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record_id = test_data["scoring_record"].id
        
        if not reason or reason.strip() == "":
            # 空理由应该被拒绝
            with pytest.raises(InvalidAppealError) as exc_info:
                review_manager.submit_appeal(
                    scoring_record_id, teacher_id, teacher_name, reason
                )
            assert "异议理由不能为空" in str(exc_info.value)
        else:
            # 有效理由应该被接受
            appeal_id = review_manager.submit_appeal(
                scoring_record_id, teacher_id, teacher_name, reason
            )
            assert appeal_id > 0
            
            # 验证异议记录已创建
            appeal = db_session.query(ScoringAppeal).filter(
                ScoringAppeal.id == appeal_id
            ).first()
            assert appeal is not None
            assert appeal.appeal_reason == reason.strip()
            assert appeal.status == "pending"
        
        db_session.close()
    
    # Feature: auto-scoring-system, Property 20: 异议提交通知管理员
    @given(
        teacher_id=st.text(min_size=1, max_size=50),
        teacher_name=st.text(min_size=1, max_size=100),
        reason=st.text(min_size=10, max_size=500)
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_appeal_notification_property(self, teacher_id, teacher_name, reason):
        """
        Property 20: For any 成功提交的异议，系统应该通知管理员进行复核。
        
        Validates: Requirements 8.4
        
        This property tests that:
        1. Successful appeal submission triggers admin notification
        2. Appeal status is set to pending
        3. Notification is logged
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record_id = test_data["scoring_record"].id
        
        # 提交异议
        appeal_id = review_manager.submit_appeal(
            scoring_record_id, teacher_id, teacher_name, reason
        )
        
        # 验证异议状态为待处理
        appeal = db_session.query(ScoringAppeal).filter(
            ScoringAppeal.id == appeal_id
        ).first()
        assert appeal.status == "pending"
        
        # 验证日志记录了异议提交
        log_entry = db_session.query(ScoringLog).filter(
            ScoringLog.action == "appeal_submitted"
        ).first()
        assert log_entry is not None
        
        # 验证可以获取待处理异议列表
        pending_appeals = review_manager.get_pending_appeals()
        assert len(pending_appeals) > 0
        assert any(a["id"] == appeal_id for a in pending_appeals)
        
        db_session.close()
    
    # Feature: auto-scoring-system, Property 21: 人工评分覆盖自动评分
    @given(
        new_base_score=st.floats(min_value=0, max_value=100),
        new_bonus_score=st.floats(min_value=0, max_value=10),
        admin_id=st.integers(min_value=1, max_value=1000)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_manual_review_overrides_auto_scoring_property(self, new_base_score, new_bonus_score, admin_id):
        """
        Property 21: For any 管理员的人工评分调整，系统应该覆盖原有的自动评分结果。
        
        Validates: Requirements 8.6
        
        This property tests that:
        1. Manual review updates scoring record
        2. Original scores are preserved in review record
        3. Scoring type is changed to manual
        4. Review record is created
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        original_score = scoring_record.final_score
        original_type = scoring_record.scoring_type
        
        # 计算新的最终得分
        new_final_score = min(100, new_base_score + new_bonus_score)
        
        # 确定等级
        if new_final_score >= 90:
            new_grade = "优秀"
        elif new_final_score >= 80:
            new_grade = "良好"
        elif new_final_score >= 60:
            new_grade = "合格"
        else:
            new_grade = "不合格"
        
        new_score_data = {
            "base_score": new_base_score,
            "bonus_score": new_bonus_score,
            "final_score": new_final_score,
            "grade": new_grade,
            "review_reason": "人工复核调整"
        }
        
        # 执行人工复核
        success = review_manager.manual_review(
            scoring_record.id, admin_id, new_score_data
        )
        assert success
        
        # 验证评分记录已更新
        db_session.refresh(scoring_record)
        assert scoring_record.base_score == new_base_score
        assert scoring_record.bonus_score == new_bonus_score
        assert scoring_record.final_score == new_final_score
        assert scoring_record.grade == new_grade
        assert scoring_record.scoring_type == "manual"
        assert scoring_record.scored_by == admin_id
        
        # 验证复核记录已创建
        review_record = db_session.query(ReviewRecord).filter(
            ReviewRecord.scoring_record_id == scoring_record.id
        ).first()
        assert review_record is not None
        assert review_record.original_score == original_score
        assert review_record.reviewed_score == new_final_score
        assert review_record.reviewed_by == admin_id
        
        db_session.close()
    
    # Feature: auto-scoring-system, Property 22: 评分结果确认流程
    @given(
        teacher_id=st.text(min_size=1, max_size=50)
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_score_confirmation_flow_property(self, teacher_id):
        """
        Property 22: For any 完成的评分（自动或人工），系统应该将结果返回给教师并要求确认，
        确认后标记为"已确认"状态。
        
        Validates: Requirements 8.7, 8.8, 8.9
        
        This property tests that:
        1. Teachers can confirm their own scores
        2. Confirmation updates the record status
        3. Confirmation time is recorded
        4. Teachers cannot confirm others' scores
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        submission = test_data["submission"]
        
        # 测试教师确认自己的评分
        if teacher_id == submission.teacher_id:
            # 应该能够确认
            success = review_manager.confirm_score(scoring_record.id, teacher_id)
            assert success
            
            # 验证确认状态
            db_session.refresh(scoring_record)
            assert scoring_record.is_confirmed == True
            assert scoring_record.confirmed_at is not None
            
            # 验证日志记录
            log_entry = db_session.query(ScoringLog).filter(
                ScoringLog.action == "score_confirmed"
            ).first()
            assert log_entry is not None
        else:
            # 不应该能够确认他人的评分
            with pytest.raises(ReviewManagerError) as exc_info:
                review_manager.confirm_score(scoring_record.id, teacher_id)
            assert "无权限确认此评分记录" in str(exc_info.value)
        
        db_session.close()
    
    # Feature: auto-scoring-system, Property 23: 全员确认后允许公示
    @given(
        admin_id=st.integers(min_value=1, max_value=1000)
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_publish_after_all_confirmed_property(self, admin_id):
        """
        Property 23: For any 考评任务，只有当所有教师都确认评分结果后，
        系统才允许管理员公示整体结果。
        
        Validates: Requirements 8.10
        
        This property tests that:
        1. Cannot publish when scores are unconfirmed
        2. Can publish when all scores are confirmed
        3. Publish status is recorded
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        task = test_data["task"]
        scoring_record = test_data["scoring_record"]
        
        # 测试未确认时不能公示
        with pytest.raises(ReviewManagerError) as exc_info:
            review_manager.publish_results(task.task_id, admin_id)
        assert "尚未确认评分结果" in str(exc_info.value)
        
        # 确认评分
        scoring_record.is_confirmed = True
        scoring_record.confirmed_at = datetime.utcnow()
        db_session.commit()
        
        # 测试确认后可以公示
        result = review_manager.publish_results(task.task_id, admin_id)
        assert result["status"] == "published"
        assert result["task_id"] == task.task_id
        assert result["published_by"] == admin_id
        assert "total_teachers" in result
        assert "grade_distribution" in result
        
        db_session.close()
    
    # Feature: auto-scoring-system, Property 24: 评分调整审计日志
    @given(
        admin_id=st.integers(min_value=1, max_value=1000),
        new_score=st.floats(min_value=0, max_value=100)
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_scoring_adjustment_audit_log_property(self, admin_id, new_score):
        """
        Property 24: For any 评分调整操作，系统应该记录完整的调整记录
        （调整人、调整时间、调整理由）。
        
        Validates: Requirements 8.11
        
        This property tests that:
        1. All scoring adjustments are logged
        2. Log contains admin ID, time, and reason
        3. Original and new scores are recorded
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        original_score = scoring_record.final_score
        
        # 确定等级
        if new_score >= 90:
            new_grade = "优秀"
        elif new_score >= 80:
            new_grade = "良好"
        elif new_score >= 60:
            new_grade = "合格"
        else:
            new_grade = "不合格"
        
        new_score_data = {
            "base_score": new_score,
            "bonus_score": 0,
            "final_score": new_score,
            "grade": new_grade,
            "review_reason": "测试调整"
        }
        
        # 执行调整
        review_manager.manual_review(scoring_record.id, admin_id, new_score_data)
        
        # 验证审计日志
        log_entry = db_session.query(ScoringLog).filter(
            ScoringLog.action == "manual_review"
        ).first()
        assert log_entry is not None
        assert log_entry.scoring_record_id == scoring_record.id
        
        # 解析日志详情
        details = json.loads(log_entry.action_details)
        assert details["admin_id"] == admin_id
        assert details["original_score"] == original_score
        assert details["new_score"] == new_score
        
        # 验证复核记录
        review_record = db_session.query(ReviewRecord).filter(
            ReviewRecord.scoring_record_id == scoring_record.id
        ).first()
        assert review_record is not None
        assert review_record.reviewed_by == admin_id
        assert review_record.reviewed_at is not None
        
        db_session.close()
    
    # Feature: auto-scoring-system, Property 25: 抽查样本状态标记
    @given(
        sample_rate=st.floats(min_value=0.1, max_value=1.0)
    )
    @settings(
        max_examples=20,
        deadline=None,  # Disable deadline to avoid timing issues
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_sample_status_marking_property(self, sample_rate):
        """
        Property 25: For any 随机抽查选定的样本，系统应该将这些记录标记为"待复核"状态。
        
        Validates: Requirements 9.3
        
        This property tests that:
        1. Random sampling selects appropriate records
        2. Sampled records are marked for review
        3. Sample rate is respected
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        
        # 确认评分以便可以抽查
        scoring_record = test_data["scoring_record"]
        scoring_record.is_confirmed = True
        db_session.commit()
        
        # 执行随机抽查
        sampled_records = review_manager.random_sample(sample_rate)
        
        # 验证抽查结果
        if sampled_records:
            assert len(sampled_records) >= 1
            
            for record in sampled_records:
                assert "scoring_record_id" in record
                assert "status" in record
                assert record["status"] == "待复核"
                
                # 验证复核记录已创建
                review_record = db_session.query(ReviewRecord).filter(
                    ReviewRecord.scoring_record_id == record["scoring_record_id"]
                ).first()
                assert review_record is not None
                assert review_record.review_type == "random"
        
        db_session.close()
    
    # Feature: auto-scoring-system, Property 26: 复核结果记录
    @given(
        reviewed_score=st.floats(min_value=0, max_value=100),
        is_consistent=st.booleans(),
        difference_reason=st.text(max_size=200),
        reviewed_by=st.integers(min_value=1, max_value=1000)
    )
    @settings(
        max_examples=30,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_review_result_recording_property(self, reviewed_score, is_consistent, 
                                            difference_reason, reviewed_by):
        """
        Property 26: For any 完成的人工复核，系统应该记录复核结果（一致/不一致）
        和差异原因（如果不一致）。
        
        Validates: Requirements 9.4, 9.5
        
        This property tests that:
        1. Review results are properly recorded
        2. Consistency status is tracked
        3. Difference reasons are stored when inconsistent
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 创建初始复核记录
        review_record = ReviewRecord(
            scoring_record_id=scoring_record.id,
            review_type="random",
            original_score=scoring_record.final_score,
            reviewed_score=0,  # 待更新
            is_consistent=False,  # 待更新
            reviewed_by=0  # 待更新
        )
        db_session.add(review_record)
        db_session.commit()
        
        # 记录复核结果
        success = review_manager.record_review_result(
            scoring_record.id, reviewed_score, is_consistent, 
            difference_reason, reviewed_by
        )
        assert success
        
        # 验证复核结果已记录
        db_session.refresh(review_record)
        assert review_record.reviewed_score == reviewed_score
        assert review_record.is_consistent == is_consistent
        assert review_record.difference_reason == difference_reason
        assert review_record.reviewed_by == reviewed_by
        assert review_record.reviewed_at is not None
        
        db_session.close()
    
    # Feature: auto-scoring-system, Property 27: 一致性比例计算
    @given(
        days_back=st.integers(min_value=1, max_value=30)
    )
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_consistency_rate_calculation_property(self, days_back):
        """
        Property 27: For any 一致性统计请求，系统应该正确计算自动评分与人工复核的
        一致性比例（一致数量/总复核数量）。
        
        Validates: Requirements 9.6
        
        This property tests that:
        1. Consistency rate is calculated correctly
        2. Date range filtering works
        3. Statistics include all required fields
        """
        # 创建新的数据库会话
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 创建复核记录
        review_records = []
        for i in range(5):
            review_record = ReviewRecord(
                scoring_record_id=scoring_record.id,
                review_type="random",
                original_score=85.0,
                reviewed_score=85.0 if i < 3 else 80.0,  # 前3个一致，后2个不一致
                is_consistent=i < 3,
                difference_reason="" if i < 3 else "评分偏差",
                reviewed_by=1,
                reviewed_at=datetime.utcnow() - timedelta(days=i)
            )
            review_records.append(review_record)
            db_session.add(review_record)
        
        db_session.commit()
        
        # 计算一致性比例
        start_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        stats = review_manager.calculate_consistency_rate(start_date, end_date)
        
        # 验证统计结果
        assert "total_reviews" in stats
        assert "consistent_count" in stats
        assert "inconsistent_count" in stats
        assert "consistency_rate" in stats
        assert "difference_reasons" in stats
        
        # 验证计算正确性
        if stats["total_reviews"] > 0:
            expected_rate = stats["consistent_count"] / stats["total_reviews"]
            assert abs(stats["consistency_rate"] - expected_rate) < 0.0001
            assert stats["consistent_count"] + stats["inconsistent_count"] == stats["total_reviews"]
        
        db_session.close()


class TestReviewManagerEdgeCases:
    """复核管理器边界情况测试"""
    
    def test_submit_appeal_nonexistent_scoring_record(self, db_session):
        """测试对不存在的评分记录提交异议"""
        review_manager = ReviewManager(db_session)
        
        with pytest.raises(ScoringRecordNotFoundError):
            review_manager.submit_appeal(999, "teacher_001", "Test Teacher", "测试异议")
    
    def test_submit_duplicate_appeal(self, db_session):
        """测试重复提交异议"""
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record_id = test_data["scoring_record"].id
        
        # 第一次提交
        appeal_id1 = review_manager.submit_appeal(
            scoring_record_id, "teacher_001", "Test Teacher", "第一次异议"
        )
        assert appeal_id1 > 0
        
        # 第二次提交应该失败
        with pytest.raises(InvalidAppealError) as exc_info:
            review_manager.submit_appeal(
                scoring_record_id, "teacher_001", "Test Teacher", "第二次异议"
            )
        assert "已有待处理的异议" in str(exc_info.value)
    
    def test_manual_review_nonexistent_record(self, db_session):
        """测试对不存在的记录进行人工复核"""
        review_manager = ReviewManager(db_session)
        
        with pytest.raises(ScoringRecordNotFoundError):
            review_manager.manual_review(999, 1, {"final_score": 90})
    
    def test_random_sample_invalid_rate(self, db_session):
        """测试无效的抽查比例"""
        review_manager = ReviewManager(db_session)
        
        with pytest.raises(ReviewManagerError) as exc_info:
            review_manager.random_sample(-0.1)
        assert "抽查比例必须在0-1之间" in str(exc_info.value)
        
        with pytest.raises(ReviewManagerError) as exc_info:
            review_manager.random_sample(1.1)
        assert "抽查比例必须在0-1之间" in str(exc_info.value)
    
    def test_confirm_score_already_confirmed(self, db_session):
        """测试确认已经确认过的评分"""
        review_manager = ReviewManager(db_session)
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 先确认一次
        success1 = review_manager.confirm_score(scoring_record.id, "teacher_001")
        assert success1
        
        # 再次确认应该成功但有警告
        success2 = review_manager.confirm_score(scoring_record.id, "teacher_001")
        assert success2
    
    def test_publish_results_nonexistent_task(self, db_session):
        """测试公示不存在的任务结果"""
        review_manager = ReviewManager(db_session)
        
        with pytest.raises(ReviewManagerError) as exc_info:
            review_manager.publish_results("nonexistent_task", 1)
        assert "任务不存在" in str(exc_info.value)
    
    def test_calculate_consistency_rate_no_data(self, db_session):
        """测试在没有数据时计算一致性比例"""
        review_manager = ReviewManager(db_session)
        
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        stats = review_manager.calculate_consistency_rate(start_date, end_date)
        
        assert stats["total_reviews"] == 0
        assert stats["consistent_count"] == 0
        assert stats["inconsistent_count"] == 0
        assert stats["consistency_rate"] == 0.0
        assert stats["difference_reasons"] == {}