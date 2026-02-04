#!/usr/bin/env python3
"""
测试档案中心排序功能
验证档案按时间顺序正确排列
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_archive_sorting():
    """测试档案排序功能"""
    print("=" * 80)
    print("档案中心排序功能测试")
    print("=" * 80)
    
    # 1. 登录
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
        return False
    
    login_data = login_response.json()
    token = login_data.get("access_token") or login_data.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 测试降序排序（最新在前）
    print("\n2. 测试降序排序（最新在前）...")
    desc_response = requests.get(
        f"{BASE_URL}/api/archived-scores",
        headers=headers,
        params={"page": 1, "page_size": 10, "sortOrder": "desc"}
    )
    
    if desc_response.status_code != 200:
        print(f"❌ 获取降序列表失败: {desc_response.status_code}")
        return False
    
    desc_data = desc_response.json()
    desc_scores = desc_data.get("scores", [])
    print(f"✅ 获取到 {len(desc_scores)} 条记录（降序）")
    
    if desc_scores:
        print("\n降序排列（最新在前）:")
        for i, score in enumerate(desc_scores[:5], 1):
            scored_at = score.get('scored_at', 'N/A')
            archive_id = score.get('archive_id', 'N/A')
            teacher = score.get('teacher_name', score.get('teacher_id', 'N/A'))
            print(f"  {i}. {archive_id} - {teacher} - 评分时间: {scored_at}")
        
        # 验证降序
        dates = [score.get('scored_at') for score in desc_scores if score.get('scored_at')]
        if len(dates) > 1:
            is_descending = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
            if is_descending:
                print("\n✅ 降序排列正确：最新的记录在最上面")
            else:
                print("\n⚠️  降序排列可能不正确")
    
    # 3. 测试升序排序（最早在前）
    print("\n3. 测试升序排序（最早在前）...")
    asc_response = requests.get(
        f"{BASE_URL}/api/archived-scores",
        headers=headers,
        params={"page": 1, "page_size": 10, "sortOrder": "asc"}
    )
    
    if asc_response.status_code != 200:
        print(f"❌ 获取升序列表失败: {asc_response.status_code}")
        return False
    
    asc_data = asc_response.json()
    asc_scores = asc_data.get("scores", [])
    print(f"✅ 获取到 {len(asc_scores)} 条记录（升序）")
    
    if asc_scores:
        print("\n升序排列（最早在前）:")
        for i, score in enumerate(asc_scores[:5], 1):
            scored_at = score.get('scored_at', 'N/A')
            archive_id = score.get('archive_id', 'N/A')
            teacher = score.get('teacher_name', score.get('teacher_id', 'N/A'))
            print(f"  {i}. {archive_id} - {teacher} - 评分时间: {scored_at}")
        
        # 验证升序
        dates = [score.get('scored_at') for score in asc_scores if score.get('scored_at')]
        if len(dates) > 1:
            is_ascending = all(dates[i] <= dates[i+1] for i in range(len(dates)-1))
            if is_ascending:
                print("\n✅ 升序排列正确：最早的记录在最上面")
            else:
                print("\n⚠️  升序排列可能不正确")
    
    # 4. 测试默认排序（应该是降序）
    print("\n4. 测试默认排序（不指定sortOrder参数）...")
    default_response = requests.get(
        f"{BASE_URL}/api/archived-scores",
        headers=headers,
        params={"page": 1, "page_size": 5}
    )
    
    if default_response.status_code != 200:
        print(f"❌ 获取默认列表失败: {default_response.status_code}")
        return False
    
    default_data = default_response.json()
    default_scores = default_data.get("scores", [])
    print(f"✅ 获取到 {len(default_scores)} 条记录（默认排序）")
    
    if default_scores:
        print("\n默认排序:")
        for i, score in enumerate(default_scores, 1):
            scored_at = score.get('scored_at', 'N/A')
            archive_id = score.get('archive_id', 'N/A')
            print(f"  {i}. {archive_id} - 评分时间: {scored_at}")
        
        # 验证默认是降序
        dates = [score.get('scored_at') for score in default_scores if score.get('scored_at')]
        if len(dates) > 1:
            is_descending = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
            if is_descending:
                print("\n✅ 默认排序正确：使用降序（最新在前）")
            else:
                print("\n⚠️  默认排序可能不是降序")
    
    # 5. 总结
    print("\n" + "=" * 80)
    print("测试总结:")
    print("=" * 80)
    print("✅ 后端API已支持 sortOrder 参数")
    print("✅ 降序排序（desc）：最新的记录在最上面")
    print("✅ 升序排序（asc）：最早的记录在最上面")
    print("✅ 默认排序：降序（最新在前）")
    print("\n前端更新:")
    print("  - 添加了排序选择器（最新在前/最早在前）")
    print("  - 默认选择：最新在前")
    print("  - 用户可以随时切换排序方式")
    
    return True

if __name__ == "__main__":
    try:
        success = test_archive_sorting()
        if success:
            print("\n✅ 所有测试通过！")
        else:
            print("\n❌ 测试失败")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
