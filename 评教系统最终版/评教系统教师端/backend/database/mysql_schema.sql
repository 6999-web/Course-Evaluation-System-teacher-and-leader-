-- MySQL数据库创建脚本
-- 评教系统数据库结构

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `乌鲁鲁` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `乌鲁鲁`;

-- 系统配置表
CREATE TABLE IF NOT EXISTS `system_config` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `academic_year` VARCHAR(50) NOT NULL COMMENT '学年学期（如：2024-2025-1）',
  `evaluation_plan` TEXT COMMENT '评教方案配置（模板、权重等）',
  `time_windows` TEXT COMMENT '各阶段时间窗口（开评/截止）',
  `status` ENUM('enable', 'disable') DEFAULT 'enable' COMMENT '启用状态（enable/disable）',
  PRIMARY KEY (`id`),
  INDEX `idx_academic_year` (`academic_year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 评教任务表
CREATE TABLE IF NOT EXISTS `evaluation_tasks` (
  `task_id` VARCHAR(50) NOT NULL COMMENT '任务ID（格式：2024-1-T001）',
  `course_id` VARCHAR(50) NOT NULL COMMENT '关联课程ID（对接教务系统）',
  `teacher_id` VARCHAR(50) NOT NULL COMMENT '授课教师ID',
  `student_count` INT DEFAULT 0 COMMENT '应评学生数',
  `completed_count` INT DEFAULT 0 COMMENT '已评学生数',
  `quality_score` FLOAT DEFAULT 0.0 COMMENT '数据质量评分（0-100）',
  PRIMARY KEY (`task_id`),
  INDEX `idx_course_id` (`course_id`),
  INDEX `idx_teacher_id` (`teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 评教数据表
CREATE TABLE IF NOT EXISTS `evaluation_data` (
  `record_id` VARCHAR(36) NOT NULL COMMENT '记录唯一标识',
  `task_id` VARCHAR(50) NOT NULL COMMENT '关联评教任务ID',
  `student_hash` VARCHAR(100) NOT NULL COMMENT '学生匿名标识',
  `dimension_scores` TEXT COMMENT '各维度得分（如：教学态度：95）',
  `text_feedback` TEXT COMMENT '学生文字反馈',
  `submission_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  `validity_flag` BOOLEAN DEFAULT TRUE COMMENT '有效性标识（true/false）',
  `validity_reason` TEXT COMMENT '有效性原因',
  PRIMARY KEY (`record_id`),
  INDEX `idx_task_id` (`task_id`),
  INDEX `idx_student_hash` (`student_hash`),
  CONSTRAINT `fk_evaluation_data_task_id` FOREIGN KEY (`task_id`) REFERENCES `evaluation_tasks` (`task_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入初始数据
-- 系统配置初始数据
INSERT INTO `system_config` (`academic_year`, `evaluation_plan`, `time_windows`, `status`) VALUES
('2024-2025-1', '{"template": "default", "weights": {"teaching_attitude": 0.3, "teaching_method": 0.3, "course_content": 0.2, "teaching_effect": 0.2}}', '{"start_date": "2024-12-01", "end_date": "2024-12-31"}', 'enable');

-- 评教任务初始数据
INSERT INTO `evaluation_tasks` (`task_id`, `course_id`, `teacher_id`, `student_count`, `completed_count`, `quality_score`) VALUES
('2024-1-T001', 'C001', 'T001', 50, 0, 0.0),
('2024-1-T002', 'C002', 'T001', 45, 0, 0.0),
('2024-1-T003', 'C003', 'T002', 60, 0, 0.0);

-- 提交所有更改
COMMIT;

-- 查看创建的表
SHOW TABLES;

-- 查看表结构
DESCRIBE `system_config`;
DESCRIBE `evaluation_tasks`;
DESCRIBE `evaluation_data`;