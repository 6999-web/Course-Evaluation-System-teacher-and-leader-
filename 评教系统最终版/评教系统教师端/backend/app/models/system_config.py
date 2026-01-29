from sqlalchemy import Column, Integer, String, Text, Enum
import enum

from app.models.base import Base


class ConfigStatus(str, enum.Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String(50), index=True, comment="学年学期（如：2024-2025-1）")
    evaluation_plan = Column(Text, comment="评教方案配置（模板、权重等）")
    time_windows = Column(Text, comment="各阶段时间窗口（开评/截止）")
    status = Column(Enum(ConfigStatus), default=ConfigStatus.ENABLE, comment="启用状态（enable/disable）")
