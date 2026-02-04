#!/usr/bin/env python3
"""
DeepSeek自动评分系统功能演示脚本
展示完整的评教流程和核心功能
"""

import requests
import json
import time
from datetime import datetime
import os

class EvaluationSystemDemo:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.token = None
        self.demo_submissions = []
    
    def print_header(self, title):
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"🎯 {title}")
        print("=" * 60)
    
    def print_step(self, step, description):
        """打印步骤"""
        print(f"\n📋 步骤 {step}: {description}")
        print("-" * 40)
    
    def login_admin(self):
        """管理员登录"""
        self.print_step(1, "管理员登录")
        
        try:
            response = requests.post(f"{self.base_url}/api/login", json={
                "username": "admin",
                "password": "123456"
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token", {}).get("access_token")
                print("✅ 管理员登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def create_demo_materials(self):
        """创建演示用的教学材料"""
        self.print_step(2, "创建演示教学材料")
        
        # 创建不同质量的教学材料
        materials = {
            "优秀教案.txt": """
高等数学《导数的概念与计算》教学设计

一、教学目标
1. 知识目标：
   - 理解导数的定义和几何意义
   - 掌握基本函数的导数公式
   - 能够运用导数公式进行简单计算

2. 能力目标：
   - 培养学生的抽象思维能力和逻辑推理能力
   - 提高学生运用数学知识解决实际问题的能力
   - 增强学生的数学建模意识

3. 情感目标：
   - 激发学生对数学的兴趣和探究欲望
   - 培养学生严谨的学习态度和科学精神
   - 增强学生的团队合作意识

二、教学重点与难点
重点：导数的定义、几何意义和基本计算方法
难点：导数定义中极限概念的理解和应用

三、教学内容与过程
1. 导入环节（10分钟）
   - 通过实际问题（汽车速度变化）引入导数概念
   - 复习极限的相关知识

2. 新课讲授（70分钟）
   - 导数的定义及其几何意义
   - 基本函数的导数公式推导
   - 导数的运算法则
   - 典型例题分析和练习

3. 巩固练习（15分钟）
   - 课堂练习题
   - 学生互动讨论

4. 课堂小结（5分钟）
   - 知识点梳理
   - 布置课后作业

四、教学方法
采用问题驱动、启发式教学、多媒体辅助等方法，
注重理论与实践相结合，培养学生的创新思维。

五、教学评价
通过课堂提问、练习反馈、作业检查等多种方式
进行过程性评价，及时了解学生掌握情况。
            """,
            
            "简单教案.txt": """
数学课教案

教学目标：学会导数
教学内容：导数的定义和计算
教学方法：讲授法
教学过程：讲解导数概念，做练习题
            """,
            
            "详细教学反思.txt": """
《导数的概念与计算》教学反思

一、教学目标达成情况分析
本次课程的教学目标达成情况如下：
1. 知识目标达成度：90%
   - 学生对导数概念的理解：通过课堂提问，85%的学生能够准确描述导数的定义
   - 几何意义掌握：80%的学生能够正确解释导数的几何意义
   - 计算能力：基础计算题正确率达95%

2. 能力目标达成度：75%
   - 抽象思维能力有所提升，但仍需加强训练
   - 问题解决能力在实际应用中还有待提高

3. 情感目标达成度：85%
   - 学生参与度高，课堂氛围活跃
   - 对数学的兴趣明显增强

二、教学重难点处理效果反思
1. 重点处理效果良好
   - 导数定义通过实际问题引入，学生理解较好
   - 基本公式推导过程清晰，学生跟进顺利

2. 难点突破有待改进
   - 极限概念的理解仍是学生的薄弱环节
   - 需要增加更多直观的几何解释

三、教学方法效果评价
1. 问题驱动法效果显著，激发了学生的思考
2. 多媒体辅助直观有效，但使用时间需要控制
3. 互动讨论环节活跃，但时间分配需要优化

四、存在的问题及改进措施
问题：
1. 部分学生对抽象概念理解困难
2. 练习时间不够充分
3. 个别学生参与度不高

改进措施：
1. 增加具体实例，降低抽象程度
2. 合理分配时间，确保充足的练习
3. 关注个体差异，采用分层教学

五、理论反思
基于建构主义学习理论，学生需要在已有知识基础上
主动构建新知识。今后教学中要更好地发挥学生的
主体作用，提供更多的探究机会。
            """
        }
        
        # 确保目录存在
        upload_dir = "评教系统最终版/评教系统教师端/backend/uploads/submissions/teacher_001"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 创建文件
        for filename, content in materials.items():
            filepath = os.path.join(upload_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 创建材料: {filename}")
        
        print(f"✅ 共创建 {len(materials)} 个演示材料")
    
    def submit_demo_materials(self):
        """提交演示材料"""
        self.print_step(3, "提交演示材料")
        
        materials = [
            {
                "name": "优秀教案.txt",
                "teacher": "张教授",
                "type": "教案"
            },
            {
                "name": "简单教案.txt", 
                "teacher": "李老师",
                "type": "教案"
            },
            {
                "name": "详细教学反思.txt",
                "teacher": "王教授", 
                "type": "教学反思"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        for i, material in enumerate(materials):
            try:
                submission_data = {
                    "submission_id": f"demo_{int(datetime.now().timestamp())}_{i}",
                    "teacher_id": f"teacher_{i+1:03d}",
                    "teacher_name": material["teacher"],
                    "files": [
                        {
                            "file_id": f"demo_file_{i}",
                            "file_name": material["name"],
                            "file_size": 1000,
                            "file_url": f"uploads/submissions/teacher_001/{material['name']}"
                        }
                    ],
                    "notes": f"演示提交 - {material['type']}",
                    "submitted_at": datetime.now().isoformat()
                }
                
                response = requests.post(
                    f"{self.base_url}/api/teacher/sync-submission",
                    headers=headers,
                    json=submission_data,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ {material['teacher']} 提交 {material['name']} 成功")
                    self.demo_submissions.append(submission_data["submission_id"])
                else:
                    print(f"❌ 提交失败: {response.text}")
                    
            except Exception as e:
                print(f"❌ 提交异常: {e}")
        
        print(f"✅ 共提交 {len(self.demo_submissions)} 个材料")
    
    def demonstrate_single_scoring(self):
        """演示单个评分功能"""
        self.print_step(4, "单个材料自动评分演示")
        
        if not self.demo_submissions:
            print("❌ 没有可评分的提交")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        for i, submission_id in enumerate(self.demo_submissions):
            print(f"\n🔍 正在评分第 {i+1} 个提交: {submission_id}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/scoring/score/{submission_id}",
                    headers=headers,
                    json=[],
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        result = data.get("scoring_result", {})
                        
                        print(f"  ✅ 评分成功!")
                        print(f"  📊 最终得分: {result.get('final_score', 0)}分")
                        print(f"  📈 评定等级: {result.get('grade', '')}")
                        print(f"  ⚠️  触发否决: {result.get('veto_triggered', False)}")
                        
                        if result.get('veto_triggered'):
                            print(f"  🚫 否决原因: {result.get('veto_reason', '')[:100]}...")
                        else:
                            score_details = result.get('score_details', [])
                            if score_details:
                                print("  📋 详细评分:")
                                for detail in score_details:
                                    indicator = detail.get('indicator', '')
                                    score = detail.get('score', 0)
                                    max_score = detail.get('max_score', 0)
                                    print(f"    • {indicator}: {score}/{max_score}分")
                    else:
                        print(f"  ❌ 评分失败")
                else:
                    print(f"  ❌ 评分请求失败: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ 评分异常: {e}")
            
            # 添加延迟，避免API调用过快
            time.sleep(2)
    
    def demonstrate_batch_scoring(self):
        """演示批量评分功能"""
        self.print_step(5, "批量评分功能演示")
        
        if len(self.demo_submissions) < 2:
            print("❌ 提交数量不足，无法演示批量评分")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"🔄 开始批量评分 {len(self.demo_submissions)} 个提交...")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/scoring/batch-score",
                headers=headers,
                json=self.demo_submissions,
                timeout=180  # 批量评分需要更长时间
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                success_count = data.get("success", 0)
                failed_count = data.get("failed", 0)
                
                print("🎉 批量评分完成!")
                print(f"  📊 总数: {total}")
                print(f"  ✅ 成功: {success_count}")
                print(f"  ❌ 失败: {failed_count}")
                print(f"  📈 成功率: {success_count/total*100:.1f}%")
                
                results = data.get("results", [])
                print("\n📋 批量评分详细结果:")
                for i, result in enumerate(results):
                    submission_id = result.get("submission_id", "")
                    success = result.get("success", False)
                    
                    if success:
                        scoring_result = result.get("scoring_result", {})
                        final_score = scoring_result.get("final_score", 0)
                        grade = scoring_result.get("grade", "")
                        print(f"  {i+1}. ✅ {submission_id[:20]}... → {final_score}分 ({grade})")
                    else:
                        error = result.get("error", "")
                        print(f"  {i+1}. ❌ {submission_id[:20]}... → 失败: {error[:50]}...")
            else:
                print(f"❌ 批量评分失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 批量评分异常: {e}")
    
    def show_system_statistics(self):
        """显示系统统计信息"""
        self.print_step(6, "系统统计信息")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # 获取提交统计
            response = requests.get(
                f"{self.base_url}/api/materials/submissions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                
                # 统计各种状态的数量
                status_count = {}
                for sub in submissions:
                    status = sub.get("review_status", "unknown")
                    status_count[status] = status_count.get(status, 0) + 1
                
                print("📊 提交材料统计:")
                print(f"  📝 总提交数: {len(submissions)}")
                for status, count in status_count.items():
                    print(f"  📋 {status}: {count}")
                
                # 显示最近的提交
                print("\n📅 最近提交:")
                for sub in submissions[:5]:
                    teacher = sub.get("teacher_name", "")
                    status = sub.get("review_status", "")
                    time_str = sub.get("submission_time", "")[:19]
                    print(f"  • {teacher} - {status} - {time_str}")
                    
            else:
                print(f"❌ 获取统计信息失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 获取统计信息异常: {e}")
    
    def run_demo(self):
        """运行完整演示"""
        self.print_header("DeepSeek自动评分系统功能演示")
        
        print("🎯 本演示将展示以下功能:")
        print("  1. 管理员登录")
        print("  2. 创建演示教学材料")
        print("  3. 提交材料到系统")
        print("  4. 单个材料自动评分")
        print("  5. 批量评分功能")
        print("  6. 系统统计信息")
        
        # 执行演示步骤
        if not self.login_admin():
            print("❌ 演示终止：登录失败")
            return
        
        self.create_demo_materials()
        self.submit_demo_materials()
        self.demonstrate_single_scoring()
        self.demonstrate_batch_scoring()
        self.show_system_statistics()
        
        # 演示总结
        self.print_header("演示总结")
        print("🎉 DeepSeek自动评分系统功能演示完成!")
        print("\n✨ 系统核心优势:")
        print("  🤖 AI智能评分 - 基于DeepSeek大语言模型")
        print("  📊 多维度评价 - 全面专业的评分标准")
        print("  ⚡ 高效处理 - 支持单个和批量评分")
        print("  🎯 精准反馈 - 详细的评分理由和改进建议")
        print("  🔍 质量把控 - 一票否决机制确保评分质量")
        
        print("\n📈 应用价值:")
        print("  • 大幅提升评教工作效率")
        print("  • 确保评分标准的一致性和公正性")
        print("  • 为教师提供专业的改进指导")
        print("  • 支持大规模教学质量评估")
        
        print("\n🚀 系统已准备就绪，可以开始正式使用!")

def main():
    """主函数"""
    demo = EvaluationSystemDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()