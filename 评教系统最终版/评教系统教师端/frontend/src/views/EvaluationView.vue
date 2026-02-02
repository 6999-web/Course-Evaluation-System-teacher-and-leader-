<template>
  <div class="evaluation-container">
    <h2>我的评价</h2>
    
    <el-card class="filter-card" shadow="hover">
      <div class="filter-content">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="学期">
            <el-select v-model="filterForm.semester" placeholder="选择学期">
              <el-option label="2025-2026学年第一学期" value="2025-2026-1" />
              <el-option label="2024-2025学年第二学期" value="2024-2025-2" />
              <el-option label="2024-2025学年第一学期" value="2024-2025-1" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="课程">
            <el-input v-model="filterForm.courseName" placeholder="课程名称" clearable />
          </el-form-item>
          
          <el-form-item label="评价状态">
            <el-select v-model="filterForm.status" placeholder="选择状态">
              <el-option label="全部" value="all" />
              <el-option label="已完成" value="completed" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="未开始" value="not_started" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleFilter">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <el-card class="table-card" shadow="hover">
      <el-table :data="evaluations" style="width: 100%" stripe>
        <el-table-column type="index" width="50" />
        <el-table-column prop="semester" label="学期" width="180" />
        <el-table-column prop="courseName" label="课程名称" min-width="200">
          <template #default="scope">
            <div class="course-info">
              <strong>{{ scope.row.courseName }}</strong>
              <span class="course-code">{{ scope.row.courseCode }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="classInfo" label="班级" width="150" />
        <el-table-column prop="studentCount" label="应评人数" width="100" />
        <el-table-column prop="completedCount" label="已评人数" width="100" />
        <el-table-column prop="completionRate" label="参评率" width="100">
          <template #default="scope">
            <el-progress :percentage="scope.row.completionRate" :format="formatPercentage" size="small" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="评分状态" width="120">
          <template #default="scope">
            <el-tag
              :type="getScoreStatusTagType(scope.row.status)"
              size="small"
            >
              {{ getScoreStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="任务状态" width="120">
          <template #default="scope">
            <el-tag
              :type="getStatusTagType(scope.row.status)"
              size="small"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="evaluationDate" label="评价日期" width="150" />
        <el-table-column fixed="right" label="操作" width="180">
          <template #default="scope">
            <el-button
              v-if="scope.row.status === 'completed'"
              type="primary"
              size="small"
              @click="viewEvaluationDetail(scope.row)"
            >
              查看详情
            </el-button>
            <el-button
              v-else-if="scope.row.status === 'in_progress'"
              type="warning"
              size="small"
              @click="viewEvaluationProgress(scope.row)"
            >
              查看进度
            </el-button>
            <el-button
              v-else
              type="info"
              size="small"
              @click="viewEvaluationPlan(scope.row)"
            >
              查看计划
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalEvaluations"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessageBox } from 'element-plus'

// 筛选表单
const filterForm = reactive({
  semester: '2025-2026-1',
  courseName: '',
  status: 'all'
})

// 分页数据
const currentPage = ref(1)
const pageSize = ref(10)
const totalEvaluations = ref(24)

// 评价数据
const evaluations = ref([
  {
    id: 1,
    semester: '2025-2026学年第一学期',
    courseName: '高等数学',
    courseCode: 'MATH101',
    classInfo: '2024级计算机1班',
    studentCount: 45,
    completedCount: 45,
    completionRate: 100,
    averageScore: 4.8,
    status: 'completed',
    evaluationDate: '2026-01-15'
  },
  {
    id: 2,
    semester: '2025-2026学年第一学期',
    courseName: '大学物理',
    courseCode: 'PHYS101',
    classInfo: '2024级电子1班',
    studentCount: 52,
    completedCount: 48,
    completionRate: 92,
    averageScore: 4.7,
    status: 'completed',
    evaluationDate: '2026-01-14'
  },
  {
    id: 3,
    semester: '2025-2026学年第一学期',
    courseName: '计算机基础',
    courseCode: 'CS101',
    classInfo: '2024级数学1班',
    studentCount: 48,
    completedCount: 35,
    completionRate: 73,
    averageScore: 4.6,
    status: 'in_progress',
    evaluationDate: '2026-01-20'
  },
  {
    id: 4,
    semester: '2024-2025学年第二学期',
    courseName: '线性代数',
    courseCode: 'MATH201',
    classInfo: '2023级计算机2班',
    studentCount: 42,
    completedCount: 42,
    completionRate: 100,
    averageScore: 4.5,
    status: 'completed',
    evaluationDate: '2025-06-15'
  },
  {
    id: 5,
    semester: '2025-2026学年第一学期',
    courseName: '数据结构',
    courseCode: 'CS201',
    classInfo: '2023级计算机1班',
    studentCount: 38,
    completedCount: 0,
    completionRate: 0,
    averageScore: 0,
    status: 'not_started',
    evaluationDate: '2026-02-01'
  }
])

// 格式化百分比
const formatPercentage = (percentage: number) => {
  return `${percentage}%`
}

// 获取评分状态标签类型
const getScoreStatusTagType = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'in_progress':
      return 'warning'
    case 'not_started':
      return 'info'
    default:
      return 'info'
  }
}

// 获取评分状态文本
const getScoreStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return '已评分'
    case 'in_progress':
      return '评分中'
    case 'not_started':
      return '未评分'
    default:
      return '未评分'
  }
}

// 获取任务状态标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'in_progress':
      return 'warning'
    case 'not_started':
      return 'info'
    default:
      return ''
  }
}

// 获取任务状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'in_progress':
      return '进行中'
    case 'not_started':
      return '未开始'
    default:
      return ''
  }
}

// 处理筛选
const handleFilter = () => {
  console.log('筛选条件:', filterForm)
  // 这里可以添加筛选逻辑
}

// 重置筛选
const resetFilter = () => {
  filterForm.semester = '2025-2026-1'
  filterForm.courseName = ''
  filterForm.status = 'all'
}

// 查看评价详情（不显示评分）
const viewEvaluationDetail = (row: any) => {
  console.log('查看评价详情（不含评分）:', row)
  ElMessageBox.alert(
    `<div style="line-height: 1.8;">
      <p><strong>课程名称：</strong>${row.courseName}</p>
      <p><strong>班级：</strong>${row.classInfo}</p>
      <p><strong>应评人数：</strong>${row.studentCount}人</p>
      <p><strong>已评人数：</strong>${row.completedCount}人</p>
      <p><strong>参评率：</strong>${row.completionRate}%</p>
      <p><strong>评价日期：</strong>${row.evaluationDate}</p>
      <p style="color: #67C23A; margin-top: 10px;"><strong>评分状态：</strong>已评分</p>
      <p style="color: #909399; font-size: 12px; margin-top: 10px;">注：具体评分由管理员统一管理，教师端不显示评分详情</p>
    </div>`,
    '评价详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定'
    }
  )
}

// 查看评价进度
const viewEvaluationProgress = (row: any) => {
  console.log('查看评价进度:', row)
  // 这里可以添加查看进度的逻辑
}

// 查看评价计划
const viewEvaluationPlan = (row: any) => {
  console.log('查看评价计划:', row)
  // 这里可以添加查看计划的逻辑
}

// 处理每页条数变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  console.log('每页条数:', size)
}

// 处理当前页码变化
const handleCurrentChange = (current: number) => {
  currentPage.value = current
  console.log('当前页码:', current)
}
</script>

<style scoped>
.evaluation-container {
  padding: 0;
  position: relative;
  z-index: 1;
}

.evaluation-container h2 {
  margin-bottom: 20px;
  color: #303133;
  font-family: 'SimHei', '黑体', sans-serif;
  font-weight: bold;
  position: relative;
  padding-bottom: 10px;
}

.evaluation-container h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, #ffd04b, #0f4c81);
  border-radius: 2px;
}

.filter-card {
  margin-bottom: 20px;
  background-color: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(15, 76, 129, 0.3);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.filter-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  border-color: rgba(15, 76, 129, 0.5);
}

.filter-content {
  display: flex;
  align-items: center;
}

.filter-form {
  width: 100%;
}

.table-card {
  margin-bottom: 20px;
  background-color: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(15, 76, 129, 0.3);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.table-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  border-color: rgba(15, 76, 129, 0.5);
}

.course-info {
  display: flex;
  flex-direction: column;
}

.course-code {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* 表格样式优化 */
.el-table {
  border-radius: 6px;
  overflow: hidden;
}

.el-table th {
  background-color: rgba(15, 76, 129, 0.9);
  color: white;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.el-table td {
  border-bottom: 1px solid rgba(15, 76, 129, 0.1);
}

.el-table__row:hover {
  background-color: rgba(255, 210, 75, 0.1);
}
</style>