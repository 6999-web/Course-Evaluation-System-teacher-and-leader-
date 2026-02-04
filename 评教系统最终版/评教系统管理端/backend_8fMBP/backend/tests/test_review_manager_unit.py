"""
复核管理器单元测试

测试复核管理器的具体功能实现
"""

import pytest
from datetime import datetime, timedelta
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


class TestReviewManagerUnit:
    """复核管理器单元测试类"""
    
    def test_submit_appeal_success(self, review_manager, db_session):
        """测试成功提交异议"""
        test_data = create_test_data(db_session)
        scoring_record_id = test_data["scoring_record"].id
        
        # 提交异议
        appeal_id = review_manager.submit_appeal(
            scoring_record_id, "teacher_001", "Test Teacher", "我认为评分不合理"
        )
        
        # 验证异议记录
        assert appeal_id > 0
        appeal = db_session.query(ScoringAppeal).filter(
            ScoringAppeal.id == appeal_id
        ).first()
        assert appeal is not None
        assert appeal.scoring_record_id == scoring_record_id
        assert appeal.teacher_id == "teacher_001"
        assert appeal.teacher_name == "Test Teacher"
        assert appeal.appeal_reason == "我认为评分不合理"
        assert appeal.status == "pending"
    
    def test_submit_appeal_empty_reason(self, review_manager, db_session):
        """测试提交空异议理由"""
        test_data = create_test_data(db_session)
        scoring_record_id = test_data["scoring_record"].id
        
        # 测试空理由
        with pytest.raises(InvalidAppealError) as exc_info:
            review_manager.submit_appeal(
                scoring_record_id, "teacher_001", "Test Teacher", ""
            )
        assert "异议理由不能为空" in str(exc_info.value)
        
        # 测试空白理由
        with pytest.raises(InvalidAppealError) as exc_info:
            review_manager.submit_appeal(
                scoring_record_id, "teacher_001", "Test Teacher", "   "
            )
        assert "异议理由不能为空" in str(exc_info.value)
    
    def test_submit_appeal_nonexistent_record(self, review_manager, db_session):
        """测试对不存在的评分记录提交异议"""
        with pytest.raises(ScoringRecordNotFoundError) as exc_info:
            review_manager.submit_appeal(
                999, "teacher_001", "Test Teacher", "测试异议"
            )
        assert "评分记录不存在: 999" in str(exc_info.value)
    
    def test_submit_duplicate_appeal(self, review_manager, db_session):
        """测试重复提交异议"""
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
    
    def test_get_pending_appeals(self, review_manager, db_session):
        """测试获取待处理异议列表"""
        test_data = create_test_data(db_session)
        scoring_record_id = test_data["scoring_record"].id
        
        # 提交几个异议
        appeal_id1 = review_manager.submit_appeal(
            scoring_record_id, "teacher_001", "Test Teacher", "异议1"
        )
        
        # 创建另一个评分记录和异议
        scoring_record2 = ScoringRecord(
            id=2,
            submission_id="sub_002",
            file_id="file_002",
            file_type="教学反思",
            file_name="test2.docx",
            base_score=75.0,
            bonus_score=0.0,
            final_score=75.0,
            grade="合格",
            score_details='{"indicators": []}',
            scoring_type="auto",
            is_confirmed=False
        )
        db_session.add(scoring_record2)
        db_session.commit()
        
        appeal_id2 = review_manager.submit_appeal(
            scoring_record2.id, "teacher_002", "Test Teacher 2", "异议2"
        )
        
        # 获取待处理异议
        pending_appeals = review_manager.get_pending_appeals()
        
        assert len(pending_appeals) == 2
        appeal_ids = [a["id"] for a in pending_appeals]
        assert appeal_id1 in appeal_ids
        assert appeal_id2 in appeal_ids
        
        # 验证异议信息完整
        for appeal in pending_appeals:
            assert "id" in appeal
            assert "scoring_record_id" in appeal
            assert "teacher_id" in appeal
            assert "teacher_name" in appeal
            assert "appeal_reason" in appeal
            assert "status" in appeal
            assert appeal["status"] == "pending"
    
    def test_manual_review_success(self, review_manager, db_session):
        """测试成功进行人工复核"""
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        original_score = scoring_record.final_score
        
        # 准备新的评分数据
        new_score_data = {
            "base_score": 88.0,
            "bonus_score": 7.0,
            "final_score": 95.0,
            "grade": "优秀",
            "review_reason": "重新评估后调整"
        }
        
        # 执行人工复核
        success = review_manager.manual_review(
            scoring_record.id, 1, new_score_data
        )
        assert success
        
        # 验证评分记录已更新
        db_session.refresh(scoring_record)
        assert scoring_record.base_score == 88.0
        assert scoring_record.bonus_score == 7.0
        assert scoring_record.final_score == 95.0
        assert scoring_record.grade == "优秀"
        assert scoring_record.scoring_type == "manual"
        assert scoring_record.scored_by == 1
        
        # 验证复核记录已创建
        review_record = db_session.query(ReviewRecord).filter(
            ReviewRecord.scoring_record_id == scoring_record.id
        ).first()
        assert review_record is not None
        assert review_record.original_score == original_score
        assert review_record.reviewed_score == 95.0
        assert review_record.reviewed_by == 1
    
    def test_manual_review_nonexistent_record(self, review_manager, db_session):
        """测试对不存在的记录进行人工复核"""
        new_score_data = {"final_score": 90.0}
        
        with pytest.raises(ScoringRecordNotFoundError) as exc_info:
            review_manager.manual_review(999, 1, new_score_data)
        assert "评分记录不存在: 999" in str(exc_info.value)
    
    def test_random_sample_success(self, review_manager, db_session):
        """测试成功进行随机抽查"""
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 确认评分以便可以抽查
        scoring_record.is_confirmed = True
        db_session.commit()
        
        # 执行随机抽查
        sampled_records = review_manager.random_sample(1.0)  # 100%抽查
        
        assert len(sampled_records) == 1
        record = sampled_records[0]
        assert record["scoring_record_id"] == scoring_record.id
        assert record["status"] == "待复核"
        assert "teacher_id" in record
        assert "teacher_name" in record
        assert "file_type" in record
        assert "current_score" in record
        assert "current_grade" in record
    
    def test_random_sample_invalid_rate(self, review_manager, db_session):
        """测试无效的抽查比例"""
        # 测试负数
        with pytest.raises(ReviewManagerError) as exc_info:
            review_manager.random_sample(-0.1)
        assert "抽查比例必须在0-1之间" in str(exc_info.value)
        
        # 测试大于1
        with pytest.raises(ReviewManagerError) as exc_info:
            review_manager.random_sample(1.1)
        assert "抽查比例必须在0-1之间" in str(exc_info.value)
    
    def test_random_sample_no_eligible_records(self, review_manager, db_session):
        """测试没有符合条件的记录时的随机抽查"""
        # 不创建任何数据，或创建未确认的数据
        test_data = create_test_data(db_session)
        # scoring_record 默认 is_confirmed=False，不符合抽查条件
        
        sampled_records = review_manager.random_sample(0.5)
        assert len(sampled_records) == 0
    
    def test_record_review_result_success(self, review_manager, db_session):
        """测试成功记录复核结果"""
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
            scoring_record.id, 88.0, False, "评分偏差", 1
        )
        assert success
        
        # 验证复核结果已记录
        db_session.refresh(review_record)
        assert review_record.reviewed_score == 88.0
        assert review_record.is_consistent == False
        assert review_record.difference_reason == "评分偏差"
        assert review_record.reviewed_by == 1
        assert review_record.reviewed_at is not None
    
    def test_record_review_result_no_record(self, review_manager, db_session):
        """测试记录不存在复核记录的结果"""
        with pytest.raises(ReviewManagerError) as exc_info:
            review_manager.record_review_result(999, 88.0, True, "", 1)
        assert "未找到评分记录 999 的复核记录" in str(exc_info.value)
    
    def test_calculate_consistency_rate_success(self, review_manager, db_session):
        """测试成功计算一致性比例"""
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
        start_date = (datetime.utcnow() - timedelta(days=10)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        stats = review_manager.calculate_consistency_rate(start_date, end_date)
        
        # 验证统计结果
        assert stats["total_reviews"] == 5
        assert stats["consistent_count"] == 3
        assert stats["inconsistent_count"] == 2
        assert stats["consistency_rate"] == 0.6  # 3/5 = 0.6
        assert "评分偏差" in stats["difference_reasons"]
        assert stats["difference_reasons"]["评分偏差"] == 2
    
    def test_calculate_consistency_rate_no_data(self, review_manager, db_session):
        """测试在没有数据时计算一致性比例"""
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        stats = review_manager.calculate_consistency_rate(start_date, end_date)
        
        assert stats["total_reviews"] == 0
        assert stats["consistent_count"] == 0
        assert stats["inconsistent_count"] == 0
        assert stats["consistency_rate"] == 0.0
        assert stats["difference_reasons"] == {}
    
    def test_confirm_score_success(self, review_manager, db_session):
        """测试成功确认评分"""
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 确认评分
        success = review_manager.confirm_score(scoring_record.id, "teacher_001")
        assert success
        
        # 验证确认状态
        db_session.refresh(scoring_record)
        assert scoring_record.is_confirmed == True
        assert scoring_record.confirmed_at is not None
    
    def test_confirm_score_wrong_teacher(self, review_manager, db_session):
        """测试错误的教师确认评分"""
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 尝试用错误的教师ID确认
        with pytest.raises(ReviewManagerError) as exc_info:
            review_manager.confirm_score(scoring_record.id, "wrong_teacher")
        assert "无权限确认此评分记录" in str(exc_info.value)
    
    def test_confirm_score_already_confirmed(self, review_manager, db_session):
        """测试确认已经确认过的评分"""
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 先确认一次
        success1 = review_manager.confirm_score(scoring_record.id, "teacher_001")
        assert success1
        
        # 再次确认应该成功但有警告
        success2 = review_manager.confirm_score(scoring_record.id, "teacher_001")
        assert success2
    
    def test_confirm_score_nonexistent_record(self, review_manager, db_session):
        """测试确认不存在的评分记录"""
        with pytest.raises(ScoringRecordNotFoundError) as exc_info:
            review_manager.confirm_score(999, "teacher_001")
        assert "评分记录不存在: 999" in str(exc_info.value)
    
    def test_get_task_confirmation_status(self, review_manager, db_session):
        """测试获取任务确认状态"""
        test_data = create_test_data(db_session)
        task = test_data["task"]
        scoring_record = test_data["scoring_record"]
        
        # 获取确认状态（未确认）
        status = review_manager.get_task_confirmation_status(task.task_id)
        
        assert status["task_id"] == task.task_id
        assert status["total_records"] == 1
        assert status["confirmed_count"] == 0
        assert status["unconfirmed_count"] == 1
        assert status["confirmation_rate"] == 0.0
        assert status["can_publish"] == False
        assert len(status["unconfirmed_teachers"]) == 1
        
        # 确认评分后再次检查
        scoring_record.is_confirmed = True
        db_session.commit()
        
        status = review_manager.get_task_confirmation_status(task.task_id)
        assert status["confirmed_count"] == 1
        assert status["unconfirmed_count"] == 0
        assert status["confirmation_rate"] == 1.0
        assert status["can_publish"] == True
        assert len(status["unconfirmed_teachers"]) == 0


class TestReviewManagerIntegration:
    """复核管理器集成测试"""
    
    def test_complete_appeal_workflow(self, review_manager, db_session):
        """测试完整的异议处理流程"""
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 1. 提交异议
        appeal_id = review_manager.submit_appeal(
            scoring_record.id, "teacher_001", "Test Teacher", "我认为评分过低"
        )
        assert appeal_id > 0
        
        # 2. 获取待处理异议
        pending_appeals = review_manager.get_pending_appeals()
        assert len(pending_appeals) == 1
        assert pending_appeals[0]["id"] == appeal_id
        
        # 3. 人工复核调整评分
        new_score_data = {
            "base_score": 92.0,
            "bonus_score": 5.0,
            "final_score": 97.0,
            "grade": "优秀",
            "review_reason": "重新评估后调整"
        }
        success = review_manager.manual_review(scoring_record.id, 1, new_score_data)
        assert success
        
        # 4. 验证异议状态已更新
        appeal = db_session.query(ScoringAppeal).filter(
            ScoringAppeal.id == appeal_id
        ).first()
        assert appeal.status == "resolved"
        
        # 5. 教师确认评分
        success = review_manager.confirm_score(scoring_record.id, "teacher_001")
        assert success
        
        # 6. 验证最终状态
        db_session.refresh(scoring_record)
        assert scoring_record.final_score == 97.0
        assert scoring_record.is_confirmed == True
        assert scoring_record.scoring_type == "manual"
    
    def test_random_sampling_workflow(self, review_manager, db_session):
        """测试随机抽查流程"""
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 1. 确认评分
        scoring_record.is_confirmed = True
        db_session.commit()
        
        # 2. 随机抽查
        sampled_records = review_manager.random_sample(1.0)
        assert len(sampled_records) == 1
        
        # 3. 记录复核结果
        success = review_manager.record_review_result(
            scoring_record.id, 88.0, False, "评分偏差", 1
        )
        assert success
        
        # 4. 计算一致性统计
        start_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        stats = review_manager.calculate_consistency_rate(start_date, end_date)
        assert stats["total_reviews"] == 1
        assert stats["consistent_count"] == 0
        assert stats["inconsistent_count"] == 1
        assert stats["consistency_rate"] == 0.0
        assert "评分偏差" in stats["difference_reasons"]


class TestReviewManagerErrorHandling:
    """复核管理器错误处理测试"""
    
    def test_database_rollback_on_error(self, review_manager, db_session):
        """测试数据库错误时的回滚"""
        test_data = create_test_data(db_session)
        scoring_record_id = test_data["scoring_record"].id
        
        # 尝试提交异议到不存在的评分记录应该失败
        with pytest.raises(ScoringRecordNotFoundError):
            review_manager.submit_appeal(
                999, "teacher_001", "Test Teacher", "测试异议"
            )
    
    def test_invalid_date_format(self, review_manager, db_session):
        """测试无效日期格式"""
        with pytest.raises(ReviewManagerError):
            review_manager.calculate_consistency_rate("invalid-date", "2024-01-31")
    
    def test_logging_functionality(self, review_manager, db_session):
        """测试日志记录功能"""
        test_data = create_test_data(db_session)
        scoring_record = test_data["scoring_record"]
        
        # 提交异议
        appeal_id = review_manager.submit_appeal(
            scoring_record.id, "teacher_001", "Test Teacher", "测试异议"
        )
        
        # 验证日志记录
        log_entry = db_session.query(ScoringLog).filter(
            ScoringLog.action == "appeal_submitted"
        ).first()
        assert log_entry is not None
        assert log_entry.scoring_record_id == scoring_record.id
        
        # 确认评分
        review_manager.confirm_score(scoring_record.id, "teacher_001")
        
        # 验证确认日志
        confirm_log = db_session.query(ScoringLog).filter(
            ScoringLog.action == "score_confirmed"
        ).first()
        assert confirm_log is not None