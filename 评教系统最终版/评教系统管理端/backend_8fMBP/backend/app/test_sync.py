"""
测试同步功能
"""
import asyncio
from services import sync_distribution_to_teacher

async def test():
    print("测试开始...")
    await sync_distribution_to_teacher(
        material_id="test_material_001",
        material_name="测试材料",
        material_type="evaluation_form",
        file_url="/uploads/test",
        teacher_ids=["teacher_001"],
        distributed_at="2024-01-29T10:00:00"
    )
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(test())
