<template>
  <div class="personal-growth-profile">
    <!-- 个人成长档案主卡片 -->
    <el-card class="growth-profile-card" shadow="hover">
      <template #header>
        <div class="growth-profile-header">
          <el-icon name="UserFilled"></el-icon>
          <span class="growth-profile-title">个人成长档案</span>
          <el-button type="primary" size="small" @click="exportGrowthProfile">
            <el-icon name="Download"></el-icon>导出档案
          </el-button>
        </div>
      </template>
      
      <div class="growth-profile-content">
        <!-- 基本信息部分 -->
        <el-card class="info-section-card" shadow="hover" size="small">
          <template #header>
            <div class="section-header">
              <el-icon name="User"></el-icon>
              <span class="section-title">基本信息</span>
            </div>
          </template>
          
          <div class="info-content">
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">姓名：</span>
                <span class="info-value">{{ teacherInfo.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">性别：</span>
                <span class="info-value">{{ teacherInfo.gender }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">年龄：</span>
                <span class="info-value">{{ teacherInfo.age }}岁</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">职称：</span>
                <span class="info-value">{{ teacherInfo.title }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">教龄：</span>
                <span class="info-value">{{ teacherInfo.teachingYears }}年</span>
              </div>
              <div class="info-item">
                <span class="info-label">所属学院：</span>
                <span class="info-value">{{ teacherInfo.department }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item full-width">
                <span class="info-label">研究方向：</span>
                <span class="info-value">{{ teacherInfo.researchArea }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item full-width">
                <span class="info-label">个人简介：</span>
                <span class="info-value description">{{ teacherInfo.bio }}</span>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 评价数据统计部分 -->
        <div class="stats-section">
          <el-card class="stats-card" shadow="hover" size="small">
            <template #header>
              <div class="section-header">
                <el-icon name="TrendCharts"></el-icon>
                <span class="section-title">评价数据统计</span>
              </div>
            </template>
            
            <div class="stats-content">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ evaluationStats.averageScore.toFixed(2) }}</div>
                  <div class="stat-label">平均评分</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ evaluationStats.coursesTaught }}</div>
                  <div class="stat-label">课程总数</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ evaluationStats.studentsTaught }}</div>
                  <div class="stat-label">授课学生数</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ evaluationStats.excellentRate }}%</div>
                  <div class="stat-label">优秀率</div>
                </div>
              </div>
              
              <!-- 评分趋势图 -->
              <div class="chart-container">
                <el-progress type="dashboard" :percentage="evaluationStats.averageScore" :format="formatScore"></el-progress>
                <div class="chart-info">
                  <div class="chart-title">综合评分</div>
                  <div class="chart-description">基于所有评价的平均得分</div>
                </div>
              </div>
            </div>
          </el-card>
          
          <!-- 成就荣誉部分 -->
          <el-card class="achievements-card" shadow="hover" size="small">
            <template #header>
              <div class="section-header">
                <el-icon name="Trophy"></el-icon>
                <span class="section-title">成就与荣誉</span>
                <el-button type="primary" size="small" circle @click="addAchievement">
                  <el-icon name="Plus"></el-icon>
                </el-button>
              </div>
            </template>
            
            <div class="achievements-content">
              <el-timeline>
                <el-timeline-item
                  v-for="(achievement, index) in achievements"
                  :key="index"
                  :timestamp="achievement.year"
                  placement="top"
                >
                  <div class="achievement-item">
                    <div class="achievement-title">{{ achievement.title }}</div>
                    <div class="achievement-description">{{ achievement.description }}</div>
                    <div class="achievement-type">
                      <el-tag :type="achievement.type === 'award' ? 'success' : 'primary'">
                        {{ achievement.type === 'award' ? '荣誉奖项' : '教学成果' }}
                      </el-tag>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-card>
        </div>
        
        <!-- 专业发展记录 -->
        <el-card class="professional-section-card" shadow="hover" size="small">
          <template #header>
            <div class="section-header">
              <el-icon name="Reading"></el-icon>
              <span class="section-title">专业发展记录</span>
            </div>
          </template>
          
          <div class="professional-content">
            <el-tabs v-model="activeTab">
              <el-tab-pane label="培训经历" name="training">
                <div class="tab-content">
                  <el-table :data="professionalRecords.training" style="width: 100%" border size="small">
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="name" label="培训名称" min-width="200" />
                    <el-table-column prop="institution" label="培训机构" min-width="150" />
                    <el-table-column prop="startDate" label="开始日期" width="120" />
                    <el-table-column prop="endDate" label="结束日期" width="120" />
                    <el-table-column prop="hours" label="学时" width="80" />
                    <el-table-column prop="status" label="状态" width="100">
                      <template #default="scope">
                        <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'">
                          {{ scope.row.status === 'completed' ? '已完成' : '进行中' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="学术成果" name="academic">
                <div class="tab-content">
                  <el-table :data="professionalRecords.academic" style="width: 100%" border size="small">
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="title" label="成果名称" min-width="200" />
                    <el-table-column prop="type" label="成果类型" width="100">
                      <template #default="scope">
                        <el-tag :type="scope.row.type === 'paper' ? 'primary' : scope.row.type === 'project' ? 'info' : 'success'">
                          {{ scope.row.type === 'paper' ? '论文' : scope.row.type === 'project' ? '项目' : '著作' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="publication" label="发表/完成单位" min-width="150" />
                    <el-table-column prop="date" label="发表/完成日期" width="120" />
                    <el-table-column prop="status" label="状态" width="100">
                      <template #default="scope">
                        <el-tag :type="scope.row.status === 'published' ? 'success' : 'info'">
                          {{ scope.row.status === 'published' ? '已发表' : '已完成' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="教学改革" name="reform">
                <div class="tab-content">
                  <el-table :data="professionalRecords.reform" style="width: 100%" border size="small">
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="title" label="改革项目" min-width="200" />
                    <el-table-column prop="description" label="项目描述" min-width="200" />
                    <el-table-column prop="startDate" label="开始日期" width="120" />
                    <el-table-column prop="endDate" label="结束日期" width="120" />
                    <el-table-column prop="status" label="状态" width="100">
                      <template #default="scope">
                        <el-tag :type="scope.row.status === 'completed' ? 'success' : scope.row.status === 'in_progress' ? 'warning' : 'info'">
                          {{ scope.row.status === 'completed' ? '已完成' : scope.row.status === 'in_progress' ? '进行中' : '规划中' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
        
        <!-- 成长轨迹可视化 -->
        <el-card class="growth-timeline-card" shadow="hover" size="small">
          <template #header>
            <div class="section-header">
              <el-icon name="Calendar"></el-icon>
              <span class="section-title">成长轨迹可视化</span>
            </div>
          </template>
          
          <div class="growth-timeline-content">
            <div class="timeline-chart">
              <div class="timeline-axis"></div>
              <div class="timeline-items">
                <div
                  v-for="(milestone, index) in growthMilestones"
                  :key="index"
                  class="timeline-item"
                  :class="{ 'left': index % 2 === 0, 'right': index % 2 !== 0 }"
                >
                  <div class="timeline-dot"></div>
                  <div class="timeline-content">
                    <div class="timeline-year">{{ milestone.year }}</div>
                    <div class="timeline-event">{{ milestone.event }}</div>
                    <div class="timeline-type">{{ milestone.type }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 添加成就对话框 -->
    <el-dialog v-model="addAchievementDialogVisible" title="添加成就记录" width="50%">
      <el-form :model="newAchievement" :rules="achievementRules" ref="achievementFormRef" label-width="120px">
        <el-form-item label="成就名称" prop="title">
          <el-input v-model="newAchievement.title" placeholder="请输入成就名称" />
        </el-form-item>
        <el-form-item label="成就描述" prop="description">
          <el-input v-model="newAchievement.description" type="textarea" :rows="3" placeholder="请输入成就描述" />
        </el-form-item>
        <el-form-item label="获得年份" prop="year">
          <el-input-number v-model="newAchievement.year" :min="1980" :max="new Date().getFullYear()" placeholder="请输入获得年份" />
        </el-form-item>
        <el-form-item label="成就类型" prop="type">
          <el-radio-group v-model="newAchievement.type">
            <el-radio :label="'award'">荣誉奖项</el-radio>
            <el-radio :label="'achievement'">教学成果</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addAchievementDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitNewAchievement">确认添加</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, FormInstance } from 'element-plus'

// 教师基本信息
const teacherInfo = reactive({
  name: '张老师',
  gender: '女',
  age: 35,
  title: '副教授',
  teachingYears: 10,
  department: '刑事司法学院',
  researchArea: '刑法学、刑事诉讼法学',
  bio: '2010年毕业于中国政法大学，获法学硕士学位。2012年入职广西警察学院，主要从事刑法学和刑事诉讼法学的教学与研究工作。主持参与多项省部级科研项目，发表学术论文10余篇。'
})

// 评价数据统计
const evaluationStats = reactive({
  averageScore: 4.85,
  coursesTaught: 12,
  studentsTaught: 1500,
  excellentRate: 85
})

// 成就与荣誉
const achievements = ref([
  {
    year: '2023年',
    title: '广西警察学院优秀教师',
    description: '在2023年度教学工作中表现突出，被评为学院优秀教师',
    type: 'award'
  },
  {
    year: '2022年',
    title: '广西高等教育教学成果奖二等奖',
    description: '主持的《刑法学实践教学改革研究》项目获得广西高等教育教学成果奖二等奖',
    type: 'achievement'
  },
  {
    year: '2021年',
    title: '广西警察学院教学名师',
    description: '在教学工作中成绩显著，被评为学院教学名师',
    type: 'award'
  },
  {
    year: '2020年',
    title: '全国公安院校教学成果奖三等奖',
    description: '参与的《公安法学实践教学体系构建》项目获得全国公安院校教学成果奖三等奖',
    type: 'achievement'
  }
])

// 专业发展记录
const professionalRecords = reactive({
  training: [
    {
      id: 1,
      name: '刑法学前沿问题研讨班',
      institution: '中国政法大学',
      startDate: '2023-07-15',
      endDate: '2023-07-20',
      hours: 40,
      status: 'completed'
    },
    {
      id: 2,
      name: '高校教师教学能力提升培训',
      institution: '广西师范大学',
      startDate: '2022-08-01',
      endDate: '2022-08-05',
      hours: 30,
      status: 'completed'
    },
    {
      id: 3,
      name: '刑事诉讼法修改专题培训',
      institution: '西南政法大学',
      startDate: '2021-09-10',
      endDate: '2021-09-14',
      hours: 35,
      status: 'completed'
    }
  ],
  academic: [
    {
      id: 1,
      title: '论刑法中的正当防卫制度',
      type: 'paper',
      publication: '广西警察学院学报',
      date: '2023-06-15',
      status: 'published'
    },
    {
      id: 2,
      title: '刑事诉讼法修改对公安工作的影响研究',
      type: 'project',
      publication: '广西公安厅',
      date: '2022-12-30',
      status: 'completed'
    },
    {
      id: 3,
      title: '刑法学案例教程',
      type: 'book',
      publication: '广西人民出版社',
      date: '2021-08-20',
      status: 'published'
    }
  ],
  reform: [
    {
      id: 1,
      title: '刑法学翻转课堂教学改革',
      description: '探索刑法学课程的翻转课堂教学模式，提高学生的学习积极性和参与度',
      startDate: '2023-03-01',
      endDate: '2024-02-28',
      status: 'in_progress'
    },
    {
      id: 2,
      title: '公安法学实践教学体系构建',
      description: '构建适合公安院校特点的法学实践教学体系，提高学生的实践能力',
      startDate: '2021-01-01',
      endDate: '2022-12-31',
      status: 'completed'
    },
    {
      id: 3,
      title: '混合式教学模式在刑事诉讼法中的应用',
      description: '研究混合式教学模式在刑事诉讼法课程中的应用，提高教学效果',
      startDate: '2024-03-01',
      endDate: '2025-02-28',
      status: 'planning'
    }
  ]
})

// 成长里程碑
const growthMilestones = [
  {
    year: '2010年',
    event: '毕业于中国政法大学，获法学硕士学位',
    type: '学业完成'
  },
  {
    year: '2012年',
    event: '入职广西警察学院，担任讲师',
    type: '职业起步'
  },
  {
    year: '2015年',
    event: '晋升为副教授',
    type: '职称晋升'
  },
  {
    year: '2020年',
    event: '获得全国公安院校教学成果奖三等奖',
    type: '教学成果'
  },
  {
    year: '2021年',
    event: '被评为学院教学名师',
    type: '荣誉奖项'
  },
  {
    year: '2022年',
    event: '获得广西高等教育教学成果奖二等奖',
    type: '教学成果'
  },
  {
    year: '2023年',
    event: '被评为学院优秀教师',
    type: '荣誉奖项'
  }
]

// 标签页状态
const activeTab = ref('training')

// 导出档案
const exportGrowthProfile = () => {
  ElMessage.success('个人成长档案导出功能开发中...')
}

// 添加成就对话框
const addAchievementDialogVisible = ref(false)
const achievementFormRef = ref<FormInstance | null>(null)
const newAchievement = reactive({
  title: '',
  description: '',
  year: new Date().getFullYear(),
  type: 'award'
})

const achievementRules = reactive({
  title: [{ required: true, message: '请输入成就名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入成就描述', trigger: 'blur' }],
  year: [{ required: true, message: '请输入获得年份', trigger: 'change' }]
})

const addAchievement = () => {
  addAchievementDialogVisible.value = true
}

const submitNewAchievement = () => {
  if (!achievementFormRef.value) return
  
  achievementFormRef.value.validate((valid) => {
    if (valid) {
      // 添加新成就
      achievements.value.push({
        year: newAchievement.year.toString(),
        title: newAchievement.title,
        description: newAchievement.description,
        type: newAchievement.type
      })
      
      // 关闭对话框并重置表单
      addAchievementDialogVisible.value = false
      achievementFormRef.value?.resetFields()
      
      ElMessage.success('成就记录添加成功')
    }
  })
}

// 格式化评分
const formatScore = (percentage: number) => {
  return percentage.toFixed(2)
}
</script>

<style scoped>
.personal-growth-profile {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.growth-profile-card {
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e9ecef;
}

.growth-profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.growth-profile-title {
  margin-left: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.growth-profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 基本信息部分 */
.info-section-card {
  border-radius: 8px;
}

.section-header {
  display: flex;
  align-items: center;
}

.section-title {
  margin-left: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  min-width: 200px;
}

.info-label {
  font-weight: bold;
  color: #606266;
  margin-right: 8px;
}

.info-value {
  color: #303133;
}

.info-item.full-width {
  flex: 1;
  min-width: 100%;
}

.info-value.description {
  line-height: 1.5;
}

/* 统计部分 */
.stats-section {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stats-card, .achievements-card {
  flex: 1;
  min-width: 300px;
  border-radius: 8px;
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background-color: #f0f9eb;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.2);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #67c23a;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
}

.chart-info {
  text-align: center;
}

.chart-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.chart-description {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
}

/* 成就部分 */
.achievements-content {
  max-height: 300px;
  overflow-y: auto;
}

.achievement-item {
  padding: 15px;
  background-color: #f0f9eb;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.achievement-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.2);
}

.achievement-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.achievement-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
  line-height: 1.5;
}

.achievement-type {
  display: flex;
  justify-content: flex-end;
}

/* 专业发展记录 */
.professional-section-card {
  border-radius: 8px;
}

.professional-content {
  margin-top: 10px;
}

.tab-content {
  margin-top: 15px;
}

/* 成长轨迹可视化 */
.growth-timeline-card {
  border-radius: 8px;
}

.growth-timeline-content {
  margin-top: 10px;
}

.timeline-chart {
  position: relative;
  padding: 20px 0;
}

.timeline-axis {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  background-color: #409eff;
  transform: translateX(-50%);
}

.timeline-items {
  position: relative;
  z-index: 1;
}

.timeline-item {
  position: relative;
  margin-bottom: 40px;
  display: flex;
  align-items: center;
}

.timeline-item.left {
  justify-content: flex-end;
}

.timeline-item.right {
  justify-content: flex-start;
}

.timeline-dot {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  background-color: #409eff;
  border-radius: 50%;
  border: 3px solid #fff;
  box-shadow: 0 0 0 2px #409eff;
  transform: translateY(-50%);
}

.timeline-item.left .timeline-dot {
  right: -8px;
}

.timeline-item.right .timeline-dot {
  left: -8px;
}

.timeline-content {
  width: 45%;
  padding: 15px;
  background-color: #f0f9eb;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.timeline-item.left .timeline-content {
  text-align: right;
  margin-right: 25px;
}

.timeline-item.right .timeline-content {
  margin-left: 25px;
}

.timeline-content:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.2);
}

.timeline-year {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.timeline-event {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
  line-height: 1.5;
}

.timeline-type {
  font-size: 12px;
  color: #909399;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-section {
    flex-direction: column;
  }
  
  .stats-card, .achievements-card {
    min-width: 100%;
  }
  
  .info-row {
    flex-direction: column;
  }
  
  .info-item {
    min-width: 100%;
  }
  
  .timeline-axis {
    left: 30px;
  }
  
  .timeline-item {
    justify-content: flex-start !important;
    margin-left: 30px;
  }
  
  .timeline-dot {
    left: -8px !important;
    right: auto !important;
  }
  
  .timeline-content {
    width: 100% !important;
    margin-left: 25px !important;
    margin-right: 0 !important;
    text-align: left !important;
  }
}
</style>