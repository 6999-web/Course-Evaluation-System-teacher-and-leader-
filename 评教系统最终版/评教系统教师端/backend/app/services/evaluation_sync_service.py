"""
向管理端同步考评数据的服务
"""
import httpx
import os

# 管理端API地址
ADMIN_API_BASE = os.getenv("ADMIN_API_URL", "http://localhost:8001")


async def sync_evaluation_submission_to_admin(
    task_id: str,
    template_id: str,
    teacher_id: str,
    teacher_name: str,
    files: list,
    notes: str,
    submitted_at: str
):
    """
    将考评提交信息同步到管理端
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{ADMIN_API_BASE}/api/evaluation-tasks/sync-submission",
                json={
                    "task_id": task_id,
                    "template_id": template_id,
                    "teacher_id": teacher_id,
                    "teacher_name": teacher_name,
                    "files": files,
                    "notes": notes,
                    "submitted_at": submitted_at
                },
                timeout=10.0
            )
            if response.status_code not in [200, 201]:
                print(f"同步考评提交到管理端失败: {response.text}")
                return False
            print(f"同步考评提交到管理端成功")
            return True
        except Exception as e:
            print(f"同步考评提交到管理端异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
