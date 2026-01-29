// 枚举类型定义

// 申诉状态枚举
export enum AppealStatus {
  PENDING = 'pending',      // 待审核
  APPROVED = 'approved',    // 已通过
  REJECTED = 'rejected',    // 已拒绝
  PROCESSING = 'processing' // 处理中
}

// 申诉类型枚举
export enum AppealType {
  EVALUATION = 'evaluation',    // 评价申诉
  SCORE = 'score',              // 分数申诉
  PROCESS = 'process'           // 流程申诉
}

// 评价状态枚举
export enum EvaluationStatus {
  PENDING = 'pending',      // 待评价
  COMPLETED = 'completed',  // 已完成
  EXPIRED = 'expired'       // 已过期
}

// 评价类型枚举
export enum EvaluationType {
  REGULAR = 'regular',      // 常规评价
  MIDTERM = 'midterm',      // 期中评价
  FINAL = 'final'           // 期末评价
}

// 反馈类型枚举
export enum FeedbackType {
  SUGGESTION = 'suggestion',  // 建议
  COMPLAINT = 'complaint',    // 投诉
  PRAISE = 'praise',          // 表扬
  QUESTION = 'question'       // 疑问
}

// 反馈状态枚举
export enum FeedbackStatus {
  PENDING = 'pending',      // 待处理
  PROCESSING = 'processing',// 处理中
  RESOLVED = 'resolved'     // 已解决
}

// 改进计划状态枚举
export enum ImprovementStatus {
  PENDING = 'pending',      // 待实施
  IN_PROGRESS = 'in_progress',// 实施中
  COMPLETED = 'completed',  // 已完成
  DELAYED = 'delayed'       // 已延迟
}

// 评审状态枚举
export enum ReviewStatus {
  PENDING = 'pending',      // 待评审
  APPROVED = 'approved',    // 已通过
  REJECTED = 'rejected',    // 已拒绝
  REVISED = 'revised'       // 已修改
}

// 评审类型枚举
export enum ReviewType {
  IMPROVEMENT = 'improvement',  // 改进计划审核
  APPEAL = 'appeal'             // 申诉审核
}

// 评分等级枚举
export enum ScoreLevel {
  EXCELLENT = 'excellent',  // 优秀
  GOOD = 'good',            // 良好
  SATISFACTORY = 'satisfactory', // 满意
  POOR = 'poor'             // 较差
}
