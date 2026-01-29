<template>
  <div class="dashboard-container">
    <h2>仪表盘</h2>
    
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <h3 class="stat-title">本学期评价</h3>
            <p class="stat-value">{{ currentEvaluationCount }}</p>
            <span class="stat-change positive">+12% 较上学期</span>
          </div>
          <div class="stat-icon success">
            <el-icon name="Document" />
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <h3 class="stat-title">综合评分</h3>
            <p class="stat-value">{{ overallScore }}</p>
            <span class="stat-change positive">+0.8 较上学期</span>
          </div>
          <div class="stat-icon primary">
            <el-icon name="Star" />
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <h3 class="stat-title">待改进项目</h3>
            <p class="stat-value">{{ pendingImprovements }}</p>
            <span class="stat-change negative">-3 较上学期</span>
          </div>
          <div class="stat-icon warning">
            <el-icon name="EditPen" />
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <h3 class="stat-title">学生反馈</h3>
            <p class="stat-value">{{ feedbackCount }}</p>
            <span class="stat-change positive">+25% 较上学期</span>
          </div>
          <div class="stat-icon info">
            <el-icon name="ChatDotRound" />
          </div>
        </div>
      </el-card>
    </div>
    
    <div class="charts-grid">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>评价趋势</span>
            <el-select v-model="timeRange" size="small" placeholder="选择时间范围">
              <el-option label="本学期" value="current" />
              <el-option label="近一年" value="year" />
              <el-option label="近三年" value="three_years" />
            </el-select>
          </div>
        </template>
        <div class="chart-container">
          <div ref="trendChart" class="chart"></div>
        </div>
      </el-card>
      
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>评价维度分析</span>
          </div>
        </template>
        <div class="chart-container">
          <div ref="dimensionChart" class="chart"></div>
        </div>
      </el-card>
    </div>
    
    <div class="recent-activity">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>最近评价</span>
            <el-button type="primary" size="small" @click="viewAllEvaluations">查看全部</el-button>
          </div>
        </template>
        <el-table :data="recentEvaluations" style="width: 100%">
          <el-table-column prop="courseName" label="课程名称" />
          <el-table-column prop="evaluationScore" label="评价得分" width="100">
            <template #default="scope">
              <el-rate v-model="scope.row.evaluationScore" disabled show-score />
            </template>
          </el-table-column>
          <el-table-column prop="evaluationDate" label="评价日期" width="150" />
          <el-table-column prop="studentCount" label="参评人数" width="100" />
          <el-table-column fixed="right" label="操作" width="120">
            <template #default="scope">
              <el-button type="text" size="small" @click="viewEvaluationDetail(scope.row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()

// 统计数据
const currentEvaluationCount = ref(12)
const overallScore = ref(94.5)
const pendingImprovements = ref(2)
const feedbackCount = ref(86)

// 时间范围
const timeRange = ref('current')

// 图表引用
const trendChart = ref<HTMLElement | null>(null)
const dimensionChart = ref<HTMLElement | null>(null)

// 最近评价数据
const recentEvaluations = ref([
  {
    id: 1,
    courseName: '高等数学',
    evaluationScore: 4.8,
    evaluationDate: '2026-01-15',
    studentCount: 45
  },
  {
    id: 2,
    courseName: '大学物理',
    evaluationScore: 4.7,
    evaluationDate: '2026-01-14',
    studentCount: 52
  },
  {
    id: 3,
    courseName: '计算机基础',
    evaluationScore: 4.9,
    evaluationDate: '2026-01-12',
    studentCount: 48
  },
  {
    id: 4,
    courseName: '线性代数',
    evaluationScore: 4.6,
    evaluationDate: '2026-01-10',
    studentCount: 42
  }
])

// 查看所有评价
const viewAllEvaluations = () => {
  router.push('/evaluation')
}

// 查看评价详情
const viewEvaluationDetail = (row: any) => {
  // 跳转到评价详情页面
  console.log('查看评价详情:', row)
}

// 初始化评价趋势图
const initTrendChart = () => {
  if (!trendChart.value) return
  
  const chart = echarts.init(trendChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['第1周', '第2周', '第3周', '第4周', '第5周', '第6周', '第7周', '第8周']
    },
    yAxis: {
      type: 'value',
      min: 80,
      max: 100
    },
    series: [{
      data: [82, 88, 85, 93, 90, 98, 92, 96],
      type: 'line',
      smooth: true,
      lineStyle: {
        width: 5,
        color: '#0f4c81',
        shadowColor: 'rgba(15, 76, 129, 0.5)',
        shadowBlur: 8,
        shadowOffsetY: 3
      },
      areaStyle: {
        opacity: 0.4,
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(15, 76, 129, 0.6)' },
          { offset: 1, color: 'rgba(15, 76, 129, 0.1)' }
        ])
      },
      symbol: 'circle',
      symbolSize: 10,
      itemStyle: {
        color: '#ffd04b',
        borderWidth: 2,
        borderColor: '#0f4c81'
      },
      emphasis: {
        symbolSize: 12,
        itemStyle: {
          color: '#ffd04b',
          borderWidth: 3,
          borderColor: '#0f4c81'
        }
      }
    }]
  }
  
  chart.setOption(option)
}

// 初始化评价维度分析图
const initDimensionChart = () => {
  if (!dimensionChart.value) return
  
  const chart = echarts.init(dimensionChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['教学态度', '教学内容', '教学方法', '教学效果', '作业批改', '课后辅导']
    },
    yAxis: {
      type: 'value',
      min: 80,
      max: 100
    },
    series: [{
      data: [85, 98, 82, 95, 89, 96],
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
}

onMounted(() => {
  initTrendChart()
  initDimensionChart()
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    if (trendChart.value) {
      echarts.init(trendChart.value).resize()
    }
    if (dimensionChart.value) {
      echarts.init(dimensionChart.value).resize()
    }
  })
})
</script>

<style scoped>
/* 数据驱动科技风样式 */
.dashboard-container {
  padding: 0;
  position: relative;
  z-index: 1;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 网格底纹背景 */
.dashboard-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(100, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(100, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  z-index: -1;
  pointer-events: none;
}

.dashboard-container h2 {
  margin-bottom: 20px;
  color: #2c3e50;
  font-family: 'SimHei', '黑体', sans-serif;
  font-weight: bold;
  position: relative;
  padding-bottom: 10px;
}

.dashboard-container h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #00ffff, #ffd700);
  border-radius: 3px;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

/* 玻璃态卡片样式 */
.stat-card {
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(100, 255, 255, 0.3);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2),
    0 0 20px rgba(0, 255, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* 卡片发光效果 */
.stat-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent,
    rgba(100, 255, 255, 0.2),
    transparent
  );
  animation: shimmer 3s linear infinite;
  pointer-events: none;
}

@keyframes shimmer {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 
    0 15px 35px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.3),
    0 0 30px rgba(0, 255, 255, 0.2);
  border-color: rgba(100, 255, 255, 0.6);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
  margin-top: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 更大更醒目的数据数值 */
.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 10px 0;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
}

/* 改进的增减百分比样式 */
.stat-change {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.stat-change.positive {
  color: #27ae60;
  background-color: rgba(39, 174, 96, 0.1);
  box-shadow: 0 0 8px rgba(39, 174, 96, 0.3);
}

.stat-change.negative {
  color: #e74c3c;
  background-color: rgba(231, 76, 60, 0.1);
  box-shadow: 0 0 8px rgba(231, 76, 60, 0.3);
}

/* 科技风图标样式 */
.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  background: rgba(100, 255, 255, 0.1);
  border: 1px solid rgba(100, 255, 255, 0.3);
  box-shadow: 0 0 15px rgba(100, 255, 255, 0.2);
}

.stat-icon.primary {
  background: rgba(100, 255, 255, 0.1);
  color: #00ffff;
  border-color: rgba(100, 255, 255, 0.3);
  box-shadow: 0 0 15px rgba(100, 255, 255, 0.2);
}

.stat-icon.warning {
  background: rgba(255, 215, 0, 0.1);
  color: #ffd700;
  border-color: rgba(255, 215, 0, 0.3);
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
}

.stat-icon.info {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
  border-color: rgba(52, 152, 219, 0.3);
  box-shadow: 0 0 15px rgba(52, 152, 219, 0.2);
}

/* 图表网格 */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 25px;
}

/* 图表卡片 */
.chart-card {
  height: 320px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(100, 255, 255, 0.3);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2),
    0 0 20px rgba(0, 255, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.chart-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent,
    rgba(100, 255, 255, 0.1),
    transparent
  );
  animation: shimmer 4s linear infinite;
  pointer-events: none;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 12px 36px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.3),
    0 0 25px rgba(0, 255, 255, 0.2);
  border-color: rgba(100, 255, 255, 0.5);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 15px;
  position: relative;
  z-index: 1;
}

.card-header span {
  font-weight: bold;
  color: #2c3e50;
  font-family: 'SimHei', '黑体', sans-serif;
  text-shadow: 0 0 5px rgba(255, 255, 0, 0.3);
}

/* 图表容器 */
.chart-container {
  height: calc(100% - 50px);
  padding: 15px;
  position: relative;
  z-index: 1;
}

.chart {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 0, 0.2);
  overflow: hidden;
}

/* 最近活动区域 */
.recent-activity {
  margin-bottom: 25px;
}

.recent-activity .el-card {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 0, 0.3);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2),
    0 0 20px rgba(255, 255, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.recent-activity .el-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent,
    rgba(255, 255, 0, 0.1),
    transparent
  );
  animation: shimmer 5s linear infinite;
  pointer-events: none;
}

.recent-activity .el-card:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 12px 36px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.3),
    0 0 25px rgba(255, 255, 0, 0.2);
  border-color: rgba(255, 255, 0, 0.5);
}

/* 表格样式 */
.recent-activity .el-table {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

.recent-activity .el-table th {
  background: rgba(44, 62, 80, 0.9);
  color: #ffffff;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 0, 0.3);
  text-shadow: 0 0 5px rgba(255, 255, 0, 0.5);
}

.recent-activity .el-table td {
  border-bottom: 1px solid rgba(255, 255, 0, 0.2);
  color: #2c3e50;
}

.recent-activity .el-table__row:hover {
  background: rgba(255, 255, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-value {
    font-size: 30px;
  }
}
</style>