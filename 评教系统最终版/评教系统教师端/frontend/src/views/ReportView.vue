<template>
  <div class="report-container">
    <h2>评价报告</h2>
    
    <el-card class="report-selector" shadow="hover">
      <div class="selector-content">
        <el-form :inline="true" :model="reportForm" class="report-form">
          <el-form-item label="学期">
            <el-select v-model="reportForm.semester" placeholder="选择学期" @change="loadReportData">
              <el-option label="2025-2026学年第一学期" value="2025-2026-1" />
              <el-option label="2024-2025学年第二学期" value="2024-2025-2" />
              <el-option label="2024-2025学年第一学期" value="2024-2025-1" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="报告类型">
            <el-radio-group v-model="reportForm.reportType" @change="loadReportData">
              <el-radio label="个人综合报告" />
              <el-radio label="课程详细报告" />
              <el-radio label="对比分析报告" />
            </el-radio-group>
          </el-form-item>
          
          <el-form-item v-if="reportForm.reportType === '课程详细报告'">
            <el-select v-model="reportForm.courseId" placeholder="选择课程" @change="loadReportData">
              <el-option
                v-for="course in courses"
                :key="course.id"
                :label="course.name"
                :value="course.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="generateReport">生成报告</el-button>
            <el-button @click="exportReport">导出报告</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
    
    <!-- 报告内容 -->
    <el-card class="report-content" shadow="hover" v-if="reportData">
      <!-- 报告头部 -->
      <div class="report-header">
        <h3>{{ reportData.title }}</h3>
        <div class="report-meta">
          <span>报告生成时间：{{ reportData.generatedTime }}</span>
          <span>报告期：{{ reportData.period }}</span>
        </div>
      </div>
      
      <!-- 个人基本信息 -->
      <div class="report-section" v-if="reportData.reportType === '个人综合报告'">
        <h4>一、个人基本信息</h4>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="教师姓名">{{ reportData.teacherInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ reportData.teacherInfo.employeeId }}</el-descriptions-item>
          <el-descriptions-item label="所属院系">{{ reportData.teacherInfo.department }}</el-descriptions-item>
          <el-descriptions-item label="职称">{{ reportData.teacherInfo.title }}</el-descriptions-item>
          <el-descriptions-item label="所授课程数" :span="2">{{ reportData.teacherInfo.courseCount }}门</el-descriptions-item>
          <el-descriptions-item label="总授课学时" :span="2">{{ reportData.teacherInfo.totalHours }}学时</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 综合评价概览 -->
      <div class="report-section">
        <h4>二、综合评价概览</h4>
        <div class="overview-grid">
          <div class="overview-item">
            <div class="overview-label">综合评分</div>
            <div class="overview-value score">{{ reportData.overview.overallScore }}</div>
            <div class="overview-trend" :class="reportData.overview.scoreTrend > 0 ? 'positive' : 'negative'">
              <el-icon :name="reportData.overview.scoreTrend > 0 ? 'ArrowUp' : 'ArrowDown'" />
              {{ Math.abs(reportData.overview.scoreTrend) }}分
            </div>
          </div>
          
          <div class="overview-item">
            <div class="overview-label">课程平均得分</div>
            <div class="overview-value">{{ reportData.overview.averageCourseScore }}</div>
          </div>
          
          <div class="overview-item">
            <div class="overview-label">最高评分课程</div>
            <div class="overview-value">{{ reportData.overview.topCourse.name }}</div>
            <div class="overview-subvalue">{{ reportData.overview.topCourse.score }}分</div>
          </div>
          
          <div class="overview-item">
            <div class="overview-label">最低评分课程</div>
            <div class="overview-value">{{ reportData.overview.bottomCourse.name }}</div>
            <div class="overview-subvalue">{{ reportData.overview.bottomCourse.score }}分</div>
          </div>
        </div>
      </div>
      
      <!-- 评价维度分析 -->
      <div class="report-section">
        <h4>三、评价维度分析</h4>
        <div class="dimension-chart">
          <div ref="dimensionChart" class="chart"></div>
        </div>
        <div class="dimension-table">
          <el-table :data="reportData.dimensionScores" style="width: 100%" border>
            <el-table-column prop="dimension" label="评价维度" width="150" />
            <el-table-column prop="score" label="得分" width="100" />
            <el-table-column prop="rank" label="排名" width="100" />
            <el-table-column prop="trend" label="趋势" width="100">
              <template #default="scope">
                <span :class="scope.row.trend > 0 ? 'positive' : 'negative'">
                  <el-icon :name="scope.row.trend > 0 ? 'ArrowUp' : 'ArrowDown'" />
                  {{ Math.abs(scope.row.trend) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="comment" label="评价" />
          </el-table>
        </div>
      </div>
      
      <!-- 学生反馈摘要 -->
      <div class="report-section">
        <h4>四、学生反馈摘要</h4>
        <div class="feedback-summary">
          <div class="feedback-item">
            <div class="feedback-label">正面反馈（{{ reportData.feedback.positiveCount }}条）</div>
            <div class="feedback-tags">
              <el-tag
                v-for="tag in reportData.feedback.positiveTags"
                :key="tag"
                type="success"
                size="small"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
          
          <div class="feedback-item">
            <div class="feedback-label">建议改进（{{ reportData.feedback.suggestionCount }}条）</div>
            <div class="feedback-tags">
              <el-tag
                v-for="tag in reportData.feedback.suggestionTags"
                :key="tag"
                type="warning"
                size="small"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <!-- 典型反馈示例 -->
        <div class="feedback-examples">
          <h5>典型反馈示例</h5>
          <div class="example-item" v-for="(example, index) in reportData.feedback.examples" :key="index">
            <div class="example-label">{{ example.type === 'positive' ? '正面反馈' : '改进建议' }}</div>
            <div class="example-content">{{ example.content }}</div>
          </div>
        </div>
      </div>
      
      <!-- 改进建议 -->
      <div class="report-section">
        <h4>五、改进建议</h4>
        <el-timeline>
          <el-timeline-item
            v-for="(suggestion, index) in reportData.improvementSuggestions"
            :key="index"
            :timestamp="suggestion.priority"
            placement="top"
          >
            <el-card shadow="hover">
              <h5>{{ suggestion.title }}</h5>
              <p>{{ suggestion.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
      
      <!-- 报告结论 -->
      <div class="report-section">
        <h4>六、报告结论</h4>
        <div class="report-conclusion">
          {{ reportData.conclusion }}
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

// 报告表单
const reportForm = reactive({
  semester: '2025-2026-1',
  reportType: '个人综合报告',
  courseId: '',
  compareWith: 'department' // 与院系对比
})

// 课程列表
const courses = ref([
  { id: 1, name: '高等数学' },
  { id: 2, name: '大学物理' },
  { id: 3, name: '计算机基础' },
  { id: 4, name: '线性代数' },
  { id: 5, name: '数据结构' }
])

// 图表引用
const dimensionChart = ref<HTMLElement | null>(null)

// 报告数据
const reportData = ref<any>(null)

// 加载报告数据
const loadReportData = () => {
  // 模拟加载报告数据
  reportData.value = {
    title: `${reportForm.reportType} - ${reportForm.semester}`,
    generatedTime: '2026-01-20 15:30:00',
    period: reportForm.semester,
    reportType: reportForm.reportType,
    teacherInfo: {
      name: '张老师',
      employeeId: 'T123456',
      department: '计算机学院',
      title: '副教授',
      courseCount: 5,
      totalHours: 240
    },
    overview: {
      overallScore: 94.5,
      scoreTrend: 2.3,
      averageCourseScore: 93.8,
      topCourse: {
        name: '高等数学',
        score: 97.2
      },
      bottomCourse: {
        name: '数据结构',
        score: 91.5
      }
    },
    dimensionScores: [
      { dimension: '教学态度', score: 98, rank: 1, trend: 3, comment: '教学认真负责，态度热情' },
      { dimension: '教学内容', score: 95, rank: 3, trend: 1, comment: '内容丰富，理论与实践结合' },
      { dimension: '教学方法', score: 93, rank: 5, trend: -1, comment: '教学方法多样，但可进一步创新' },
      { dimension: '教学效果', score: 94, rank: 4, trend: 2, comment: '学生学习效果良好' },
      { dimension: '作业批改', score: 92, rank: 6, trend: 0, comment: '批改及时，反馈详细' },
      { dimension: '课后辅导', score: 96, rank: 2, trend: 4, comment: '课后辅导耐心，解答及时' }
    ],
    feedback: {
      positiveCount: 86,
      suggestionCount: 14,
      positiveTags: ['教学认真', '内容丰富', '讲解清晰', '耐心辅导', '关注学生', '互动性强'],
      suggestionTags: ['增加实例', '放慢节奏', '扩展内容', '改进作业', '增加讨论'],
      examples: [
        {
          type: 'positive',
          content: '老师教学认真负责，讲解清晰易懂，对学生非常耐心，是一位优秀的教师。'
        },
        {
          type: 'positive',
          content: '课程内容丰富，理论与实践结合紧密，能够帮助我们更好地理解和应用知识。'
        },
        {
          type: 'suggestion',
          content: '希望老师能够增加更多的实际案例，帮助我们更好地理解抽象的概念。'
        },
        {
          type: 'suggestion',
          content: '课堂节奏可以适当放慢一些，让我们有更多的时间思考和消化。'
        }
      ]
    },
    improvementSuggestions: [
      {
        priority: '高',
        title: '优化教学方法',
        content: '针对数据结构课程，建议增加更多的可视化演示和互动练习，帮助学生更好地理解抽象概念。'
      },
      {
        priority: '中',
        title: '扩展教学内容',
        content: '在高等数学课程中，可以适当引入一些前沿应用案例，提高学生的学习兴趣。'
      },
      {
        priority: '低',
        title: '改进作业设计',
        content: '建议设计更多具有挑战性和创新性的作业，培养学生的独立思考和解决问题的能力。'
      }
    ],
    conclusion: '总体而言，张老师在本报告期内表现优秀，教学质量得到了学生的高度认可。建议继续保持良好的教学态度和方法，同时针对数据结构等课程进一步优化教学策略，提高教学效果。'
  }
  
  // 初始化图表
  setTimeout(() => {
    initDimensionChart()
  }, 100)
}

// 生成报告
const generateReport = () => {
  loadReportData()
}

// 导出报告
const exportReport = () => {
  console.log('导出报告')
  // 这里可以添加导出报告的逻辑
}

// 初始化维度分析图表
const initDimensionChart = () => {
  if (!dimensionChart.value || !reportData.value) return
  
  const chart = echarts.init(dimensionChart.value)
  
  const dimensions = reportData.value.dimensionScores.map((item: any) => item.dimension)
  const scores = reportData.value.dimensionScores.map((item: any) => item.score)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: dimensions
    },
    yAxis: {
      type: 'value',
      min: 80,
      max: 100
    },
    series: [{
      data: scores,
      type: 'bar',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#ffd04b' },
          { offset: 1, color: '#0f4c81' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      emphasis: {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ffc107' },
            { offset: 1, color: '#0a3a66' }
          ])
        }
      },
      barWidth: '60%'
    }]
  }
  
  chart.setOption(option)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 监听报告数据变化
watch(() => reportData.value, () => {
  if (reportData.value) {
    setTimeout(() => {
      initDimensionChart()
    }, 100)
  }
})

onMounted(() => {
  // 默认加载报告数据
  loadReportData()
})
</script>

<style scoped>
.report-container {
  padding: 20px;
  position: relative;
  z-index: 1;
  min-height: 100vh;
  background-color: #f0f2f5;
  background-image: 
    linear-gradient(rgba(15, 76, 129, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15, 76, 129, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  background-position: -1px -1px;
}

.report-container h2 {
  margin-bottom: 30px;
  color: #0f4c81;
  font-family: 'SimHei', '黑体', sans-serif;
  font-weight: bold;
  font-size: 28px;
  position: relative;
  padding-bottom: 15px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.report-container h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #ffd04b, #0f4c81);
  border-radius: 2px;
}

.report-selector {
  margin-bottom: 30px;
  background-color: rgba(255, 255, 255, 0.7);
  border: 2px solid rgba(15, 76, 129, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(15px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.report-selector::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.8s ease;
}

.report-selector:hover {
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
  border-color: rgba(15, 76, 129, 0.4);
  transform: translateY(-2px);
}

.report-selector:hover::before {
  left: 100%;
}

.selector-content {
  display: flex;
  align-items: center;
}

.report-form {
  width: 100%;
}

.report-content {
  margin-bottom: 30px;
  background-color: rgba(255, 255, 255, 0.7);
  border: 2px solid rgba(15, 76, 129, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(15px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.report-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.8s ease;
}

.report-content:hover {
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
  border-color: rgba(15, 76, 129, 0.4);
  transform: translateY(-2px);
}

.report-content:hover::before {
  left: 100%;
}

.report-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(15, 76, 129, 0.2);
  background-color: rgba(15, 76, 129, 0.05);
  border-radius: 10px 10px 0 0;
}

.report-header h3 {
  margin: 0 0 15px 0;
  color: #0f4c81;
  font-family: 'SimHei', '黑体', sans-serif;
  font-size: 24px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.report-meta {
  display: flex;
  justify-content: center;
  gap: 40px;
  color: #606266;
  font-size: 14px;
}

.report-section {
  margin-bottom: 30px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(15, 76, 129, 0.15);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.report-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.8s ease;
}

.report-section:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: rgba(15, 76, 129, 0.25);
  transform: translateY(-2px);
}

.report-section:hover::before {
  left: 100%;
}

.report-section h4 {
  margin: 0 0 20px 0;
  color: #0f4c81;
  border-left: 4px solid #ffd04b;
  padding-left: 15px;
  font-family: 'SimHei', '黑体', sans-serif;
  font-size: 18px;
  font-weight: bold;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.overview-item {
  text-align: center;
  padding: 30px 20px;
  background-color: rgba(255, 255, 255, 0.7);
  border: 2px solid rgba(15, 76, 129, 0.3);
  border-radius: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(15px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.5), 0 0 20px rgba(255, 210, 75, 0.1);
}

.overview-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.6s ease;
}

.overview-item:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.6), 0 0 25px rgba(255, 210, 75, 0.2);
  border-color: rgba(15, 76, 129, 0.5);
  transform: translateY(-4px);
}

.overview-item:hover::before {
  left: 100%;
}

.overview-label {
  font-size: 16px;
  color: #606266;
  margin-bottom: 15px;
  font-weight: 500;
}

.overview-value {
  font-size: 36px;
  font-weight: bold;
  color: #0f4c81;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.overview-value.score {
  color: #0f4c81;
  font-size: 40px;
}

.overview-trend {
  font-size: 14px;
  font-weight: 500;
}

.overview-trend.positive {
  color: rgba(103, 194, 58, 0.8);
}

.overview-trend.negative {
  color: rgba(245, 108, 108, 0.8);
}

.overview-subvalue {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

.dimension-chart {
  height: 350px;
  margin-bottom: 30px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(15, 76, 129, 0.15);
  backdrop-filter: blur(10px);
}

.chart {
  width: 100%;
  height: 100%;
}

.dimension-table {
  margin-top: 30px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(15, 76, 129, 0.15);
  backdrop-filter: blur(10px);
}

.feedback-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.feedback-item {
  padding: 20px;
  background-color: rgba(255, 210, 75, 0.15);
  border: 1px solid rgba(255, 210, 75, 0.3);
  border-radius: 12px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.feedback-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.6s ease;
}

.feedback-item:hover {
  background-color: rgba(255, 210, 75, 0.25);
  border-color: rgba(255, 210, 75, 0.5);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.feedback-item:hover::before {
  left: 100%;
}

.feedback-label {
  font-weight: bold;
  margin-bottom: 15px;
  color: #0f4c81;
  font-size: 16px;
}

.feedback-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.feedback-examples {
  margin-top: 30px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(15, 76, 129, 0.15);
  backdrop-filter: blur(10px);
}

/* 表格样式优化 */
.el-table {
  border-radius: 10px;
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
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

.feedback-examples h5 {
  margin: 0 0 20px 0;
  color: #0f4c81;
  font-size: 18px;
  font-weight: bold;
}

.example-item {
  margin-bottom: 20px;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  border-left: 4px solid #ffd04b;
  border: 1px solid rgba(15, 76, 129, 0.15);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.example-item:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateX(5px);
}

.example-label {
  font-weight: bold;
  margin-bottom: 10px;
  color: #0f4c81;
  font-size: 16px;
}

.example-content {
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

.report-conclusion {
  padding: 25px;
  background-color: rgba(240, 249, 235, 0.8);
  border-radius: 12px;
  border-left: 4px solid rgba(103, 194, 58, 0.8);
  color: #303133;
  line-height: 1.8;
  font-size: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(103, 194, 58, 0.2);
}

.positive {
  color: rgba(103, 194, 58, 0.8);
}

.negative {
  color: rgba(245, 108, 108, 0.8);
}

/* 时间轴样式优化 */
.el-timeline {
  margin-top: 20px;
}

.el-timeline-item__timestamp {
  color: #0f4c81;
  font-weight: bold;
  font-size: 14px;
}

.el-timeline-item__node {
  background-color: #0f4c81;
}

/* 卡片样式优化 */
.el-card {
  border-radius: 12px;
  overflow: hidden;
}

/* 按钮样式优化 */
.el-button--primary {
  background-color: #0f4c81;
  border-color: #0f4c81;
}

.el-button--primary:hover {
  background-color: #1a6aaf;
  border-color: #1a6aaf;
}
</style>