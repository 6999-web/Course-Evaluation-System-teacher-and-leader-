<template>
  <div class="monitoring-center page-container">
    <div class="content-container">
      <div class="page-title">实时监控中心</div>
      <el-card>
      <template #header>
        <div class="card-header">
          <span>评教进度监控</span>
          <el-button type="primary" @click="refreshData">刷新数据</el-button>
        </div>
      </template>
      
      <div class="dashboard">
        <div class="dashboard-item">
          <h3>全校评教整体进度</h3>
          <div class="progress-circle">
            <el-progress 
              type="dashboard" 
              :percentage="overallProgress" 
              :color="progressColor"
              :stroke-width="15"
            ></el-progress>
            <div class="progress-text">{{ overallProgress.toFixed(1) }}%</div>
          </div>
        </div>
        
        <div class="dashboard-item">
          <h3>院系进度排名</h3>
          <el-table :data="departmentRanking" style="width: 100%">
            <el-table-column prop="name" label="院系名称"></el-table-column>
            <el-table-column prop="rate" label="参评率">
              <template #default="scope">
                <el-progress :percentage="scope.row.rate" :stroke-width="8"></el-progress>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="dashboard-item">
          <h3>异常课程预警</h3>
          <el-table :data="warningCourses" style="width: 100%">
            <el-table-column prop="course_code" label="课程代码"></el-table-column>
            <el-table-column prop="issue" label="问题描述"></el-table-column>
            <el-table-column prop="level" label="预警等级">
              <template #default="scope">
                <el-tag :type="scope.row.level === 'high' ? 'danger' : 'warning'">
                  {{ scope.row.level === 'high' ? '高' : '中' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      
      <div class="chart-container">
        <h3>实时参评率趋势图</h3>
        <div ref="trendChart" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const overallProgress = ref(0);
const progressColor = ref('#409EFF');
const departmentRanking = ref([
  { name: '计算机学院', rate: 89.2 },
  { name: '电子工程学院', rate: 85.6 },
  { name: '人文学院', rate: 78.9 },
  { name: '经管学院', rate: 75.3 },
  { name: '外语学院', rate: 72.1 }
]);
const warningCourses = ref([
  { course_code: 'CS101', issue: '参评率<50%', level: 'high' },
  { course_code: 'EE202', issue: '出现批量异常评分', level: 'medium' },
  { course_code: 'H303', issue: '参评率<60%', level: 'medium' }
]);
const trendChart = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;
let ws: WebSocket | null = null;

const refreshData = async () => {
  try {
    const response = await fetch('http://120.26.29.145:8000/monitoring/dashboard?academic_year=2024-2025-1');
    if (response.ok) {
      const data = await response.json();
      overallProgress.value = data.overall_progress;
      departmentRanking.value = data.department_ranking || departmentRanking.value;
      warningCourses.value = data.warning_courses || warningCourses.value;
      updateProgressColor();
    }
  } catch (error) {
    console.error('刷新数据失败:', error);
  }
};

const updateProgressColor = () => {
  if (overallProgress.value < 50) {
    progressColor.value = '#F56C6C';
  } else if (overallProgress.value < 80) {
    progressColor.value = '#E6A23C';
  } else {
    progressColor.value = '#67C23A';
  }
};

const initChart = () => {
  if (trendChart.value) {
    chartInstance = echarts.init(trendChart.value);
    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}%'
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
        data: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: '参评率',
          type: 'line',
          data: [12, 25, 38, 45, 52, 63, 71, 78, 85],
          smooth: true,
          itemStyle: {
            color: '#409EFF'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ])
          }
        }
      ]
    };
    chartInstance.setOption(option);
  }
};

const connectWebSocket = () => {
  ws = new WebSocket('ws://120.26.29.145:8000/ws/monitoring/all');
  
  ws.onopen = () => {
    console.log('WebSocket连接成功');
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'REALTIME_UPDATE') {
        overallProgress.value = data.data.overall_progress;
        departmentRanking.value = data.data.department_ranking || departmentRanking.value;
        warningCourses.value = data.data.warning_courses || warningCourses.value;
        updateProgressColor();
      }
    } catch (error) {
      console.error('解析WebSocket消息失败:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket错误:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket连接关闭');
  };
};

onMounted(() => {
  refreshData();
  initChart();
  connectWebSocket();
  
  window.addEventListener('resize', () => {
    chartInstance?.resize();
  });
});

onUnmounted(() => {
  if (ws) {
    ws.close();
  }
  if (chartInstance) {
    chartInstance.dispose();
  }
  window.removeEventListener('resize', () => {
    chartInstance?.resize();
  });
});
</script>

<style scoped>
.monitoring-center {
  /* 样式已统一到 App.vue 的 page-container 类 */
}


/* 卡片头部样式继承自 App.vue */


.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.dashboard-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.dashboard-item h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 16px;
  color: #333;
}

.progress-circle {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.chart-container {
  margin-top: 30px;
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 16px;
  color: #333;
}

.chart {
  width: 100%;
  height: 400px;
}
</style>