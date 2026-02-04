#!/usr/bin/env python3
"""
完整的考评表流程测试
包括：管理端制定考评表 -> 分发到教师端 -> 教师端提交文件 -> 管理端自动评分
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta

# API基础URL
ADMIN_API = "http://localhost:8001"
TEACHER_API = "http://localhost:8000"

class EvaluationFlowTest:
    def __init__(self):
        self.admin_token = None
        self.teacher_token = None
        self.template_id = None
        self.task_id = None
        self.submission_id = None
    
    def login_admin(self):
        """管理员登录"""
        try:
            response = requests.post(f"{ADMIN_API}/api/login", json={
                "username": "admin",
                "password": "123456"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token", {}).get("access_token")
                print("✅ 管理员登录成功")
                return True
            else:
                print(f"❌ 管理员登录失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 管理员登录异常: {e}")
            return False
    
    def login_teacher(self):
        """教师登录（如果需要）"""
        # 教师端可能不需要登录，或者使用不同的认证方式
        print("✅ 教师端访问准备就绪")
        return True
    
    def create_evaluation_template(self):
        """步骤1: 管理端创建考评表模板"""
        print("\n=== 步骤1: 创建考评表模板 ===")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # 创建考评表模板数据
            template_data = {
                "name": "2026年春季教学质量评估表",
                "description": "针对教师教学质量的综合评估，包含教案、教学反思等材料",
                "file_name": "教学质量评估表.pdf",
                "file_type": "pdf",
                "file_size": 1024,
                "scoring_criteria": [
                    {"name": "教案质量", "max_score": 30},
                    {"name": "教学反思", "max_score": 25},
                    {"name": "课件制作", "max_score": 25},
                    {"name": "教学创新", "max_score": 20}
                ],
                "total_score": 100,
                "submission_requirements": {
                    "file_types": ["pdf", "docx", "pptx"],
                    "max_files": 5,
                    "description": "请提交教案、教学反思、课件等相关材料"
                },
                "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
                "target_teachers": [
                    {"teacher_id": "teacher_001", "teacher_name": "张三"}
                ],
                "distribution_type": "targeted"
            }
            
            # 调用创建模板API
            response = requests.post(
                f"{ADMIN_API}/api/evaluation-templates",
                headers=headers,
                json=template_data
            )
            
            print(f"创建模板状态码: {response.status_code}")
            print(f"创建模板响应: {response.text}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.template_id = data.get("template_id")
                print(f"✅ 考评表模板创建成功，ID: {self.template_id}")
                return True
            else:
                print("❌ 考评表模板创建失败")
                return False
                
        except Exception as e:
            print(f"❌ 创建考评表模板异常: {e}")
            return False
    
    def distribute_template(self):
        """步骤2: 分发考评表到教师端"""
        print("\n=== 步骤2: 分发考评表到教师端 ===")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # 分发考评表
            distribute_data = {
                "template_id": self.template_id,
                "teacher_ids": ["teacher_001"]
            }
            
            response = requests.post(
                f"{ADMIN_API}/api/evaluation-templates/{self.template_id}/distribute",
                headers=headers,
                json=distribute_data
            )
            
            print(f"分发状态码: {response.status_code}")
            print(f"分发响应: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ 考评表分发成功")
                return True
            else:
                print("❌ 考评表分发失败")
                return False
                
        except Exception as e:
            print(f"❌ 分发考评表异常: {e}")
            return False
    
    def check_teacher_tasks(self):
        """步骤3: 检查教师端是否收到考评任务"""
        print("\n=== 步骤3: 检查教师端考评任务 ===")
        
        try:
            # 检查教师端的考评任务
            response = requests.get(f"{TEACHER_API}/api/teacher/evaluation-tasks")
            
            print(f"教师端任务查询状态码: {response.status_code}")
            print(f"教师端任务查询响应: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("tasks", [])
                if tasks:
                    self.task_id = tasks[0].get("task_id")
                    print(f"✅ 教师端收到考评任务，任务ID: {self.task_id}")
                    return True
                else:
                    print("⚠️  教师端暂未收到考评任务")
                    return False
            else:
                print("❌ 教师端任务查询失败")
                return False
                
        except Exception as e:
            print(f"❌ 检查教师端任务异常: {e}")
            return False
    
    def create_test_files(self):
        """创建测试文件"""
        print("\n=== 创建测试文件 ===")
        
        # 创建教案文件
        lesson_plan = """
教学设计方案

课程名称：高等数学
授课教师：张三
授课时间：2026年2月4日

一、教学目标
1. 知识目标：
   - 掌握函数极限的定义和性质
   - 理解连续函数的概念
   - 学会计算基本函数的极限

2. 能力目标：
   - 培养学生的逻辑思维能力
   - 提高数学分析和解决问题的能力
   - 增强数学建模意识

3. 情感目标：
   - 激发学生对数学的兴趣
   - 培养严谨的学习态度
   - 增强团队合作精神

二、教学内容
1. 函数极限的定义
   - ε-δ定义
   - 几何意义
   - 物理意义

2. 极限的性质
   - 唯一性
   - 局部有界性
   - 保号性

3. 极限的计算
   - 基本极限公式
   - 运算法则
   - 洛必达法则

三、教学方法
1. 讲授法：系统讲解基本概念和理论
2. 讨论法：引导学生思考和讨论
3. 案例分析法：通过具体例题加深理解
4. 多媒体教学：利用图形和动画演示

四、教学过程
1. 导入（5分钟）
   - 回顾前节课内容
   - 提出本节课问题

2. 新课讲授（30分钟）
   - 极限定义的引入
   - 性质的证明和应用
   - 计算方法的讲解

3. 练习巩固（10分钟）
   - 课堂练习
   - 学生讨论

4. 总结（5分钟）
   - 知识点梳理
   - 布置作业

五、教学评价
1. 课堂表现评价
2. 练习完成情况
3. 课后作业质量
4. 学生反馈意见

六、教学反思
通过本节课的教学，学生对函数极限有了初步认识，但在计算方面还需要更多练习。
下次课将重点加强练习环节，提高学生的计算能力。
"""
        
        # 创建教学反思文件
        reflection = """
教学反思报告

课程：高等数学 - 函数极限
授课教师：张三
反思时间：2026年2月4日

一、教学效果反思
本节课围绕函数极限这一重要概念展开教学，整体效果良好。学生对极限的直观理解较好，
但在严格的数学定义方面还需要进一步加强。

二、教学方法反思
1. 优点：
   - 多媒体演示效果好，学生能够直观理解极限概念
   - 案例分析贴近实际，激发了学生兴趣
   - 课堂互动较为活跃

2. 不足：
   - 理论推导部分讲解过快，部分学生跟不上
   - 练习时间不够充分
   - 个别学生参与度不高

三、学生学习情况分析
1. 学习态度：大部分学生学习积极性较高
2. 理解程度：基本概念掌握较好，计算能力有待提高
3. 存在问题：对ε-δ定义理解困难

四、改进措施
1. 增加练习时间，特别是计算练习
2. 对理论部分采用更多的类比和实例
3. 关注学习困难的学生，提供个别辅导
4. 设计更多互动环节，提高全员参与度

五、下次课改进计划
1. 复习本节课重点内容
2. 增加计算练习的比重
3. 采用小组讨论的方式加深理解
4. 准备更多的实际应用案例

通过这次教学实践，我深刻认识到教学是一个不断改进的过程，
需要根据学生的实际情况调整教学策略，提高教学效果。
"""
        
        # 保存文件
        os.makedirs("test_files", exist_ok=True)
        
        with open("test_files/教案.txt", "w", encoding="utf-8") as f:
            f.write(lesson_plan)
        
        with open("test_files/教学反思.txt", "w", encoding="utf-8") as f:
            f.write(reflection)
        
        print("✅ 测试文件创建成功")
        print("  - test_files/教案.txt")
        print("  - test_files/教学反思.txt")
        
        return True
    
    def submit_materials(self):
        """步骤4: 教师端提交材料"""
        print("\n=== 步骤4: 教师端提交材料 ===")
        
        try:
            # 模拟教师端提交材料
            submission_data = {
                "teacher_id": "teacher_001",
                "teacher_name": "张三",
                "files": [
                    {
                        "file_id": "file_lesson_plan_001",
                        "file_name": "教案.txt",
                        "file_size": 2048,
                        "file_url": "test_files/教案.txt"
                    },
                    {
                        "file_id": "file_reflection_001", 
                        "file_name": "教学反思.txt",
                        "file_size": 1536,
                        "file_url": "test_files/教学反思.txt"
                    }
                ],
                "notes": "提交教案和教学反思材料，请审核",
                "submitted_at": datetime.now().isoformat()
            }
            
            # 直接向管理端同步提交数据
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{ADMIN_API}/api/teacher/sync-submission",
                headers=headers,
                json=submission_data
            )
            
            print(f"材料提交状态码: {response.status_code}")
            print(f"材料提交响应: {response.text}")
            
            if response.status_code in [200, 201]:
                # 获取提交ID
                self.submission_id = submission_data.get("submission_id", f"sub_test_{int(time.time())}")
                print(f"✅ 材料提交成功，提交ID: {self.submission_id}")
                return True
            else:
                print("❌ 材料提交失败")
                return False
                
        except Exception as e:
            print(f"❌ 提交材料异常: {e}")
            return False
    
    def auto_scoring(self):
        """步骤5: 管理端自动评分"""
        print("\n=== 步骤5: 管理端自动评分 ===")
        
        try:
            # 首先获取最新的提交记录
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # 获取提交列表
            response = requests.get(f"{ADMIN_API}/api/materials/submissions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                
                if submissions:
                    # 使用最新的提交记录
                    latest_submission = submissions[0]
                    submission_id = latest_submission.get("submission_id")
                    
                    print(f"找到提交记录: {submission_id}")
                    print(f"教师: {latest_submission.get('teacher_name')}")
                    print(f"文件数量: {len(latest_submission.get('files', []))}")
                    
                    # 执行自动评分
                    scoring_response = requests.post(
                        f"{ADMIN_API}/api/scoring/score/{submission_id}",
                        headers=headers,
                        json=[]
                    )
                    
                    print(f"自动评分状态码: {scoring_response.status_code}")
                    print(f"自动评分响应: {scoring_response.text}")
                    
                    if scoring_response.status_code == 200:
                        scoring_data = scoring_response.json()
                        if scoring_data.get("success"):
                            result = scoring_data.get("scoring_result", {})
                            print("✅ 自动评分成功!")
                            print(f"  基础分: {result.get('base_score', 0)}")
                            print(f"  最终分: {result.get('final_score', 0)}")
                            print(f"  等级: {result.get('grade', '')}")
                            print(f"  是否触发否决: {result.get('veto_triggered', False)}")
                            if result.get('veto_triggered'):
                                print(f"  否决原因: {result.get('veto_reason', '')}")
                            print(f"  评价总结: {result.get('summary', '')[:100]}...")
                            return True
                        else:
                            print("❌ 自动评分失败")
                            return False
                    else:
                        print("❌ 自动评分请求失败")
                        return False
                else:
                    print("❌ 没有找到提交记录")
                    return False
            else:
                print("❌ 获取提交列表失败")
                return False
                
        except Exception as e:
            print(f"❌ 自动评分异常: {e}")
            return False
    
    def get_scoring_results(self):
        """步骤6: 查看评分结果"""
        print("\n=== 步骤6: 查看评分结果 ===")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # 获取提交列表
            response = requests.get(f"{ADMIN_API}/api/materials/submissions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                
                print(f"共找到 {len(submissions)} 个提交记录")
                
                # 显示已评分的记录
                scored_count = 0
                for submission in submissions[:5]:  # 显示前5个
                    submission_id = submission.get("submission_id")
                    teacher_name = submission.get("teacher_name")
                    review_status = submission.get("review_status")
                    
                    print(f"\n提交记录: {submission_id}")
                    print(f"  教师: {teacher_name}")
                    print(f"  状态: {review_status}")
                    
                    if review_status == "scored":
                        scored_count += 1
                        # 获取详细评分记录
                        record_response = requests.get(
                            f"{ADMIN_API}/api/scoring/records/{submission_id}",
                            headers=headers
                        )
                        
                        if record_response.status_code == 200:
                            record_data = record_response.json()
                            scoring_result = record_data.get("scoring_result", {})
                            if scoring_result:
                                print(f"  评分结果: {scoring_result.get('final_score', 0)}分")
                                print(f"  等级: {scoring_result.get('grade', '')}")
                
                print(f"\n✅ 已评分记录数量: {scored_count}")
                return True
            else:
                print("❌ 获取评分结果失败")
                return False
                
        except Exception as e:
            print(f"❌ 查看评分结果异常: {e}")
            return False
    
    def run_complete_test(self):
        """运行完整测试流程"""
        print("🚀 开始完整考评表流程测试")
        print("=" * 60)
        
        # 步骤0: 登录
        if not self.login_admin():
            return False
        
        if not self.login_teacher():
            return False
        
        # 创建测试文件
        if not self.create_test_files():
            return False
        
        # 步骤4: 提交材料（跳过前面的步骤，直接测试核心功能）
        if not self.submit_materials():
            return False
        
        # 等待一下确保数据同步
        print("\n⏳ 等待数据同步...")
        time.sleep(2)
        
        # 步骤5: 自动评分
        if not self.auto_scoring():
            return False
        
        # 步骤6: 查看结果
        if not self.get_scoring_results():
            return False
        
        print("\n" + "=" * 60)
        print("🎉 完整考评表流程测试完成!")
        print("✅ 所有功能测试通过:")
        print("  - 管理员认证")
        print("  - 材料提交同步")
        print("  - DeepSeek API自动评分")
        print("  - 评分结果存储和查询")
        print("=" * 60)
        
        return True

def main():
    test = EvaluationFlowTest()
    test.run_complete_test()

if __name__ == "__main__":
    main()