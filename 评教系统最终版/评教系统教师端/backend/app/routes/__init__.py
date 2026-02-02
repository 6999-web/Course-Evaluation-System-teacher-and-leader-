from fastapi import APIRouter
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .evaluation import router as evaluation_router
from .feedback import router as feedback_router
from .report import router as report_router
from .appeal import router as appeal_router
from .improvement import router as improvement_router
from .review import router as review_router
from .material import router as material_router
from .admin_sync import router as admin_sync_router
from .evaluation_task import router as evaluation_task_router

api_router = APIRouter()

# 注册认证路由
api_router.include_router(auth_router, tags=["auth"])

# 注册各个模块的路由
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(evaluation_router, prefix="/evaluation", tags=["evaluation"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["feedback"])
api_router.include_router(report_router, prefix="/report", tags=["report"])
api_router.include_router(appeal_router, prefix="/appeal", tags=["appeal"])
api_router.include_router(improvement_router, prefix="/improvement", tags=["improvement"])
api_router.include_router(review_router, prefix="/review", tags=["review"])
# 【修改】material_router已经有前缀，不需要再添加
api_router.include_router(material_router, tags=["material"])
# 【修改】admin_sync_router已经有前缀，不需要再添加
api_router.include_router(admin_sync_router, tags=["admin_sync"])
# 【新增】考评任务路由
api_router.include_router(evaluation_task_router, tags=["evaluation_task"])
