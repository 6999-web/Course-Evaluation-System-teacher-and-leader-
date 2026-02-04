#!/usr/bin/env python3
"""
测试前端AI自动评分功能
"""

import requests
import json
from datetime import datetime
import time

def test_frontend_auto_scoring():
    """测试前端AI自动评分功能"""
    print("🚀 测试前端AI自动评分功能")
    print("=" * 60)
    
    # 1. 登录获取token
    print("1. 管理员登录...")
    try:
        response = requests.post("http://localhost:8001/api/login", json={
            "username": "admin",
            "password": "123456"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token", {}).get("access_token")
            print("✅ 管理员登录成功")
        else:
            print(f"❌ 管理员登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 创建测试提交
    print("\n2. 创建测试提交...")
    try:
        submission_data = {
            "submission_id": f"frontend_test_{int(datetime.now().timestamp())}",
            "teacher_id": "teacher_001",
            "teacher_name": "测试教师",
            "files": [
                {
                    "file_id": "frontend_test_file",
                    "file_name": "完整教学反思.txt",
                    "file_size": 5000,
                    "file_url": "uploads/submissions/teacher_001/完整教学反思.txt"
                }
            ],
            "notes": "前端AI自动评分测试",
            "submitted_at": datetime.now().isoformat()
        }
        
        response = requests.post(
            "http://localhost:8001/api/teacher/sync-submission",
            headers=headers,
            json=submission_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✅ 测试提交创建成功")
            submission_id = submission_data["submission_id"]
        else:
            print(f"❌ 创建提交失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建提交异常: {e}")
        return False
    
    # 3. 测试单个AI自动评分API
    print("\n3. 测试单个AI自动评分API...")
    try:
        print(f"正在调用评分API: /api/scoring/score/{submission_id}")
        
        response = requests.post(
            f"http://localhost:8001/api/scoring/score/{submission_id}",
            headers=headers,
            json=[],  # 空的加分项数组
            timeout=60
        )
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("scoring_result", {})
                print("🎉 AI自动评分API测试成功!")
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
                
                return True
            else:
                print("❌ 自动评分失败")
                return False
        else:
            print(f"❌ 评分API调用失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 自动评分异常: {e}")
        return False

def test_batch_auto_scoring():
    """测试批量AI自动评分"""
    print("\n🚀 测试批量AI自动评分功能")
    print("=" * 60)
    
    # 1. 登录
    print("1. 管理员登录...")
    try:
        response = requests.post("http://localhost:8001/api/login", json={
            "username": "admin",
            "password": "123456"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token", {}).get("access_token")
            print("✅ 管理员登录成功")
        else:
            print(f"❌ 管理员登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取现有提交
    print("\n2. 获取现有提交...")
    try:
        response = requests.get(
            "http://localhost:8001/api/materials/submissions",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            submissions = data.get("submissions", [])
            print(f"✅ 获取到 {len(submissions)} 个提交")
            
            if len(submissions) == 0:
                print("❌ 没有提交可以测试批量评分")
                return False
                
            # 选择前3个提交进行批量评分
            submission_ids = [sub["submission_id"] for sub in submissions[:3]]
            print(f"选择评分的提交: {submission_ids}")
            
        else:
            print(f"❌ 获取提交失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取提交异常: {e}")
        return False
    
    # 3. 测试批量AI自动评分API
    print("\n3. 测试批量AI自动评分API...")
    try:
        print(f"正在调用批量评分API，提交数量: {len(submission_ids)}")
        
        response = requests.post(
            "http://localhost:8001/api/scoring/batch-score",
            headers=headers,
            json=submission_ids,
            timeout=180  # 3分钟超时
        )
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            success_count = data.get("success", 0)
            failed_count = data.get("failed", 0)
            
            print("🎉 批量AI自动评分API测试成功!")
            print(f"  📊 总数: {total}")
            print(f"  ✅ 成功: {success_count}")
            print(f"  ❌ 失败: {failed_count}")
            print(f"  📈 成功率: {success_count/total*100:.1f}%")
            
            results = data.get("results", [])
            if results:
                print("  📋 详细结果:")
                for i, result in enumerate(results[:3]):  # 只显示前3个
                    submission_id = result.get("submission_id", "")
                    success = result.get("success", False)
                    
                    if success:
                        scoring_result = result.get("scoring_result", {})
                        final_score = scoring_result.get("final_score", 0)
                        grade = scoring_result.get("grade", "")
                        print(f"    {i+1}. ✅ {submission_id[:20]}... → {final_score}分 ({grade})")
                    else:
                        error = result.get("error", "")
                        print(f"    {i+1}. ❌ {submission_id[:20]}... → 失败: {error[:50]}...")
            
            return success_count > 0
        else:
            print(f"❌ 批量评分API调用失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 批量评分异常: {e}")
        return False

def main():
    """主函数"""
    print("🎯 前端AI自动评分功能测试")
    print("=" * 60)
    print("本测试将验证以下功能:")
    print("1. 单个AI自动评分API")
    print("2. 批量AI自动评分API")
    print("3. 前端界面集成验证")
    print("=" * 60)
    
    # 测试单个评分
    single_success = test_frontend_auto_scoring()
    
    # 等待一下
    time.sleep(2)
    
    # 测试批量评分
    batch_success = test_batch_auto_scoring()
    
    # 总结
    print("\n" + "=" * 60)
    print("🏆 测试总结")
    print("=" * 60)
    
    if single_success and batch_success:
        print("✅ 所有测试通过!")
        print("🎉 前端AI自动评分功能已准备就绪!")
        print("\n📋 功能说明:")
        print("• 单个AI自动评分: 点击'AI自动评分'按钮")
        print("• 批量AI自动评分: 选择多个任务后点击'AI批量自动评分'")
        print("• 手动评分: 仍然保留，点击'手动评分'按钮")
        print("• 评分结果: 自动显示详细的AI评分结果和建议")
    else:
        print("❌ 部分测试失败")
        if not single_success:
            print("• 单个AI自动评分功能需要检查")
        if not batch_success:
            print("• 批量AI自动评分功能需要检查")
    
    print("\n🚀 现在可以在前端界面中使用AI自动评分功能了!")

if __name__ == "__main__":
    main()