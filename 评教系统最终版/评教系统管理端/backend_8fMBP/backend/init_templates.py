"""
初始化默认评分模板

将5类文件的默认评分模板导入到数据库
"""

import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, ScoringTemplate
from app.config import DATABASE_URL
from app.services.template_manager import DEFAULT_TEMPLATES

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_templates():
    """初始化默认模板"""
    
    # 创建数据库连接
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 检查表是否存在
        Base.metadata.create_all(engine)
        
        # 导入默认模板
        for file_type, template_data in DEFAULT_TEMPLATES.items():
            # 检查模板是否已存在
            existing = session.query(ScoringTemplate).filter(
                ScoringTemplate.file_type == file_type
            ).first()
            
            if existing:
                logger.info(f"模板已存在，跳过: {file_type}")
                continue
            
            # 创建新模板
            template = ScoringTemplate(
                file_type=file_type,
                template_content=json.dumps(template_data, ensure_ascii=False),
                is_active=True
            )
            
            session.add(template)
            logger.info(f"添加模板: {file_type}")
        
        # 提交事务
        session.commit()
        logger.info("所有模板初始化成功")
        
    except Exception as e:
        session.rollback()
        logger.error(f"初始化模板失败: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_templates()
