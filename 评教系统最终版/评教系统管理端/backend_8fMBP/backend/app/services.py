"""
跨系统通信服务
"""
import httpx
from typing import List, Dict
import os

# 教师端API地址
TEACHER_API_BASE = os.getenv("TEACHER_API_URL", "http://localhost:8000")


async def sync_distribution_to_teacher(
    material_id: str,
    material_name: str,
    material_type: str,
    file_url: str,
    teacher_ids: List[str],
    distributed_at: str
):
    """
    将分发信息同步到教师端
    """
    print(f"开始同步分发信息到教师端: {teacher_ids}")
    async with httpx.AsyncClient(timeout=30.0) as client:
        for teacher_id in teacher_ids:
            try:
                print(f"正在同步到教师 {teacher_id}...")
                response = await client.post(
                    f"{TEACHER_API_BASE}/api/admin/sync-distribution",
                    json={
                        "material_id": material_id,
                        "teacher_id": teacher_id,
                        "material_name": material_name,
                        "material_type": material_type,
                        "file_url": file_url,
                        "distributed_at": distributed_at
                    },
                    timeout=30.0
                )
                print(f"同步响应状态码: {response.status_code}")
                if response.status_code not in [200, 201]:
                    print(f"同步到教师 {teacher_id} 失败: {response.text}")
                else:
                    print(f"同步到教师 {teacher_id} 成功！")
            except Exception as e:
                print(f"同步到教师 {teacher_id} 异常: {str(e)}")
                import traceback
                traceback.print_exc()


async def get_teacher_submission(submission_id: str) -> Dict:
    """
    从教师端获取提交信息
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{TEACHER_API_BASE}/api/admin/submission/{submission_id}",
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"获取提交信息失败: {str(e)}")
    return {}


async def sync_review_status_to_teacher(
    submission_id: str,
    status: str,
    feedback: str,
    reviewed_at: str
):
    """
    将审核状态同步到教师端
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{TEACHER_API_BASE}/api/admin/sync-review",
                json={
                    "submission_id": submission_id,
                    "status": status,
                    "feedback": feedback,
                    "reviewed_at": reviewed_at
                },
                timeout=10.0
            )
            if response.status_code not in [200, 201]:
                print(f"同步审核状态失败: {response.text}")
            else:
                print(f"同步审核状态成功")
        except Exception as e:
            print(f"同步审核状态异常: {str(e)}")
            import traceback
            traceback.print_exc()
