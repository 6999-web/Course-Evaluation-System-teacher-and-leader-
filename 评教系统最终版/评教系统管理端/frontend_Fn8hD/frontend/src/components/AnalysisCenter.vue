<template>
  <div class="analysis-center page-container">
    <div class="content-container">
      <div class="page-title"><i class="el-icon-data-analysis"></i>分析中心</div>
      <el-card>
      <template #header>
        <div class="card-header">
          <span>评价数据分析</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="数据概览" name="overview">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>评价数据概览</span>
              </div>
            </template>
            
            <div class="overview-stats">
              <el-statistic-group>
                <el-statistic 
                  title="总评价人次" 
                  :value="totalEvaluations"
                  :precision="0"
                  :value-style="{ color: '#3f8600' }"
                >
                  <template #suffix>人次</template>
                </el-statistic>
                <el-statistic 
                  title="参与教师数" 
                  :value="totalTeachers"
                  :precision="0"
                  :value-style="{ color: '#1890ff' }"
                >
                  <template #suffix>人</template>
                </el-statistic>
                <el-statistic 
                  title="评价课程数" 
                  :value="totalCourses"
                  :precision="0"
                  :value-style="{ color: '#722ed1' }"
                >
                  <template #suffix>门</template>
                </el-statistic>
                <el-statistic 
                  title="平均满意度" 
                  :value="averageSatisfaction"
                  :precision="1"
                  :value-style="{ color: '#fa541c' }"
                >
                  <template #suffix>%</template>
                </el-statistic>
              </el-statistic-group>
            </div>
            
            <div class="charts-container">
              <el-card class="chart-card">
                <template #header>
                  <span>各院系评价参与率</span>
                </template>
                <div ref="departmentChart" class="chart"></div>
              </el-card>
              
              <el-card class="chart-card">
                <template #header>
                  <span>评价维度分布</span>
                </template>
                <div ref="dimensionChart" class="chart"></div>
              </el-card>
            </div>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="详细分析" name="detail">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>详细数据分析</span>
              </div>
            </template>
            
            <el-form :model="analysisForm" label-width="120px" class="analysis-form">
              <el-form-item label="学年学期">
                <el-select v-model="analysisForm.academicYear" placeholder="选择学年学期">
                  <el-option label="2024-2025-1" value="2024-2025-1"></el-option>
                  <el-option label="2023-2024-2" value="2023-2024-2"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="院系">
                <el-select v-model="analysisForm.department" placeholder="选择院系">
                  <el-option label="计算机学院" value="cs"></el-option>
                  <el-option label="电子工程学院" value="ee"></el-option>
                  <el-option label="人文学院" value="h"></el-option>
                  <el-option label="经管学院" value="jm"></el-option>
                  <el-option label="外语学院" value="fl"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="课程类型">
                <el-select v-model="analysisForm.courseType" placeholder="选择课程类型">
                  <el-option label="必修课" value="compulsory"></el-option>
                  <el-option label="选修课" value="elective"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="analyzeData">分析数据</el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
            
            <div class="analysis-results" v-if="analysisResults.length > 0">
              <h3>分析结果</h3>
              <el-table :data="analysisResults" style="width: 100%">
                <el-table-column prop="courseName" label="课程名称"></el-table-column>
                <el-table-column prop="teacherName" label="教师姓名"></el-table-column>
                <el-table-column prop="evaluationCount" label="评价人数"></el-table-column>
                <el-table-column prop="averageScore" label="平均分">
                  <template #default="scope">
                    <el-rate :value="scope.row.averageScore" disabled :max="5"></el-rate>
                  </template>
                </el-table-column>
                <el-table-column prop="satisfactionRate" label="满意度">
                  <template #default="scope">
                    <el-progress 
                      :percentage="scope.row.satisfactionRate" 
                      :stroke-width="10"
                    ></el-progress>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="趋势分析" name="trend">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>评价趋势分析</span>
              </div>
            </template>
            
            <div class="trend-chart">
              <div ref="trendChart" class="chart large"></div>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';

const activeTab = ref('overview');

// 概览数据
const totalEvaluations = ref(12580);
const totalTeachers = ref(326);
const totalCourses = ref(875);
const averageSatisfaction = ref(85.6);

// 分析表单
const analysisForm = ref({
  academicYear: '2024-2025-1',
  department: '',
  courseType: ''
});

// 分析结果
const analysisResults = ref([
  {
    courseName: '数据结构',
    teacherName: '张三',
    evaluationCount: 120,
    averageScore: 4.8,
    satisfactionRate: 95
  },
  {
    courseName: '操作系统',
    teacherName: '李四',
    evaluationCount: 98,
    averageScore: 4.6,
    satisfactionRate: 92
  },
  {
    courseName: '计算机网络',
    teacherName: '王五',
    evaluationCount: 112,
    averageScore: 4.7,
    satisfactionRate: 94
  },
  {
    courseName: '数据库原理',
    teacherName: '赵六',
    evaluationCount: 105,
    averageScore: 4.5,
    satisfactionRate: 90
  }
]);

// 图表引用
const departmentChart = ref<HTMLElement>();
const dimensionChart = ref<HTMLElement>();
const trendChart = ref<HTMLElement>();

// 初始化图表
const initCharts = () => {
  // 院系评价参与率图表
  if (departmentChart.value) {
    const chart = echarts.init(departmentChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['计算机学院', '电子工程学院', '人文学院', '经管学院', '外语学院']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: '参与率',
          type: 'bar',
          data: [95.2, 88.7, 92.1, 85.3, 89.6],
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }
      ]
    });
  }
  
  // 评价维度分布图表
  if (dimensionChart.value) {
    const chart = echarts.init(dimensionChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '评价维度',
          type: 'pie',
          radius: '70%',
          data: [
            { value: 30, name: '教学态度' },
            { value: 25, name: '教学内容' },
            { value: 20, name: '教学方法' },
            { value: 15, name: '教学效果' },
            { value: 10, name: '其他' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    });
  }
  
  // 趋势分析图表
  if (trendChart.value) {
    const chart = echarts.init(trendChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['评价人次', '平均满意度']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['2023-1', '2023-2', '2024-1', '2024-2', '2025-1']
      },
      yAxis: [
        {
          type: 'value',
          name: '评价人次',
          position: 'left'
        },
        {
          type: 'value',
          name: '满意度',
          position: 'right',
          axisLabel: {
            formatter: '{value}%'
          }
        }
      ],
      series: [
        {
          name: '评价人次',
          type: 'line',
          data: [10200, 11500, 12800, 13200, 12580]
        },
        {
          name: '平均满意度',
          type: 'line',
          yAxisIndex: 1,
          data: [82.5, 83.8, 84.2, 85.0, 85.6]
        }
      ]
    });
  }
};

// 分析数据
const analyzeData = () => {
  ElMessage.success('数据分析完成');
  // 这里可以添加实际的数据分析逻辑
};

// 重置表单
const resetForm = () => {
  analysisForm.value = {
    academicYear: '2024-2025-1',
    department: '',
    courseType: ''
  };
};

// 组件挂载时初始化图表
onMounted(() => {
  initCharts();
  
  // 监听窗口大小变化， resize 图表
  window.addEventListener('resize', () => {
    if (departmentChart.value) {
      echarts.getInstanceByDom(departmentChart.value)?.resize();
    }
    if (dimensionChart.value) {
      echarts.getInstanceByDom(dimensionChart.value)?.resize();
    }
    if (trendChart.value) {
      echarts.getInstanceByDom(trendChart.value)?.resize();
    }
  });
});
</script>

<style scoped>
.analysis-center {
  /* 样式已统一到 App.vue 的 page-container 类 */
}

/* 页面标题和卡片头部样式继承自 App.vue */

.overview-stats {
  margin-bottom: 30px;
}

.overview-stats .el-statistic-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart {
  width: 100%;
  height: 300px;
}

.chart.large {
  height: 400px;
}

.analysis-form {
  margin-bottom: 20px;
}

.analysis-results {
  margin-top: 20px;
}

.trend-chart {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .overview-stats .el-statistic-group {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart {
    height: 250px;
  }
}
</style>
