#!/usr/bin/env python3
"""
测试批量评分功能
"""

import requests
import json
from datetime import datetime

def test_batch_scoring():
    """测试批量评分功能"""
    print("🚀 开始测试批量评分功能")
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
    
    # 2. 获取所有提交记录
    print("\n2. 获取提交记录列表...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "http://localhost:8001/api/materials/submissions",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            submissions = data.get("submissions", [])
            print(f"✅ 获取到 {len(submissions)} 个提交记录")
            
            # 显示提交记录
            for i, sub in enumerate(submissions[:5]):  # 只显示前5个
                print(f"  {i+1}. {sub['submission_id']} - {sub['teacher_name']} - {sub['review_status']}")
            
            if len(submissions) == 0:
                print("❌ 没有找到提交记录")
                return False
                
        else:
            print(f"❌ 获取提交记录失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取提交记录异常: {e}")
        return False
    
    # 3. 选择前几个提交进行批量评分
    print("\n3. 执行批量评分...")
    try:
        # 选择前3个提交记录进行批量评分
        submission_ids = [sub["submission_id"] for sub in submissions[:3]]
        print(f"选择评分的提交ID: {submission_ids}")
        
        response = requests.post(
            "http://localhost:8001/api/scoring/batch-score",
            headers=headers,
            json=submission_ids,
            timeout=120  # 批量评分需要更长时间
        )
        
        print(f"批量评分状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total", 0)
            success_count = data.get("success", 0)
            failed_count = data.get("failed", 0)
            results = data.get("results", [])
            
            print("🎉 批量评分完成!")
            print(f"  📊 总数: {total}")
            print(f"  ✅ 成功: {success_count}")
            print(f"  ❌ 失败: {failed_count}")
            
            print("\n  📋 详细结果:")
            for i, result in enumerate(results):
                submission_id = result.get("submission_id", "")
                success = result.get("success", False)
                
                if success:
                    scoring_result = result.get("scoring_result", {})
                    final_score = scoring_result.get("final_score", 0)
                    grade = scoring_result.get("grade", "")
                    veto_triggered = scoring_result.get("veto_triggered", False)
                    
                    print(f"    {i+1}. {submission_id[:20]}...")
                    print(f"       ✅ 评分成功: {final_score}分 ({grade})")
                    if veto_triggered:
                        print(f"       ⚠️ 触发否决: {scoring_result.get('veto_reason', '')[:50]}...")
                else:
                    error = result.get("error", "")
                    print(f"    {i+1}. {submission_id[:20]}...")
                    print(f"       ❌ 评分失败: {error}")
            
            return success_count > 0
        else:
            error_text = response.text
            print(f"❌ 批量评分失败: {error_text}")
            return False
    except Exception as e:
        print(f"❌ 批量评分异常: {e}")
        return False

if __name__ == "__main__":
    print("测试DeepSeek API批量评分功能")
    print("=" * 60)
    
    success = test_batch_scoring()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 批量评分测试通过!")
        print("🎯 DeepSeek API批量评分功能正常工作")
    else:
        print("❌ 批量评分测试失败")
    print("=" * 60)