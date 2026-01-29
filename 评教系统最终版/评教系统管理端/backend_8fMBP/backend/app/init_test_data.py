"""
初始化测试数据
"""
from database import SessionLocal, engine, Base
from models import Teacher, Department

# 创建所有表
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # 检查是否已有数据
    existing_teachers = db.query(Teacher).count()
    if existing_teachers > 0:
        print(f"已存在 {existing_teachers} 个教师记录")
    else:
        # 创建测试部门
        departments = [
            Department(department_id="dept_001", department_name="计算机学院"),
            Department(department_id="dept_002", department_name="电子工程学院"),
            Department(department_id="dept_003", department_name="人文学院"),
        ]
        
        for dept in departments:
            existing = db.query(Department).filter(Department.department_id == dept.department_id).first()
            if not existing:
                db.add(dept)
        
        # 创建测试教师
        teachers = [
            Teacher(teacher_id="teacher_001", teacher_name="张三", department_id="dept_001"),
            Teacher(teacher_id="teacher_002", teacher_name="李四", department_id="dept_002"),
            Teacher(teacher_id="teacher_003", teacher_name="王五", department_id="dept_003"),
            Teacher(teacher_id="teacher_004", teacher_name="赵六", department_id="dept_001"),
            Teacher(teacher_id="teacher_005", teacher_name="孙七", department_id="dept_002"),
        ]
        
        for teacher in teachers:
            existing = db.query(Teacher).filter(Teacher.teacher_id == teacher.teacher_id).first()
            if not existing:
                db.add(teacher)
        
        db.commit()
        print("测试数据初始化成功！")
        print(f"创建了 {len(departments)} 个部门")
        print(f"创建了 {len(teachers)} 个教师")
        
except Exception as e:
    print(f"初始化失败: {e}")
    db.rollback()
finally:
    db.close()
