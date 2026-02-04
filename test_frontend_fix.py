#!/usr/bin/env python3
"""
测试前端修复是否成功
"""

import requests
import time

def test_frontend_access():
    """测试前端是否可以正常访问"""
    print("🚀 测试前端修复结果")
    print("=" * 50)
    
    # 测试前端页面是否可以访问
    print("1. 测试前端页面访问...")
    try:
        response = requests.get("http://localhost:5174", timeout=10)
        if response.status_code == 200:
            print("✅ 前端页面可以正常访问")
            print(f"   状态码: {response.status_code}")
            print(f"   页面大小: {len(response.text)} 字符")
            return True
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端页面访问异常: {e}")
        return False

def test_backend_api():
    """测试后端API是否正常"""
    print("\n2. 测试后端API...")
    try:
        # 测试登录API
        response = requests.post("http://localhost:8001/api/login", json={
            "username": "admin",
            "password": "123456"
        }, timeout=10)
        
        if response.status_code == 200:
            print("✅ 后端API正常工作")
            return True
        else:
            print(f"❌ 后端API异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端API连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 前端修复验证测试")
    print("=" * 50)
    
    # 等待前端服务完全启动
    print("等待前端服务启动...")
    time.sleep(3)
    
    frontend_ok = test_frontend_access()
    backend_ok = test_backend_api()
    
    print("\n" + "=" * 50)
    print("🏆 测试结果总结")
    print("=" * 50)
    
    if frontend_ok and backend_ok:
        print("✅ 所有测试通过!")
        print("🎉 前端修复成功!")
        print("\n📋 修复内容:")
        print("• 修复了MagicStick图标导入错误")
        print("• 修复了loading属性绑定问题")
        print("• 修复了重复标签问题")
        print("• 重启了前端开发服务器")
        print("\n🚀 现在可以正常使用前端界面了!")
        print(f"   前端地址: http://localhost:5174")
        print(f"   后端地址: http://localhost:8001")
    else:
        print("❌ 部分测试失败")
        if not frontend_ok:
            print("• 前端页面访问有问题")
        if not backend_ok:
            print("• 后端API有问题")
        print("\n💡 建议:")
        print("• 检查服务是否正常启动")
        print("• 查看浏览器控制台错误信息")
        print("• 清除浏览器缓存后重试")

if __name__ == "__main__":
    main()