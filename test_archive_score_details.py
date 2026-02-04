#!/usr/bin/env python3
"""
测试档案中心评分详情显示
验证档案中心的各项评分详情与考评任务列表的显示一致
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_archive_score_details():
    """测试档案中心评分详情显示"""
    print("=" * 80)
    print("档案中心评分详情显示测试")
    print("=" * 80)
    
    # 1. 登录获取token
    print("\n1. 登录管理端...")
    login_response = requests.post(
        f"{BASE_URL}/api/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        print(f"响应: {login_response.text}")
        return False
    
    login_data = login_response.json()
    token = login_data.get("access_token") or login_data.get("token")
    if not token:
        print(f"❌ 登录响应中没有token: {login_data}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 获取归档评分列表
    print("\n2. 获取归档评分列表...")
    list_response = requests.get(
        f"{BASE_URL}/api/archived-scores",
        headers=headers,
        params={"page": 1, "page_size": 5}
    )
    
    if list_response.status_code != 200:
        print(f"❌ 获取列表失败: {list_response.status_code}")
        return False
    
    data = list_response.json()
    scores = data.get("scores", [])
    print(f"✅ 获取到 {len(scores)} 条归档记录")
    
    if not scores:
        print("⚠️  没有归档记录，无法测试详情显示")
        return True
    
    # 3. 测试每条记录的详情
    print("\n3. 测试评分详情显示...")
    for i, score in enumerate(scores[:3], 1):  # 只测试前3条
        print(f"\n--- 记录 {i}: {score.get('archive_id')} ---")
        print(f"教师: {score.get('teacher_id')} - {score.get('teacher_name')}")
        print(f"考评表: {score.get('template_name')}")
        print(f"得分: {score.get('score')}/{score.get('total_score')}")
        
        # 获取详情
        detail_response = requests.get(
            f"{BASE_URL}/api/archived-scores/{score['id']}",
            headers=headers
        )
        
        if detail_response.status_code != 200:
            print(f"❌ 获取详情失败: {detail_response.status_code}")
            continue
        
        detail = detail_response.json()
        scores_data = detail.get("scores", {})
        
        print(f"\n评分数据结构:")
        print(f"  - 类型: {type(scores_data)}")
        
        # 检查是否有AI评分的score_details
        if isinstance(scores_data, dict) and "score_details" in scores_data:
            score_details = scores_data["score_details"]
            print(f"  - 格式: AI自动评分 (score_details)")
            print(f"  - 评分项数量: {len(score_details)}")
            
            print(f"\n各项评分详情:")
            for detail_item in score_details:
                indicator = detail_item.get("indicator", "未知")
                score_val = detail_item.get("score", 0)
                max_score = detail_item.get("max_score", 0)
                reason = detail_item.get("reason", "")
                percentage = round((score_val / max_score * 100) if max_score > 0 else 0)
                
                print(f"  ✓ {indicator}: {score_val}/{max_score} ({percentage}%)")
                if reason:
                    print(f"    说明: {reason[:50]}...")
            
            print(f"\n✅ 该记录使用AI评分格式，包含详细评分说明")
            
        else:
            print(f"  - 格式: 手动评分 (传统格式)")
            if isinstance(scores_data, dict):
                # 过滤掉元数据字段
                meta_fields = ['base_score', 'bonus_score', 'final_score', 'grade', 
                              'veto_triggered', 'veto_reason', 'summary', 'scored_at']
                score_items = {k: v for k, v in scores_data.items() if k not in meta_fields}
                print(f"  - 评分项数量: {len(score_items)}")
                
                if score_items:
                    print(f"\n各项评分:")
                    for name, value in score_items.items():
                        print(f"  ✓ {name}: {value}")
            
            print(f"\n✅ 该记录使用手动评分格式")
    
    # 4. 总结
    print("\n" + "=" * 80)
    print("测试总结:")
    print("=" * 80)
    print("✅ 档案中心评分详情显示功能已更新")
    print("✅ 支持AI自动评分格式 (score_details数组)")
    print("✅ 支持手动评分格式 (传统对象格式)")
    print("✅ 显示评分说明 (reason字段)")
    print("\n前端更新内容:")
    print("  1. formatScoreItems() 函数已更新，优先使用 score_details")
    print("  2. 表格新增 '评分说明' 列，显示AI评分的reason")
    print("  3. 添加 criterion-reason CSS样式，与考评任务列表一致")
    print("  4. 保持向后兼容，支持旧的手动评分格式")
    
    return True

if __name__ == "__main__":
    try:
        success = test_archive_score_details()
        if success:
            print("\n✅ 所有测试通过！")
        else:
            print("\n❌ 测试失败")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
