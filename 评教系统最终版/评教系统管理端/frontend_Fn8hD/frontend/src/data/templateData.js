// 评教模板数据配置文件
export const templateList = [
  // 课堂教学评价
  {
    id: 1,
    name: "学生课堂教学评价表",
    description: "用于学生对教师课堂教学质量进行评价的标准表格",
    category: "课堂教学评价",
    format: "docx",
    filePath: "/templates/student-evaluation.docx",
    lastUpdate: "2024.08"
  },
  {
    id: 2,
    name: "督导听课评价表",
    description: "用于教学督导对教师课堂教学情况进行评价的表格",
    category: "课堂教学评价",
    format: "docx",
    filePath: "/templates/supervisor-evaluation.docx",
    lastUpdate: "2024.08"
  },
  
  // 课程评估
  {
    id: 3,
    name: "课程质量评估报告模板",
    description: "用于学期末对课程整体质量进行综合评估的报告模板",
    category: "课程评估",
    format: "pdf",
    filePath: "/templates/course-assessment-report.pdf",
    lastUpdate: "2024.08"
  },
  {
    id: 4,
    name: "课程目标达成度分析表",
    description: "用于分析课程目标达成情况的表格模板",
    category: "课程评估",
    format: "docx",
    filePath: "/templates/course-objective-analysis.docx",
    lastUpdate: "2024.08"
  },
  
  // 专项检查
  {
    id: 5,
    name: "教学中期检查表",
    description: "用于教学中期检查的标准表格",
    category: "专项检查",
    format: "docx",
    filePath: "/templates/midterm-checklist.docx",
    lastUpdate: "2024.08"
  },
  {
    id: 6,
    name: "教案检查评分表",
    description: "用于对教师教案进行检查和评分的表格",
    category: "专项检查",
    format: "docx",
    filePath: "/templates/lesson-plan-check.docx",
    lastUpdate: "2024.08"
  },
  
  // 实践教学
  {
    id: 7,
    name: "实验教学评价表",
    description: "用于对实验教学质量进行评价的表格",
    category: "实践教学",
    format: "docx",
    filePath: "/templates/experiment-evaluation.docx",
    lastUpdate: "2024.08"
  },
  {
    id: 8,
    name: "实习实践反馈表",
    description: "用于收集学生实习实践反馈的表格",
    category: "实践教学",
    format: "pdf",
    filePath: "/templates/internship-feedback.pdf",
    lastUpdate: "2024.08"
  },
  
  // 综合调研
  {
    id: 9,
    name: "毕业生满意度调查问卷",
    description: "用于调研毕业生对教学质量满意度的问卷模板",
    category: "综合调研",
    format: "docx",
    filePath: "/templates/graduate-satisfaction.docx",
    lastUpdate: "2024.08"
  },
  {
    id: 10,
    name: "教师教学能力调研表",
    description: "用于调研教师教学能力的表格模板",
    category: "综合调研",
    format: "docx",
    filePath: "/templates/teacher-capability-survey.docx",
    lastUpdate: "2024.08"
  }
];

// 分类列表
export const categories = [
  { id: 'all', name: '全部' },
  { id: '课堂教学评价', name: '课堂教学' },
  { id: '课程评估', name: '课程评估' },
  { id: '专项检查', name: '专项检查' },
  { id: '实践教学', name: '实践教学' },
  { id: '综合调研', name: '综合调研' }
];