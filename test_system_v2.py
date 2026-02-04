#!/usr/bin/env python3
"""
评教系统完整功能测试脚本 v2
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# API基础URL
TEACHER_API_BASE = "http://localhost:8000/api"
ADMIN_API_BASE = "http://localhost:8001"

# 测试用户凭证
TEST_TEACHER_ID = "teacher_001"
TEST_TEACHER_PASSWORD = "teacher123"
TEST_ADMIN_ID = "admin"
TEST_ADMIN_PASSWORD = "admin123"

# 全局变量存储token
teacher_token = None
admin_token = None

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"测试总结: 通过 {self.passed}/{total}, 失败 {self.failed}/{total}")
        if self.errors:
            print(f"\n失败详情:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}\n")

result = TestResult()

def make_request(method: str, url: str, token: Optional[str] = None, 
                 data: Optional[Dict] = None) -> Optional[Dict]:
    """发送HTTP请求"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return None
        
        if response.status_code in [200, 201, 204]:
            try:
                return response.json() if response.text else {"status": "success"}
            except:
                return {"status": "success"}
        else:
            return None
    except Exception as e:
        return None

# ==================== 教师端测试 ====================

def test_teacher_login():
    """测试教师端登录"""
    global teacher_token
    url = f"{TEACHER_API_BASE}/auth/login"
    data = {
        "username": TEST_TEACHER_ID,
        "password": TEST_TEACHER_PASSWORD
    }
    
    response = make_request("POST", url, data=data)
    if response and "access_token" in response:
        teacher_token = response["access_token"]
        result.add_pass("教师端登录")
        return True
    else:
        result.add_fail("教师端登录", "无法获取token")
        return False

def test_teacher_dashboard():
    """测试教师端仪表盘"""
    if not teacher_token:
        result.add_fail("教师端仪表盘", "未登录")
        return False
    
    url = f"{TEACHER_API_BASE}/dashboard/stats"
    response = make_request("GET", url, token=teacher_token)
    if response:
        result.add_pass("教师端仪表盘")
        return True
    else:
        result.add_fail("教师端仪表盘", "获取数据失败")
        return False

def test_teacher_evaluations():
    """测试教师端我的评价"""
    if not teacher_token:
        result.add_fail("教师端我的评价", "未登录")
        return False
    
    url = f"{TEACHER_API_BASE}/evaluation/tasks"
    response = make_request("GET", url, token=teacher_token)
    if response is not None:
        result.add_pass("教师端我的评价")
        return True
    else:
        result.add_fail("教师端我的评价", "获取数据失败")
        return False

def test_teacher_reports():
    """测试教师端评价报告"""
    if not teacher_token:
        result.add_fail("教师端评价报告", "未登录")
        return False
    
    url = f"{TEACHER_API_BASE}/report/list"
    response = make_request("GET", url, token=teacher_token)
    if response is not None:
        result.add_pass("教师端评价报告")
        return True
    else:
        result.add_fail("教师端评价报告", "获取数据失败")
        return False

def test_teacher_feedback():
    """测试教师端学生反馈"""
    if not teacher_token:
        result.add_fail("教师端学生反馈", "未登录")
        return False
    
    url = f"{TEACHER_API_BASE}/feedback/list"
    response = make_request("GET", url, token=teacher_token)
    if response is not None:
        result.add_pass("教师端学生反馈")
        return True
    else:
        result.add_fail("教师端学生反馈", "获取数据失败")
        return False

def test_teacher_appeals():
    """测试教师端申诉"""
    if not teacher_token:
        result.add_fail("教师端申诉", "未登录")
        return False
    
    url = f"{TEACHER_API_BASE}/appeal/list"
    response = make_request("GET", url, token=teacher_token)
    if response is not None:
        result.add_pass("教师端申诉")
        return True
    else:
        result.add_fail("教师端申诉", "获取数据失败")
        return False

# ==================== 管理端测试 ====================

def test_admin_login():
    """测试管理端登录"""
    global admin_token
    url = f"{ADMIN_API_BASE}/api/login"
    data = {
        "username": TEST_ADMIN_ID,
        "password": TEST_ADMIN_PASSWORD
    }
    
    response = make_request("POST", url, data=data)
    if response and "token" in response:
        if isinstance(response["token"], dict) and "access_token" in response["token"]:
            admin_token = response["token"]["access_token"]
        else:
            admin_token = response["token"]
        result.add_pass("管理端登录")
        return True
    else:
        result.add_fail("管理端登录", "无法获取token")
        return False

def test_admin_tasks():
    """测试管理端考评任务"""
    if not admin_token:
        result.add_fail("管理端考评任务", "未登录")
        return False
    
    url = f"{ADMIN_API_BASE}/api/evaluation-tasks"
    response = make_request("GET", url, token=admin_token)
    if response is not None:
        result.add_pass("管理端考评任务")
        return True
    else:
        result.add_fail("管理端考评任务", "获取数据失败")
        return False

def test_admin_user_info():
    """测试管理端获取用户信息"""
    if not admin_token:
        result.add_fail("管理端用户信息", "未登录")
        return False
    
    url = f"{ADMIN_API_BASE}/api/user/me"
    response = make_request("GET", url, token=admin_token)
    if response is not None:
        result.add_pass("管理端用户信息")
        return True
    else:
        result.add_fail("管理端用户信息", "获取数据失败")
        return False

# ==================== 主测试流程 ====================

def run_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始评教系统完整功能测试 v2")
    print("="*60 + "\n")
    
    # 检查服务健康状态
    print("检查服务健康状态...")
    try:
        teacher_health = requests.get(f"{TEACHER_API_BASE.replace('/api', '')}/health", timeout=5)
        if teacher_health.status_code == 200:
            print("✅ 教师端后端服务正常")
        else:
            print("❌ 教师端后端服务异常")
    except:
        print("❌ 教师端后端服务无法连接")
    
    try:
        admin_health = requests.get(f"{ADMIN_API_BASE}/health", timeout=5)
        if admin_health.status_code == 200:
            print("✅ 管理端后端服务正常")
        else:
            print("❌ 管理端后端服务异常")
    except:
        print("❌ 管理端后端服务无法连接")
    
    print("\n" + "-"*60)
    print("教师端功能测试")
    print("-"*60 + "\n")
    
    # 教师端测试
    if test_teacher_login():
        test_teacher_dashboard()
        test_teacher_evaluations()
        test_teacher_reports()
        test_teacher_feedback()
        test_teacher_appeals()
    
    print("\n" + "-"*60)
    print("管理端功能测试")
    print("-"*60 + "\n")
    
    # 管理端测试
    if test_admin_login():
        test_admin_user_info()
        test_admin_tasks()
    
    # 输出测试总结
    result.summary()

if __name__ == "__main__":
    run_tests()
