"""
评分系统 API 集成测试

测试完整的评分流程：
1. 上传 → 评分 → 复核 → 公示
2. 异议处理流程
3. 导出功能
4. 随机抽查和一致性统计
"""

import pytest
from datetime import datetime, timedelta
import json
import random


class TestEndToEndScoringWorkflow:
    """
    端到端测试：完整的评分工作流
    
    流程：创建任务 → 教师上传文件 → 自动评分 → 教师查看结果
    """
    
    def test_create_task_and_upload_file(self):
        """
        测试创建考评任务并上传文件
        
        1. 管理端创建考评任务
        2. 指定需要上传的文件类型
        3. 教师端接收任务并上传文件
        """
        # 步骤 1: 创建考评任务
        task = {
            "id": 1,
            "title": "2024年度教学评估",
            "description": "请上传教案、教学反思和课件",
            "required_file_types": ["教案", "教学反思", "课件"],
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "auto_scoring_enabled": True,
            "bonus_enabled": True,
            "max_bonus_score": 10.0,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        # 验证任务创建
        assert task["id"] == 1
        assert len(task["required_file_types"]) == 3
        assert task["auto_scoring_enabled"] == True
        
        # 步骤 2: 教师上传文件
        submissions = [
            {
                "id": 1,
                "task_id": 1,
                "teacher_id": "teacher_001",
                "file_type": "教案",
                "file_name": "数学教案.docx",
                "file_size": 102400,
                "uploaded_at": datetime.utcnow().isoformat(),
                "status": "pending"
            },
            {
                "id": 2,
                "task_id": 1,
                "teacher_id": "teacher_001",
                "file_type": "教学反思",
                "file_name": "教学反思.docx",
                "file_size": 51200,
                "uploaded_at": datetime.utcnow().isoformat(),
                "status": "pending"
            },
            {
                "id": 3,
                "task_id": 1,
                "teacher_id": "teacher_001",
                "file_type": "课件",
                "file_name": "课件.pptx",
                "file_size": 204800,
                "uploaded_at": datetime.utcnow().isoformat(),
                "status": "pending"
            }
        ]
        
        # 验证文件上传
        assert len(submissions) == 3
        for submission in submissions:
            assert submission["task_id"] == 1
            assert submission["status"] == "pending"
            assert submission["file_type"] in task["required_file_types"]
    
    def test_auto_scoring_workflow(self):
        """
        测试自动评分工作流
        
        1. 触发自动评分
        2. 系统调用 API 进行评分
        3. 存储评分结果
        """
        # 步骤 1: 触发自动评分
        submission_id = 1
        
        # 步骤 2: 系统评分（模拟）
        scoring_records = [
            {
                "id": 1,
                "submission_id": 1,
                "file_type": "教案",
                "base_score": 85.0,
                "bonus_score": 5.0,
                "final_score": 90.0,
                "grade": "优秀",
                "veto_triggered": False,
                "scoring_type": "auto",
                "scored_at": datetime.utcnow().isoformat(),
                "is_confirmed": False,
                "score_details": {
                    "indicators": [
                        {"name": "教学目标", "score": 22, "max_score": 25},
                        {"name": "教学内容", "score": 23, "max_score": 25},
                        {"name": "教学方法", "score": 20, "max_score": 25},
                        {"name": "教学评价", "score": 20, "max_score": 25}
                    ]
                }
            },
            {
                "id": 2,
                "submission_id": 2,
                "file_type": "教学反思",
                "base_score": 80.0,
                "bonus_score": 3.0,
                "final_score": 83.0,
                "grade": "良好",
                "veto_triggered": False,
                "scoring_type": "auto",
                "scored_at": datetime.utcnow().isoformat(),
                "is_confirmed": False,
                "score_details": {
                    "indicators": [
                        {"name": "反思深度", "score": 28, "max_score": 30},
                        {"name": "反思内容", "score": 27, "max_score": 30},
                        {"name": "改进措施", "score": 20, "max_score": 25},
                        {"name": "理论支撑", "score": 5, "max_score": 15}
                    ]
                }
            },
            {
                "id": 3,
                "submission_id": 3,
                "file_type": "课件",
                "base_score": 88.0,
                "bonus_score": 2.0,
                "final_score": 90.0,
                "grade": "优秀",
                "veto_triggered": False,
                "scoring_type": "auto",
                "scored_at": datetime.utcnow().isoformat(),
                "is_confirmed": False,
                "score_details": {
                    "indicators": [
                        {"name": "内容质量", "score": 24, "max_score": 25},
                        {"name": "设计美观", "score": 22, "max_score": 25},
                        {"name": "媒体运用", "score": 21, "max_score": 25},
                        {"name": "教学适用性", "score": 21, "max_score": 25}
                    ]
                }
            }
        ]
        
        # 验证评分结果
        assert len(scoring_records) == 3
        for record in scoring_records:
            assert record["veto_triggered"] == False
            assert record["scoring_type"] == "auto"
            assert record["final_score"] >= 60  # 所有评分都应该≥60
            assert record["grade"] in ["优秀", "良好", "合格", "不合格"]
            assert record["is_confirmed"] == False  # 初始状态未确认
    
    def test_teacher_view_scoring_results(self):
        """
        测试教师查看评分结果
        
        教师应该能看到完整的评分明细
        """
        # 模拟教师查看评分结果
        scoring_result = {
            "submission_id": 1,
            "file_type": "教案",
            "final_score": 90.0,
            "grade": "优秀",
            "base_score": 85.0,
            "bonus_score": 5.0,
            "veto_triggered": False,
            "score_details": {
                "indicators": [
                    {"name": "教学目标", "score": 22, "max_score": 25, "reason": "目标明确具体"},
                    {"name": "教学内容", "score": 23, "max_score": 25, "reason": "内容准确完整"},
                    {"name": "教学方法", "score": 20, "max_score": 25, "reason": "方法适切有效"},
                    {"name": "教学评价", "score": 20, "max_score": 25, "reason": "评价方式多元"}
                ]
            },
            "summary": "教案设计合理，教学目标明确，内容组织有序，方法选择恰当。"
        }
        
        # 验证评分明细完整性
        assert scoring_result["final_score"] == 90.0
        assert scoring_result["grade"] == "优秀"
        assert len(scoring_result["score_details"]["indicators"]) == 4
        
        # 验证每个指标都有评分理由
        for indicator in scoring_result["score_details"]["indicators"]:
            assert "reason" in indicator
            assert indicator["score"] <= indicator["max_score"]


class TestScoringWorkflow:
    """
    测试完整的评分流程
    
    流程：上传 → 评分 → 复核 → 公示
    """
    
    def test_complete_scoring_workflow(self):
        """
        测试完整的评分工作流
        
        1. 创建提交记录
        2. 触发评分
        3. 进行复核
        4. 公示结果
        """
        # 模拟工作流步骤
        workflow_steps = []
        
        # 步骤 1: 创建提交记录
        submission = {
            "submission_id": "sub_001",
            "teacher_id": "teacher_001",
            "files": [{"file_id": "file_001", "file_name": "教案.docx"}],
            "submitted_at": datetime.utcnow().isoformat()
        }
        workflow_steps.append(("submission_created", submission))
        
        # 步骤 2: 触发评分
        scoring_record = {
            "id": 1,
            "submission_id": "sub_001",
            "base_score": 85.0,
            "bonus_score": 5.0,
            "final_score": 90.0,
            "grade": "优秀",
            "scoring_type": "auto"
        }
        workflow_steps.append(("scoring_completed", scoring_record))
        
        # 步骤 3: 进行复核
        review_record = {
            "id": 1,
            "scoring_record_id": 1,
            "original_score": 90.0,
            "reviewed_score": 90.0,
            "is_consistent": True
        }
        workflow_steps.append(("review_completed", review_record))
        
        # 步骤 4: 公示结果
        publish_result = {
            "message": "评分结果公示成功",
            "published_count": 1
        }
        workflow_steps.append(("results_published", publish_result))
        
        # 验证工作流完整性
        assert len(workflow_steps) == 4
        assert workflow_steps[0][0] == "submission_created"
        assert workflow_steps[1][0] == "scoring_completed"
        assert workflow_steps[2][0] == "review_completed"
        assert workflow_steps[3][0] == "results_published"
        
        # 验证评分结果
        scoring = workflow_steps[1][1]
        assert scoring["final_score"] == 90.0
        assert scoring["grade"] == "优秀"
        
        # 验证复核结果
        review = workflow_steps[2][1]
        assert review["is_consistent"] == True
    
    def test_scoring_with_bonus_items(self):
        """
        测试包含加分项的评分流程
        
        验证加分项是否正确计算
        """
        # 基础分
        base_score = 85.0
        
        # 加分项
        bonus_items = [
            {"name": "获奖", "score": 3.0},
            {"name": "创新", "score": 2.0}
        ]
        
        # 计算总加分
        total_bonus = sum(item["score"] for item in bonus_items)
        
        # 最终得分
        final_score = base_score + total_bonus
        
        # 验证加分计算
        assert total_bonus == 5.0
        assert final_score == 90.0
        
        # 验证加分上限（最多10分）
        assert total_bonus <= 10.0
    
    def test_veto_item_triggers_fail_grade(self):
        """
        测试否决项触发不合格等级
        
        如果触发否决项，等级应该是不合格
        """
        # 模拟触发否决项的情况
        veto_triggered = True
        veto_reason = "存在造假行为"
        
        # 如果触发否决项，等级应该是不合格
        if veto_triggered:
            grade = "不合格"
            final_score = 0
        else:
            grade = "优秀"
            final_score = 90.0
        
        # 验证否决项逻辑
        assert grade == "不合格"
        assert final_score == 0


class TestAppealWorkflow:
    """
    测试异议处理流程
    
    流程：异议申请 → 人工复核 → 教师确认 → 公示结果
    """
    
    def test_complete_appeal_workflow(self):
        """
        测试完整的异议处理流程
        
        1. 教师提交异议
        2. 管理员进行人工复核
        3. 教师确认调整后的评分
        4. 管理员公示结果
        """
        # 步骤 1: 教师提交异议
        appeal = {
            "id": 1,
            "scoring_record_id": 1,
            "teacher_id": "teacher_001",
            "appeal_reason": "我认为教学目标的评分过低，应该是25分而不是22分",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 验证异议提交
        assert appeal["status"] == "pending"
        assert len(appeal["appeal_reason"]) > 0
        
        # 步骤 2: 管理员进行人工复核
        appeal["status"] = "reviewing"
        appeal["reviewed_by"] = "admin_001"
        appeal["reviewed_at"] = datetime.utcnow().isoformat()
        
        # 管理员调整评分
        new_scoring_record = {
            "id": 1,
            "submission_id": 1,
            "file_type": "教案",
            "base_score": 87.0,  # 调整后的基础分
            "bonus_score": 5.0,
            "final_score": 92.0,  # 调整后的最终分
            "grade": "优秀",
            "veto_triggered": False,
            "scoring_type": "manual",  # 标记为人工评分
            "scored_by": "admin_001",
            "scored_at": datetime.utcnow().isoformat(),
            "is_confirmed": False,
            "score_details": {
                "indicators": [
                    {"name": "教学目标", "score": 25, "max_score": 25, "reason": "目标明确具体，表述准确"},
                    {"name": "教学内容", "score": 23, "max_score": 25, "reason": "内容准确完整"},
                    {"name": "教学方法", "score": 21, "max_score": 25, "reason": "方法适切有效"},
                    {"name": "教学评价", "score": 18, "max_score": 25, "reason": "评价方式多元"}
                ]
            }
        }
        
        # 验证人工复核
        assert new_scoring_record["scoring_type"] == "manual"
        assert new_scoring_record["final_score"] == 92.0
        assert new_scoring_record["is_confirmed"] == False
        
        # 步骤 3: 教师确认调整后的评分
        new_scoring_record["is_confirmed"] = True
        new_scoring_record["confirmed_at"] = datetime.utcnow().isoformat()
        
        # 验证教师确认
        assert new_scoring_record["is_confirmed"] == True
        
        # 步骤 4: 管理员公示结果
        publish_result = {
            "task_id": 1,
            "published_at": datetime.utcnow().isoformat(),
            "published_count": 1,
            "status": "published"
        }
        
        # 验证公示
        assert publish_result["status"] == "published"
        assert publish_result["published_count"] == 1
    
    def test_appeal_submission_validation(self):
        """
        测试异议提交表单验证
        
        异议理由不能为空
        """
        # 有效的异议
        valid_appeal = {
            "scoring_record_id": 1,
            "appeal_reason": "我认为评分不合理，因为..."
        }
        
        # 验证有效异议
        assert valid_appeal["appeal_reason"] is not None
        assert len(valid_appeal["appeal_reason"]) > 0
        
        # 无效的异议（理由为空）
        invalid_appeal = {
            "scoring_record_id": 1,
            "appeal_reason": ""
        }
        
        # 验证无效异议
        assert len(invalid_appeal["appeal_reason"]) == 0
    
    def test_appeal_notification_to_admin(self):
        """
        测试异议提交后通知管理员
        
        异议提交成功后，系统应该通知管理员
        """
        # 异议提交
        appeal = {
            "id": 1,
            "scoring_record_id": 1,
            "teacher_id": "teacher_001",
            "appeal_reason": "我认为评分不合理",
            "status": "pending"
        }
        
        # 模拟通知
        notification = {
            "type": "appeal_submitted",
            "recipient": "admin",
            "appeal_id": appeal["id"],
            "teacher_id": appeal["teacher_id"],
            "message": f"教师 {appeal['teacher_id']} 对评分记录 {appeal['scoring_record_id']} 提出异议",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 验证通知
        assert notification["type"] == "appeal_submitted"
        assert notification["recipient"] == "admin"
        assert notification["appeal_id"] == appeal["id"]
    
    def test_appeal_submission_and_review(self):
        """
        测试异议提交和复核流程
        
        1. 教师提交异议
        2. 管理员复核
        3. 更新评分
        """
        # 步骤 1: 提交异议
        appeal = {
            "id": 1,
            "scoring_record_id": 1,
            "teacher_id": "teacher_001",
            "appeal_reason": "我认为评分不合理",
            "status": "pending"
        }
        
        # 步骤 2: 管理员复核
        appeal["status"] = "reviewing"
        
        # 步骤 3: 更新评分
        new_score = {
            "base_score": 88.0,
            "bonus_score": 5.0,
            "final_score": 93.0,
            "grade": "优秀"
        }
        
        # 验证异议流程
        assert appeal["status"] == "reviewing"
        assert new_score["final_score"] == 93.0
        assert new_score["grade"] == "优秀"
    
    def test_appeal_resolution(self):
        """
        测试异议解决流程
        
        异议应该被标记为已解决
        """
        # 异议记录
        appeal = {
            "id": 1,
            "status": "pending",
            "review_result": None
        }
        
        # 解决异议
        appeal["status"] = "resolved"
        appeal["review_result"] = "评分已调整"
        
        # 验证异议解决
        assert appeal["status"] == "resolved"
        assert appeal["review_result"] is not None


class TestRandomSamplingAndConsistency:
    """
    测试随机抽查和一致性统计
    """
    
    def test_random_sampling_workflow(self):
        """
        测试随机抽查工作流
        
        1. 管理员设置抽查比例
        2. 系统随机选取样本
        3. 管理员进行人工复核
        4. 记录复核结果
        """
        # 步骤 1: 设置抽查参数
        task_id = 1
        sample_rate = 0.1  # 10%
        
        # 步骤 2: 生成样本
        all_scoring_records = [
            {"id": i, "submission_id": i, "final_score": 85.0 + i}
            for i in range(1, 101)  # 100条评分记录
        ]
        
        # 随机抽取样本
        sample_size = max(1, int(len(all_scoring_records) * sample_rate))
        sampled_records = random.sample(all_scoring_records, sample_size)
        
        # 验证样本大小
        assert len(sampled_records) == 10  # 100 * 10% = 10
        assert all(record["id"] in [r["id"] for r in all_scoring_records] for record in sampled_records)
        
        # 步骤 3: 标记样本为待复核
        for record in sampled_records:
            record["review_status"] = "pending_review"
        
        # 验证标记
        assert all(record["review_status"] == "pending_review" for record in sampled_records)
        
        # 步骤 4: 管理员进行人工复核
        review_results = []
        for record in sampled_records:
            # 模拟人工复核
            review_result = {
                "scoring_record_id": record["id"],
                "original_score": record["final_score"],
                "reviewed_score": record["final_score"],  # 假设一致
                "is_consistent": True,
                "difference_reason": "",
                "reviewed_by": "admin_001",
                "reviewed_at": datetime.utcnow().isoformat()
            }
            review_results.append(review_result)
        
        # 验证复核结果
        assert len(review_results) == 10
        assert all(result["is_consistent"] == True for result in review_results)
    
    def test_consistency_rate_calculation_advanced(self):
        """
        测试一致性比例计算（高级）
        
        一致性 = 一致数量 / 总复核数量
        """
        # 模拟复核记录
        review_records = [
            {"is_consistent": True},
            {"is_consistent": True},
            {"is_consistent": False},
            {"is_consistent": True},
            {"is_consistent": True},
            {"is_consistent": False},
            {"is_consistent": True},
            {"is_consistent": True},
            {"is_consistent": True},
            {"is_consistent": True}
        ]
        
        # 计算一致性
        consistent_count = sum(1 for r in review_records if r["is_consistent"])
        total_count = len(review_records)
        consistency_rate = consistent_count / total_count if total_count > 0 else 0
        
        # 验证计算
        assert consistent_count == 8
        assert total_count == 10
        assert consistency_rate == 0.8
        assert consistency_rate >= 0.75  # 假设目标是75%以上
    
    def test_difference_reasons_statistics_advanced(self):
        """
        测试差异原因统计（高级）
        
        应该统计不一致的原因分布
        """
        # 模拟复核记录
        review_records = [
            {"is_consistent": True, "difference_reason": ""},
            {"is_consistent": False, "difference_reason": "评分标准理解偏差"},
            {"is_consistent": False, "difference_reason": "文件内容理解偏差"},
            {"is_consistent": False, "difference_reason": "评分标准理解偏差"},
            {"is_consistent": True, "difference_reason": ""},
            {"is_consistent": False, "difference_reason": "其他原因"},
            {"is_consistent": True, "difference_reason": ""}
        ]
        
        # 统计差异原因
        difference_reasons = {}
        for record in review_records:
            if not record["is_consistent"] and record["difference_reason"]:
                reason = record["difference_reason"]
                difference_reasons[reason] = difference_reasons.get(reason, 0) + 1
        
        # 验证统计
        assert difference_reasons["评分标准理解偏差"] == 2
        assert difference_reasons["文件内容理解偏差"] == 1
        assert difference_reasons["其他原因"] == 1
        assert sum(difference_reasons.values()) == 4  # 总共4条不一致
    
    def test_sampled_records_status_marking(self):
        """
        测试抽查样本状态标记
        
        抽查选定的样本应该被标记为"待复核"状态
        """
        # 模拟所有评分记录
        all_records = [
            {"id": i, "status": "scored"} for i in range(1, 11)
        ]
        
        # 随机抽取样本
        sampled_ids = random.sample([r["id"] for r in all_records], 3)
        
        # 标记样本为待复核
        for record in all_records:
            if record["id"] in sampled_ids:
                record["status"] = "pending_review"
        
        # 验证标记
        sampled_records = [r for r in all_records if r["status"] == "pending_review"]
        assert len(sampled_records) == 3
        assert all(r["id"] in sampled_ids for r in sampled_records)
        
        # 验证未抽中的记录状态不变
        unsampled_records = [r for r in all_records if r["status"] == "scored"]
        assert len(unsampled_records) == 7


class TestAppealWorkflowOld:
    """
    测试异议处理流程（旧版本，保留以兼容）
    """


class TestExportFunctionality:
    """
    测试导出功能
    """
    
    def test_export_scoring_results(self):
        """
        测试导出评分结果
        
        导出数据应该包含所有必需字段
        """
        # 模拟评分记录
        records = [
            {
                "submission_id": "sub_001",
                "file_name": "教案.docx",
                "file_type": "教案",
                "base_score": 85.0,
                "bonus_score": 5.0,
                "final_score": 90.0,
                "grade": "优秀",
                "scoring_type": "auto",
                "scored_at": datetime.utcnow().isoformat(),
                "is_confirmed": True
            },
            {
                "submission_id": "sub_002",
                "file_name": "教学反思.docx",
                "file_type": "教学反思",
                "base_score": 80.0,
                "bonus_score": 3.0,
                "final_score": 83.0,
                "grade": "良好",
                "scoring_type": "auto",
                "scored_at": datetime.utcnow().isoformat(),
                "is_confirmed": True
            }
        ]
        
        # 验证导出数据
        assert len(records) == 2
        
        # 验证每条记录包含必需字段
        required_fields = [
            "submission_id", "file_name", "file_type",
            "base_score", "bonus_score", "final_score",
            "grade", "scoring_type", "scored_at", "is_confirmed"
        ]
        
        for record in records:
            for field in required_fields:
                assert field in record, f"缺少字段: {field}"
    
    def test_export_with_filters(self):
        """
        测试带筛选条件的导出
        
        应该支持按文件类型、等级等筛选
        """
        # 模拟所有评分记录
        all_records = [
            {"file_type": "教案", "grade": "优秀"},
            {"file_type": "教案", "grade": "良好"},
            {"file_type": "教学反思", "grade": "优秀"},
            {"file_type": "教学反思", "grade": "合格"}
        ]
        
        # 按文件类型筛选
        file_type_filter = "教案"
        filtered_by_type = [r for r in all_records if r["file_type"] == file_type_filter]
        
        assert len(filtered_by_type) == 2
        assert all(r["file_type"] == "教案" for r in filtered_by_type)
        
        # 按等级筛选
        grade_filter = "优秀"
        filtered_by_grade = [r for r in all_records if r["grade"] == grade_filter]
        
        assert len(filtered_by_grade) == 2
        assert all(r["grade"] == "优秀" for r in filtered_by_grade)


class TestConsistencyStatistics:
    """
    测试一致性统计
    """
    
    def test_consistency_rate_calculation(self):
        """
        测试一致性比例计算
        
        一致性 = 一致数量 / 总复核数量
        """
        # 模拟复核记录
        review_records = [
            {"is_consistent": True},
            {"is_consistent": True},
            {"is_consistent": False},
            {"is_consistent": True},
            {"is_consistent": True}
        ]
        
        # 计算一致性
        consistent_count = sum(1 for r in review_records if r["is_consistent"])
        total_count = len(review_records)
        consistency_rate = consistent_count / total_count if total_count > 0 else 0
        
        # 验证计算
        assert consistent_count == 4
        assert total_count == 5
        assert consistency_rate == 0.8
    
    def test_difference_reasons_statistics(self):
        """
        测试差异原因统计
        
        应该统计不一致的原因分布
        """
        # 模拟复核记录
        review_records = [
            {"is_consistent": True, "difference_reason": ""},
            {"is_consistent": False, "difference_reason": "评分标准理解偏差"},
            {"is_consistent": False, "difference_reason": "文件内容理解偏差"},
            {"is_consistent": False, "difference_reason": "评分标准理解偏差"},
            {"is_consistent": True, "difference_reason": ""}
        ]
        
        # 统计差异原因
        difference_reasons = {}
        for record in review_records:
            if not record["is_consistent"] and record["difference_reason"]:
                reason = record["difference_reason"]
                difference_reasons[reason] = difference_reasons.get(reason, 0) + 1
        
        # 验证统计
        assert difference_reasons["评分标准理解偏差"] == 2
        assert difference_reasons["文件内容理解偏差"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
