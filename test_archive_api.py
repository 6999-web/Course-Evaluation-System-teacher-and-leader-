"""测试档案中心API"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8001"

# 获取token
def get_token():
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()['token']['access_token']
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None

# 测试获取归档列表
def test_get_archived_scores(token):
    print("\n" + "="*80)
    print("测试: 获取归档评分列表")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/archived-scores",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 成功获取归档列表")
        print(f"  总数: {data.get('total', 0)}")
        print(f"  当前页记录数: {len(data.get('scores', []))}")
        
        if data.get('scores'):
            print(f"\n前3条记录:")
            for i, score in enumerate(data['scores'][:3], 1):
                print(f"  {i}. {score['archive_id']} - {score['teacher_name']} - {score['template_name']}")
        
        return data.get('scores', [])
    else:
        print(f"✗ 获取失败")
        print(f"  错误: {response.text}")
        return []

# 测试获取详情
def test_get_score_detail(token, archive_id):
    print("\n" + "="*80)
    print(f"测试: 获取归档详情 - {archive_id}")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/archived-scores/{archive_id}",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 成功获取详情")
        print(f"  归档ID: {data.get('archive_id')}")
        print(f"  教师: {data.get('teacher_name')}")
        print(f"  考评表: {data.get('template_name')}")
        print(f"  得分: {data.get('score')} / {data.get('total_score')}")
        print(f"  学期: {data.get('semester')}")
        
        if data.get('scores'):
            print(f"\n  各项得分:")
            for name, score in data['scores'].items():
                print(f"    - {name}: {score}")
        
        return data
    else:
        print(f"✗ 获取详情失败")
        print(f"  错误: {response.text}")
        return None

# 测试删除
def test_delete_score(token, archive_id):
    print("\n" + "="*80)
    print(f"测试: 删除归档记录 - {archive_id}")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/api/archived-scores/{archive_id}",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 删除成功")
        print(f"  消息: {data.get('message')}")
        return True
    else:
        print(f"✗ 删除失败")
        print(f"  错误: {response.text}")
        return False

# 主测试流程
def main():
    print("="*80)
    print("档案中心API测试")
    print("="*80)
    
    # 1. 登录获取token
    print("\n1. 登录系统...")
    token = get_token()
    if not token:
        print("✗ 无法获取token，测试终止")
        return
    print(f"✓ 登录成功，Token: {token[:50]}...")
    
    # 2. 获取归档列表
    scores = test_get_archived_scores(token)
    
    # 3. 如果有记录，测试获取详情
    if scores:
        archive_id = scores[0]['archive_id']
        detail = test_get_score_detail(token, archive_id)
        
        # 4. 测试删除（注意：这会真的删除数据，谨慎使用）
        # 如果要测试删除，取消下面的注释
        # if len(scores) > 1:  # 确保至少有2条记录
        #     test_archive_id = scores[-1]['archive_id']  # 删除最后一条
        #     test_delete_score(token, test_archive_id)
        #     
        #     # 再次获取列表验证删除
        #     print("\n验证删除结果:")
        #     test_get_archived_scores(token)
    else:
        print("\n⚠ 没有归档记录可供测试")
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    main()
