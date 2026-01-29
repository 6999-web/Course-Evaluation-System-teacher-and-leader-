<template>
  <div class="evaluation-trend-prediction">
    <!-- 评教趋势预测主卡片 -->
    <el-card class="trend-prediction-card" shadow="hover">
      <template #header>
        <div class="trend-prediction-header">
          <el-icon name="TrendCharts"></el-icon>
          <span class="trend-prediction-title">评教趋势预测</span>
          <el-button type="primary" size="small" @click="generatePredictionReport">
            <el-icon name="Document"></el-icon>生成预测报告
          </el-button>
        </div>
      </template>
      
      <div class="trend-prediction-content">
        <!-- 筛选和配置区域 -->
        <div class="filter-config-section">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="课程选择" label-width="80px">
                <el-select v-model="selectedCourse" placeholder="请选择课程" size="large">
                  <el-option label="所有课程" value="all" />
                  <el-option v-for="course in availableCourses" :key="course.id" :label="course.name" :value="course.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="时间范围" label-width="80px">
                <el-select v-model="timeRange" placeholder="请选择时间范围" size="large">
                  <el-option label="近1年" value="1y" />
                  <el-option label="近2年" value="2y" />
                  <el-option label="近3年" value="3y" />
                  <el-option label="全部" value="all" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="预测时长" label-width="80px">
                <el-select v-model="predictionPeriod" placeholder="请选择预测时长" size="large">
                  <el-option label="1学期" value="1" />
                  <el-option label="2学期" value="2" />
                  <el-option label="1年" value="4" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="预测维度" label-width="80px">
                <el-checkbox-group v-model="selectedDimensions" size="large">
                  <el-checkbox label="教学态度">教学态度</el-checkbox>
                  <el-checkbox label="教学内容">教学内容</el-checkbox>
                  <el-checkbox label="教学方法">教学方法</el-checkbox>
                  <el-checkbox label="教学效果">教学效果</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" size="large" @click="generateTrendPrediction" :loading="isGenerating">
                <el-icon name="Refresh"></el-icon>生成趋势预测
              </el-button>
            </el-col>
          </el-row>
        </div>
        
        <!-- 预测结果概览 -->
        <el-card class="overview-card" shadow="hover" size="small" v-if="predictionResults">
          <template #header>
            <div class="section-header">
              <el-icon name="InfoFilled"></el-icon>
              <span class="section-title">预测结果概览</span>
            </div>
          </template>
          
          <div class="overview-content">
            <div class="overview-stats">
              <div class="overview-stat-item">
                <div class="overview-stat-label">当前平均评分</div>
                <div class="overview-stat-value">{{ currentAverageScore.toFixed(2) }}</div>
              </div>
              <div class="overview-stat-item">
                <div class="overview-stat-label">预测平均评分</div>
                <div class="overview-stat-value prediction" :class="{ 'positive': predictionResults.predictedAverageScore > currentAverageScore, 'negative': predictionResults.predictedAverageScore < currentAverageScore }">
                  {{ predictionResults.predictedAverageScore.toFixed(2) }}
                  <span class="trend-indicator">
                    <el-icon name="ArrowUpBold" v-if="predictionResults.predictedAverageScore > currentAverageScore" class="positive"></el-icon>
                    <el-icon name="ArrowDownBold" v-else-if="predictionResults.predictedAverageScore < currentAverageScore" class="negative"></el-icon>
                    <el-icon name="Minus" v-else></el-icon>
                  </span>
                </div>
              </div>
              <div class="overview-stat-item">
                <div class="overview-stat-label">变化趋势</div>
                <div class="overview-stat-value">
                  <el-tag :type="predictionResults.trend === 'up' ? 'success' : predictionResults.trend === 'down' ? 'danger' : 'warning'">
                    {{ predictionResults.trend === 'up' ? '上升' : predictionResults.trend === 'down' ? '下降' : '平稳' }}
                  </el-tag>
                </div>
              </div>
              <div class="overview-stat-item">
                <div class="overview-stat-label">预测置信度</div>
                <div class="overview-stat-value">{{ predictionResults.confidenceLevel }}%</div>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 趋势图展示区域 -->
        <div class="trend-chart-section" v-if="predictionResults">
          <el-card class="chart-card" shadow="hover" size="small">
            <template #header>
              <div class="section-header">
                <el-icon name="DataAnalysis"></el-icon>
                <span class="section-title">评分趋势图</span>
              </div>
            </template>
            
            <div class="chart-content">
              <div class="chart-placeholder">
                <!-- 这里可以替换为实际的图表库，如 ECharts 或 Chart.js -->
                <div class="mock-chart">
                  <div class="chart-axes">
                    <div class="x-axis">
                      <div class="axis-label" v-for="(period, index) in allPeriods" :key="index">{{ period }}</div>
                    </div>
                    <div class="y-axis">
                      <div class="axis-label">5.0</div>
                      <div class="axis-label">4.5</div>
                      <div class="axis-label">4.0</div>
                      <div class="axis-label">3.5</div>
                      <div class="axis-label">3.0</div>
                    </div>
                  </div>
                  
                  <div class="chart-lines">
                    <!-- 历史数据折线 -->
                    <svg class="chart-svg" width="100%" height="100%" viewBox="0 0 800 400">
                      <defs>
                        <linearGradient id="historyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                          <stop offset="0%" :style="'stop-color:#409eff;stop-opacity:0.8'" />
                          <stop offset="100%" :style="'stop-color:#409eff;stop-opacity:0.2'" />
                        </linearGradient>
                        <linearGradient id="predictionGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                          <stop offset="0%" :style="'stop-color:#67c23a;stop-opacity:0.8'" />
                          <stop offset="100%" :style="'stop-color:#67c23a;stop-opacity:0.2'" />
                        </linearGradient>
                      </defs>
                      
                      <!-- 历史数据路径 -->
                      <path 
                        :d="historyDataPath" 
                        fill="url(#historyGradient)" 
                        stroke="#409eff" 
                        stroke-width="2"
                      />
                      
                      <!-- 预测数据路径 -->
                      <path 
                        :d="predictionDataPath" 
                        fill="url(#predictionGradient)" 
                        stroke="#67c23a" 
                        stroke-width="2"
                        stroke-dasharray="5,5"
                      />
                      
                      <!-- 历史数据点 -->
                      <circle 
                        v-for="(point, index) in historicalData" 
                        :key="'history-' + index"
                        :cx="index * 100 + 50" 
                        :cy="400 - (point.score * 60 + 100)" 
                        r="4" 
                        fill="#409eff" 
                        stroke="white"
                        stroke-width="2"
                      />
                      
                      <!-- 预测数据点 -->
                      <circle 
                        v-for="(point, index) in predictedData" 
                        :key="'prediction-' + index"
                        :cx="(historicalData.length + index) * 100 + 50" 
                        :cy="400 - (point.score * 60 + 100)" 
                        r="4" 
                        fill="#67c23a" 
                        stroke="white"
                        stroke-width="2"
                      />
                    </svg>
                  </div>
                  
                  <div class="chart-legend">
                    <div class="legend-item">
                      <div class="legend-color history"></div>
                      <span class="legend-text">历史数据</span>
                    </div>
                    <div class="legend-item">
                      <div class="legend-color prediction"></div>
                      <span class="legend-text">预测数据</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 维度分析和预测区域 -->
        <div class="dimension-analysis-section" v-if="predictionResults">
          <el-card class="dimension-card" shadow="hover" size="small">
            <template #header>
              <div class="section-header">
                <el-icon name="Grid"></el-icon>
                <span class="section-title">维度分析与预测</span>
              </div>
            </template>
            
            <div class="dimension-content">
              <el-row :gutter="20">
                <el-col :span="12" v-for="(dimension, index) in dimensionPredictions" :key="index">
                  <div class="dimension-item">
                    <div class="dimension-header">
                      <div class="dimension-name">{{ dimension.name }}</div>
                      <el-tag :type="dimension.trend === 'up' ? 'success' : dimension.trend === 'down' ? 'danger' : 'warning'">
                        {{ dimension.trend === 'up' ? '上升' : dimension.trend === 'down' ? '下降' : '平稳' }}
                      </el-tag>
                    </div>
                    <div class="dimension-chart">
                      <div class="dimension-bars">
                        <div class="bar-group">
                          <div class="bar-label">历史</div>
                          <div class="bar-container">
                            <div 
                              class="bar history" 
                              :style="'width: ' + (dimension.historicalScore / 5 * 100) + '%'"
                              :title="dimension.historicalScore.toFixed(2)"
                            ></div>
                          </div>
                          <div class="bar-value">{{ dimension.historicalScore.toFixed(2) }}</div>
                        </div>
                        <div class="bar-group">
                          <div class="bar-label">预测</div>
                          <div class="bar-container">
                            <div 
                              class="bar prediction" 
                              :style="'width: ' + (dimension.predictedScore / 5 * 100) + '%'"
                              :title="dimension.predictedScore.toFixed(2)"
                            ></div>
                          </div>
                          <div class="bar-value">{{ dimension.predictedScore.toFixed(2) }}</div>
                        </div>
                      </div>
                    </div>
                    <div class="dimension-improvement">
                      <div class="improvement-title">改进建议：</div>
                      <div class="improvement-content">{{ dimension.improvementSuggestion }}</div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </div>
        
        <!-- 预测影响因素分析 -->
        <el-card class="factors-card" shadow="hover" size="small" v-if="predictionResults">
          <template #header>
            <div class="section-header">
              <el-icon name="WarningFilled"></el-icon>
              <span class="section-title">预测影响因素分析</span>
            </div>
          </template>
          
          <div class="factors-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="主要影响因素">
                <el-tag type="info" size="small" v-for="factor in predictionResults.keyInfluencingFactors" :key="factor">{{ factor }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="风险预警">
                <el-tag type="danger" size="small" v-for="risk in predictionResults.riskWarnings" :key="risk">{{ risk }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="机遇识别">
                <el-tag type="success" size="small" v-for="opportunity in predictionResults.opportunities" :key="opportunity">{{ opportunity }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="关键指标">
                <el-tag type="primary" size="small" v-for="metric in predictionResults.keyMetrics" :key="metric">{{ metric }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
        
        <!-- 预测建议和行动方案 -->
        <el-card class="recommendations-card" shadow="hover" size="small" v-if="predictionResults">
          <template #header>
            <div class="section-header">
              <el-icon name="Tips"></el-icon>
              <span class="section-title">预测建议和行动方案</span>
            </div>
          </template>
          
          <div class="recommendations-content">
            <el-collapse v-model="activeCollapseNames" accordion>
              <el-collapse-item title="短期行动建议（1-2个月）" name="short-term">
                <el-list>
                  <el-list-item v-for="(item, index) in predictionResults.recommendations.shortTerm" :key="index">
                    <el-icon name="Check"></el-icon>
                    {{ item }}
                  </el-list-item>
                </el-list>
              </el-collapse-item>
              <el-collapse-item title="中期行动方案（3-6个月）" name="medium-term">
                <el-list>
                  <el-list-item v-for="(item, index) in predictionResults.recommendations.mediumTerm" :key="index">
                    <el-icon name="Check"></el-icon>
                    {{ item }}
                  </el-list-item>
                </el-list>
              </el-collapse-item>
              <el-collapse-item title="长期发展规划（6-12个月）" name="long-term">
                <el-list>
                  <el-list-item v-for="(item, index) in predictionResults.recommendations.longTerm" :key="index">
                    <el-icon name="Check"></el-icon>
                    {{ item }}
                  </el-list-item>
                </el-list>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 生成预测报告对话框 -->
    <el-dialog v-model="reportDialogVisible" title="评教趋势预测报告" width="70%" destroy-on-close>
      <div class="report-content" v-if="predictionReport">
        <div class="report-header">
          <h2>{{ predictionReport.title }}</h2>
          <div class="report-meta">
            <span class="meta-item">生成时间：{{ predictionReport.generatedTime }}</span>
            <span class="meta-item">课程：{{ predictionReport.courseName }}</span>
            <span class="meta-item">预测时长：{{ predictionReport.predictionPeriod }}</span>
          </div>
        </div>
        
        <div class="report-section">
          <h3>一、预测结果摘要</h3>
          <p>{{ predictionReport.summary }}</p>
        </div>
        
        <div class="report-section">
          <h3>二、趋势分析</h3>
          <p>{{ predictionReport.trendAnalysis }}</p>
        </div>
        
        <div class="report-section">
          <h3>三、维度预测详情</h3>
          <table class="report-table">
            <thead>
              <tr>
                <th>评价维度</th>
                <th>历史评分</th>
                <th>预测评分</th>
                <th>变化趋势</th>
                <th>改进建议</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(dimension, index) in predictionReport.dimensionDetails" :key="index">
                <td>{{ dimension.name }}</td>
                <td>{{ dimension.historicalScore }}</td>
                <td>{{ dimension.predictedScore }}</td>
                <td>
                  <el-tag :type="dimension.trend === 'up' ? 'success' : dimension.trend === 'down' ? 'danger' : 'warning'">
                    {{ dimension.trend === 'up' ? '上升' : dimension.trend === 'down' ? '下降' : '平稳' }}
                  </el-tag>
                </td>
                <td>{{ dimension.improvementSuggestion }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="report-section">
          <h3>四、影响因素分析</h3>
          <div class="factors-grid">
            <div class="factor-group">
              <h4>主要影响因素</h4>
              <div class="factor-list">
                <el-tag type="info" size="small" v-for="factor in predictionReport.keyInfluencingFactors" :key="factor">{{ factor }}</el-tag>
              </div>
            </div>
            <div class="factor-group">
              <h4>风险预警</h4>
              <div class="factor-list">
                <el-tag type="danger" size="small" v-for="risk in predictionReport.riskWarnings" :key="risk">{{ risk }}</el-tag>
              </div>
            </div>
            <div class="factor-group">
              <h4>机遇识别</h4>
              <div class="factor-list">
                <el-tag type="success" size="small" v-for="opportunity in predictionReport.opportunities" :key="opportunity">{{ opportunity }}</el-tag>
              </div>
            </div>
          </div>
        </div>
        
        <div class="report-section">
          <h3>五、行动建议</h3>
          <div class="recommendations-grid">
            <div class="recommendation-group">
              <h4>短期行动建议（1-2个月）</h4>
              <ul>
                <li v-for="(item, index) in predictionReport.recommendations.shortTerm" :key="index">{{ item }}</li>
              </ul>
            </div>
            <div class="recommendation-group">
              <h4>中期行动方案（3-6个月）</h4>
              <ul>
                <li v-for="(item, index) in predictionReport.recommendations.mediumTerm" :key="index">{{ item }}</li>
              </ul>
            </div>
            <div class="recommendation-group">
              <h4>长期发展规划（6-12个月）</h4>
              <ul>
                <li v-for="(item, index) in predictionReport.recommendations.longTerm" :key="index">{{ item }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="reportDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="downloadReport">下载报告</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

// 筛选条件
const selectedCourse = ref('all')
const timeRange = ref('2y')
const predictionPeriod = ref('2')
const selectedDimensions = ref(['教学态度', '教学内容', '教学方法', '教学效果'])

// 生成状态
const isGenerating = ref(false)

// 可用课程
const availableCourses = ref([
  { id: 1, name: '刑法学' },
  { id: 2, name: '刑事诉讼法' },
  { id: 3, name: '治安管理学' },
  { id: 4, name: '犯罪心理学' },
  { id: 5, name: '警察法学' }
])

// 历史数据
const historicalData = ref([
  { period: '2021春', score: 4.5 },
  { period: '2021秋', score: 4.6 },
  { period: '2022春', score: 4.4 },
  { period: '2022秋', score: 4.7 },
  { period: '2023春', score: 4.8 },
  { period: '2023秋', score: 4.9 },
  { period: '2024春', score: 4.85 }
])

// 预测数据
const predictedData = ref([
  { period: '2024秋', score: 4.92 },
  { period: '2025春', score: 4.95 }
])

// 预测结果
const predictionResults = ref<any>(null)

// 当前平均评分
const currentAverageScore = computed(() => {
  if (historicalData.value.length === 0) return 0
  const sum = historicalData.value.reduce((acc, item) => acc + item.score, 0)
  return sum / historicalData.value.length
})

// 所有时间段
const allPeriods = computed(() => {
  return [...historicalData.value.map(item => item.period), ...predictedData.value.map(item => item.period)]
})

// 历史数据路径
const historyDataPath = computed(() => {
  if (historicalData.value.length === 0) return ''
  
  let path = `M 50 ${400 - (historicalData.value[0].score * 60 + 100)}`
  for (let i = 1; i < historicalData.value.length; i++) {
    path += ` L ${i * 100 + 50} ${400 - (historicalData.value[i].score * 60 + 100)}`
  }
  path += ` L ${(historicalData.value.length - 1) * 100 + 50} 400 L 50 400 Z`
  return path
})

// 预测数据路径
const predictionDataPath = computed(() => {
  if (predictedData.value.length === 0 || historicalData.value.length === 0) return ''
  
  const startX = (historicalData.value.length - 1) * 100 + 50
  const startY = 400 - (historicalData.value[historicalData.value.length - 1].score * 60 + 100)
  
  let path = `M ${startX} ${startY}`
  for (let i = 0; i < predictedData.value.length; i++) {
    const x = (historicalData.value.length + i) * 100 + 50
    const y = 400 - (predictedData.value[i].score * 60 + 100)
    path += ` L ${x} ${y}`
  }
  path += ` L ${(historicalData.value.length + predictedData.value.length - 1) * 100 + 50} 400 L ${startX} 400 Z`
  return path
})

// 维度预测
const dimensionPredictions = ref([
  {
    name: '教学态度',
    historicalScore: 4.9,
    predictedScore: 4.95,
    trend: 'up',
    improvementSuggestion: '保持良好的教学态度，继续增强与学生的互动交流'
  },
  {
    name: '教学内容',
    historicalScore: 4.8,
    predictedScore: 4.85,
    trend: 'up',
    improvementSuggestion: '建议增加更多实际案例分析，结合最新的学术研究成果'
  },
  {
    name: '教学方法',
    historicalScore: 4.7,
    predictedScore: 4.82,
    trend: 'up',
    improvementSuggestion: '继续优化教学方法，增加更多互动式教学环节'
  },
  {
    name: '教学效果',
    historicalScore: 4.9,
    predictedScore: 4.93,
    trend: 'up',
    improvementSuggestion: '保持当前的教学效果，关注学生的学习反馈'
  }
])

// 折叠面板状态
const activeCollapseNames = ref(['short-term'])

// 预测报告
const predictionReport = ref<any>(null)
const reportDialogVisible = ref(false)

// 生成趋势预测
const generateTrendPrediction = () => {
  isGenerating.value = true
  
  // 模拟生成预测结果
  setTimeout(() => {
    predictionResults.value = {
      currentAverageScore: currentAverageScore.value,
      predictedAverageScore: 4.93,
      trend: 'up',
      confidenceLevel: 92,
      keyInfluencingFactors: ['教学方法创新', '学生参与度', '课程内容更新'],
      riskWarnings: ['部分学生对作业难度的反馈'],
      opportunities: ['引入更多案例教学', '加强实践环节'],
      keyMetrics: ['平均评分', '优秀率', '学生满意度'],
      dimensionPredictions: dimensionPredictions.value
    }
    
    isGenerating.value = false
    ElMessage.success('评教趋势预测生成成功')
  }, 1500)
}

// 生成预测报告
const generatePredictionReport = () => {
  if (!predictionResults.value) {
    ElMessage.warning('请先生成趋势预测')
    return
  }
  
  // 模拟生成报告
  isGenerating.value = true
  
  setTimeout(() => {
    predictionReport.value = {
      title: '评教趋势预测报告',
      generatedTime: new Date().toLocaleString(),
      courseName: selectedCourse.value === 'all' ? '所有课程' : availableCourses.value.find(c => c.id === Number(selectedCourse.value))?.name || '',
      predictionPeriod: `${predictionPeriod.value}个学期`,
      summary: '根据历史评教数据，预测未来2个学期的评教评分将呈现上升趋势，平均评分预计从当前的4.85分提升至4.93分，整体教学效果良好。',
      trendAnalysis: '从历史数据来看，近3年来评教评分呈现稳步上升趋势，特别是在教学方法和教学内容方面的改进取得了显著效果。预计未来2个学期，在保持现有优势的基础上，通过进一步优化教学方法和内容，评分将继续提升。',
      dimensionDetails: dimensionPredictions.value,
      recommendations: {
        shortTerm: [
          '继续保持良好的教学态度，增强与学生的互动交流',
          '针对学生反馈的作业难度问题进行调整',
          '增加更多案例分析和实践环节'
        ],
        mediumTerm: [
          '引入新的教学技术和方法，如翻转课堂等',
          '结合最新的学术研究成果更新课程内容',
          '建立学生学习效果跟踪机制'
        ],
        longTerm: [
          '构建完整的课程教学体系',
          '加强与同行的交流与合作',
          '开展教学改革研究项目'
        ]
      },
      keyInfluencingFactors: ['教学方法创新', '学生参与度', '课程内容更新'],
      riskWarnings: ['部分学生对作业难度的反馈'],
      opportunities: ['引入更多案例教学', '加强实践环节']
    }
    
    reportDialogVisible.value = true
    isGenerating.value = false
    ElMessage.success('预测报告生成成功')
  }, 2000)
}

// 下载报告
const downloadReport = () => {
  ElMessage.success('报告下载功能开发中...')
}

// 生成默认预测结果
watch(() => selectedCourse.value, (newVal) => {
  if (newVal) {
    generateTrendPrediction()
  }
}, { immediate: true })
</script>

<style scoped>
.evaluation-trend-prediction {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.trend-prediction-card {
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e9ecef;
}

.trend-prediction-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.trend-prediction-title {
  margin-left: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.trend-prediction-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 筛选和配置区域 */
.filter-config-section {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

/* 概览卡片 */
.overview-card {
  border-radius: 8px;
}

.overview-content {
  margin-top: 10px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.overview-stat-item {
  text-align: center;
  padding: 15px;
  background-color: #f0f9eb;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.overview-stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.2);
}

.overview-stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.overview-stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.overview-stat-value.prediction {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.trend-indicator {
  font-size: 18px;
}

.trend-indicator .positive {
  color: #67c23a;
}

.trend-indicator .negative {
  color: #f56c6c;
}

/* 趋势图卡片 */
.chart-card {
  border-radius: 8px;
}

.chart-content {
  margin-top: 10px;
}

.chart-placeholder {
  height: 400px;
  background-color: #fafafa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.mock-chart {
  width: 100%;
  height: 100%;
  position: relative;
}

.chart-axes {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.x-axis {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #e0e0e0;
  display: flex;
  justify-content: space-between;
  padding: 0 50px;
}

.y-axis {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 1px;
  background-color: #e0e0e0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 0;
}

.axis-label {
  font-size: 12px;
  color: #909399;
  position: absolute;
}

.x-axis .axis-label {
  bottom: -20px;
  transform: translateX(-50%);
}

.y-axis .axis-label {
  left: -30px;
  transform: translateY(-50%);
}

.chart-lines {
  width: 100%;
  height: 100%;
  position: relative;
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-color {
  width: 15px;
  height: 15px;
  border-radius: 3px;
}

.legend-color.history {
  background-color: #409eff;
}

.legend-color.prediction {
  background-color: #67c23a;
}

.legend-text {
  font-size: 14px;
  color: #606266;
}

/* 维度分析卡片 */
.dimension-card {
  border-radius: 8px;
}

.dimension-content {
  margin-top: 10px;
}

.dimension-item {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  transition: all 0.3s ease;
}

.dimension-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.dimension-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.dimension-chart {
  margin-bottom: 15px;
}

.dimension-bars {
  display: flex;
  gap: 20px;
  align-items: flex-end;
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.bar-label {
  font-size: 14px;
  color: #606266;
  font-weight: bold;
}

.bar-container {
  width: 100%;
  height: 100px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 100%;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
}

.bar.history {
  background-color: #409eff;
}

.bar.prediction {
  background-color: #67c23a;
}

.bar-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.dimension-improvement {
  margin-top: 10px;
}

.improvement-title {
  font-weight: bold;
  color: #606266;
  margin-bottom: 5px;
}

.improvement-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
}

/* 影响因素卡片 */
.factors-card {
  border-radius: 8px;
}

.factors-content {
  margin-top: 10px;
}

/* 建议卡片 */
.recommendations-card {
  border-radius: 8px;
}

.recommendations-content {
  margin-top: 10px;
}

/* 报告对话框 */
.report-content {
  max-height: 600px;
  overflow-y: auto;
  padding: 20px;
}

.report-header {
  margin-bottom: 30px;
  text-align: center;
}

.report-header h2 {
  margin-bottom: 10px;
  color: #303133;
}

.report-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 14px;
  color: #606266;
}

.report-section {
  margin-bottom: 30px;
}

.report-section h3 {
  color: #303133;
  margin-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 5px;
}

.report-section p {
  line-height: 1.6;
  color: #606266;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

.report-table th, .report-table td {
  padding: 12px;
  border: 1px solid #e9ecef;
  text-align: left;
}

.report-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #303133;
}

.report-table td {
  color: #606266;
}

.factors-grid, .recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.factor-group, .recommendation-group {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}

.factor-group h4, .recommendation-group h4 {
  color: #303133;
  margin-bottom: 10px;
}

.factor-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.recommendation-group ul {
  padding-left: 20px;
}

.recommendation-group li {
  margin-bottom: 5px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dimension-bars {
    flex-direction: column;
    gap: 10px;
  }
  
  .bar-container {
    height: 30px;
  }
  
  .factors-grid, .recommendations-grid {
    grid-template-columns: 1fr;
  }
}
</style>