<template>
  <div class="application-center page-container">
    <div class="content-container">
      <div class="page-title">结果应用中心</div>
      <el-card>
      <template #header>
        <div class="card-header">
          <span>评教结果应用</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="结果分发管理" name="distribute">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>分发评价结果</span>
                <el-button type="primary" @click="distributeResults">分发结果</el-button>
              </div>
            </template>
            
            <el-form :model="distributeForm" label-width="120px" class="distribute-form">
              <el-form-item label="选择报告">
                <el-select v-model="distributeForm.report_ids" multiple placeholder="选择要分发的报告">
                  <el-option v-for="report in availableReports" :key="report.report_id" :label="report.report_name" :value="report.report_id"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="目标角色">
                <el-select v-model="distributeForm.target_roles" multiple placeholder="选择目标角色">
                  <el-option label="校级管理员" value="admin"></el-option>
                  <el-option label="院系管理员" value="dept_admin"></el-option>
                  <el-option label="教学督导" value="supervisor"></el-option>
                  <el-option label="教师" value="teacher"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="通知方式">
                <el-checkbox-group v-model="distributeForm.notify_type">
                  <el-checkbox :label="'邮件'">邮件</el-checkbox>
                  <el-checkbox :label="'站内信'">站内信</el-checkbox>
                  <el-checkbox :label="'短信'">短信</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="分发说明">
                <el-input v-model="distributeForm.description" type="textarea" placeholder="输入分发说明"></el-input>
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>分发记录</span>
              </div>
            </template>
            
            <el-table :data="distributionRecords" style="width: 100%">
              <el-table-column prop="distribution_id" label="分发ID"></el-table-column>
              <el-table-column prop="report_names" label="分发报告"></el-table-column>
              <el-table-column prop="target_roles" label="目标角色"></el-table-column>
              <el-table-column prop="distribute_time" label="分发时间"></el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'">
                    {{ scope.row.status === 'completed' ? '已完成' : '进行中' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="viewDistributionDetail(scope.row)">查看详情</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="改进计划跟踪" name="tracking">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>改进计划管理</span>
                <el-button type="primary" @click="addImprovementPlan">添加改进计划</el-button>
              </div>
            </template>
            
            <el-form :model="trackingForm" label-width="120px" style="margin-bottom: 20px;">
              <el-form-item label="教师ID">
                <el-input v-model="trackingForm.teacher_id" placeholder="输入教师ID"></el-input>
              </el-form-item>
              
              <el-form-item label="学年学期">
                <el-input v-model="trackingForm.academic_year" placeholder="例如：2024-2025-1"></el-input>
              </el-form-item>
              
              <el-form-item label="状态">
                <el-select v-model="trackingForm.status" placeholder="选择状态">
                  <el-option label="全部" value=""></el-option>
                  <el-option label="未开始" value="not_started"></el-option>
                  <el-option label="进行中" value="in_progress"></el-option>
                  <el-option label="已完成" value="completed"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="searchImprovementPlans">查询</el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
            
            <el-table :data="improvementPlans" style="width: 100%">
              <el-table-column prop="plan_id" label="计划ID"></el-table-column>
              <el-table-column prop="teacher_name" label="教师姓名"></el-table-column>
              <el-table-column prop="teacher_id" label="教师ID"></el-table-column>
              <el-table-column prop="academic_year" label="学年学期"></el-table-column>
              <el-table-column prop="plan_content" label="改进计划内容" width="300"></el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-tag :type="getTagType(scope.row.status)">
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_time" label="创建时间"></el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="viewPlanDetail(scope.row)">查看详情</el-button>
                  <el-button type="success" size="small" v-if="scope.row.status === 'in_progress'" @click="approvePlan(scope.row)">审核通过</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="培训需求分析" name="training">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>培训需求分析</span>
                <el-button type="primary" @click="analyzeTrainingNeeds">分析需求</el-button>
              </div>
            </template>
            
            <el-form :model="trainingForm" label-width="120px" class="training-form">
              <el-form-item label="院系">
                <el-select v-model="trainingForm.department_id" placeholder="选择院系">
                  <el-option label="全部院系" value=""></el-option>
                  <el-option label="计算机学院" value="cs"></el-option>
                  <el-option label="电子工程学院" value="ee"></el-option>
                  <el-option label="人文学院" value="h"></el-option>
                  <el-option label="经管学院" value="jm"></el-option>
                  <el-option label="外语学院" value="fl"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="数据周期">
                <el-input v-model="trainingForm.data_period" placeholder="例如：2024-2025-1"></el-input>
              </el-form-item>
              
              <el-form-item label="问题类型" v-if="trainingForm.department_id">
                <el-select v-model="trainingForm.problem_types" multiple placeholder="选择问题类型">
                  <el-option label="教学态度" value="attitude"></el-option>
                  <el-option label="教学内容" value="content"></el-option>
                  <el-option label="教学方法" value="method"></el-option>
                  <el-option label="教学效果" value="effect"></el-option>
                </el-select>
              </el-form-item>
            </el-form>
            
            <div class="training-results">
              <h3>培训需求分析结果</h3>
              <el-card>
                <template #header>
                  <span>共性问题分析</span>
                </template>
                <el-table :data="commonProblems" style="width: 100%">
                  <el-table-column prop="problem_type" label="问题类型"></el-table-column>
                  <el-table-column prop="count" label="出现次数"></el-table-column>
                  <el-table-column prop="percentage" label="占比"></el-table-column>
                  <el-table-column prop="description" label="问题描述"></el-table-column>
                </el-table>
              </el-card>
              
              <el-card style="margin-top: 20px;">
                <template #header>
                  <span>推荐培训课程</span>
                </template>
                <el-table :data="recommendedCourses" style="width: 100%">
                  <el-table-column prop="course_id" label="课程ID"></el-table-column>
                  <el-table-column prop="course_name" label="课程名称"></el-table-column>
                  <el-table-column prop="target_group" label="目标群体"></el-table-column>
                  <el-table-column prop="duration" label="培训时长"></el-table-column>
                  <el-table-column prop="relevance" label="相关度">
                    <template #default="scope">
                      <el-progress :percentage="scope.row.relevance" :stroke-width="10"></el-progress>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作">
                    <template #default="scope">
                      <el-button type="primary" size="small" @click="viewCourseDetail(scope.row)">查看详情</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    </div>
    
    <!-- 分发详情对话框 -->
    <el-dialog v-model="distributionDetailVisible" title="分发详情" width="70%">
      <div class="distribution-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="分发ID">{{ distributionDetailData.distribution_id }}</el-descriptions-item>
          <el-descriptions-item label="分发时间">{{ distributionDetailData.distribute_time }}</el-descriptions-item>
          <el-descriptions-item label="分发报告" :span="2">{{ distributionDetailData.report_names }}</el-descriptions-item>
          <el-descriptions-item label="目标角色">{{ distributionDetailData.target_roles }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="distributionDetailData.status === 'completed' ? 'success' : 'warning'">
              {{ distributionDetailData.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="通知方式" :span="2">{{ distributionDetailData.notify_type || '邮件,站内信' }}</el-descriptions-item>
          <el-descriptions-item label="分发说明" :span="2">{{ distributionDetailData.description || '无' }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="recipient-list" v-if="distributionDetailData.recipients">
          <h3>接收人列表</h3>
          <el-table :data="distributionDetailData.recipients" style="width: 100%">
            <el-table-column prop="name" label="姓名"></el-table-column>
            <el-table-column prop="role" label="角色"></el-table-column>
            <el-table-column prop="email" label="邮箱"></el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'delivered' ? 'success' : 'warning'">
                  {{ scope.row.status === 'delivered' ? '已送达' : '待送达' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="distributionDetailVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';

const activeTab = ref('distribute');

// 分发结果表单
const distributeForm = ref({
  report_ids: [],
  target_roles: [],
  notify_type: ['邮件', '站内信'],
  description: ''
});

// 可用报告列表
const availableReports = ref([
  { report_id: 1, report_name: '2024-2025-1校级综合报告' },
  { report_id: 2, report_name: '2024-2025-1计算机学院诊断报告' },
  { report_id: 3, report_name: '2024-2025-1电子工程学院诊断报告' },
  { report_id: 4, report_name: '2024-2025-1教师个人报告（ID:1001）' }
]);

// 分发记录
const distributionRecords = ref([
  {
    distribution_id: 1,
    report_names: '2024-2025-1校级综合报告',
    target_roles: '校级管理员,院系管理员',
    distribute_time: '2024-12-19 10:00:00',
    status: 'completed',
    notify_type: '邮件,站内信',
    description: '2024-2025学年第一学期校级综合评价报告',
    recipients: [
      { name: '校长', role: '校级管理员', email: 'principal@example.com', status: 'delivered' },
      { name: '教务处长', role: '校级管理员', email: 'dean@example.com', status: 'delivered' },
      { name: '计算机学院院长', role: '院系管理员', email: 'cs_dean@example.com', status: 'delivered' },
      { name: '电子工程学院院长', role: '院系管理员', email: 'ee_dean@example.com', status: 'delivered' }
    ]
  },
  {
    distribution_id: 2,
    report_names: '2024-2025-1计算机学院诊断报告',
    target_roles: '计算机学院管理员,计算机学院教师',
    distribute_time: '2024-12-18 15:30:00',
    status: 'completed',
    notify_type: '邮件,站内信',
    description: '2024-2025学年第一学期计算机学院评价诊断报告',
    recipients: [
      { name: '计算机学院院长', role: '院系管理员', email: 'cs_dean@example.com', status: 'delivered' },
      { name: '计算机学院教学秘书', role: '院系管理员', email: 'cs_secretary@example.com', status: 'delivered' },
      { name: '张三', role: '教师', email: 'zhangsan@example.com', status: 'delivered' },
      { name: '李四', role: '教师', email: 'lisi@example.com', status: 'delivered' }
    ]
  },
  {
    distribution_id: 3,
    report_names: '2024-2025-1教师个人报告（ID:1001）',
    target_roles: '教师（ID:1001）',
    distribute_time: '2024-12-17 09:15:00',
    status: 'in_progress',
    notify_type: '邮件,站内信',
    description: '2024-2025学年第一学期教师个人评价报告',
    recipients: [
      { name: '张三', role: '教师', email: 'zhangsan@example.com', status: 'delivered' }
    ]
  }
]);

// 分发详情对话框
const distributionDetailVisible = ref(false);
const distributionDetailData = ref({
  distribution_id: '',
  report_names: '',
  target_roles: '',
  distribute_time: '',
  status: '',
  notify_type: '',
  description: '',
  recipients: []
});

// 改进计划跟踪表单
const trackingForm = ref({
  teacher_id: '',
  academic_year: '2024-2025-1',
  status: ''
});

// 改进计划列表
const improvementPlans = ref([
  {
    plan_id: 1,
    teacher_name: '张三',
    teacher_id: '1001',
    academic_year: '2024-2025-1',
    plan_content: '1. 改进教学方法，增加互动环节\n2. 优化课程内容，更新案例\n3. 加强与学生的沟通',
    status: 'completed',
    created_time: '2024-12-15 14:30:00'
  },
  {
    plan_id: 2,
    teacher_name: '李四',
    teacher_id: '1002',
    academic_year: '2024-2025-1',
    plan_content: '1. 改进课件质量\n2. 增加课后辅导时间\n3. 改进考试评价方式',
    status: 'in_progress',
    created_time: '2024-12-16 10:20:00'
  },
  {
    plan_id: 3,
    teacher_name: '王五',
    teacher_id: '1003',
    academic_year: '2024-2025-1',
    plan_content: '1. 改进教学态度\n2. 增加实践环节\n3. 优化作业设计',
    status: 'not_started',
    created_time: '2024-12-17 09:00:00'
  }
]);

// 培训需求分析表单
const trainingForm = ref({
  department_id: '',
  data_period: '2024-2025-1',
  problem_types: []
});

// 共性问题
const commonProblems = ref([
  {
    problem_type: '教学方法',
    count: 15,
    percentage: '35%',
    description: '缺乏互动式教学，课堂氛围沉闷'
  },
  {
    problem_type: '教学内容',
    count: 12,
    percentage: '28%',
    description: '课程内容更新不及时，案例陈旧'
  },
  {
    problem_type: '教学态度',
    count: 8,
    percentage: '19%',
    description: '部分教师上课迟到，备课不充分'
  },
  {
    problem_type: '教学效果',
    count: 7,
    percentage: '16%',
    description: '学生学习效果不佳，考试通过率低'
  }
]);

// 推荐培训课程
const recommendedCourses = ref([
  {
    course_id: 'T001',
    course_name: '互动式教学方法培训',
    target_group: '全体教师',
    duration: '16课时',
    relevance: 95
  },
  {
    course_id: 'T002',
    course_name: '课程内容设计与更新',
    target_group: '专业课教师',
    duration: '12课时',
    relevance: 88
  },
  {
    course_id: 'T003',
    course_name: '教师职业素养提升',
    target_group: '青年教师',
    duration: '8课时',
    relevance: 75
  },
  {
    course_id: 'T004',
    course_name: '现代教育技术应用',
    target_group: '全体教师',
    duration: '10课时',
    relevance: 82
  }
]);

const distributeResults = () => {
  // 实现分发结果逻辑
  if (distributeForm.value.report_ids.length === 0 || distributeForm.value.target_roles.length === 0) {
    ElMessage.error('请选择要分发的报告和目标角色');
    return;
  }
  
  // 模拟分发过程
  ElMessage.success('结果分发成功');
  
  // 添加到分发记录
  const reportNames = distributeForm.value.report_ids.map(id => {
    const report = availableReports.value.find(r => r.report_id === id);
    return report ? report.report_name : '';
  }).join(', ');
  
  // 生成模拟接收人列表
  const recipients = generateRecipients(distributeForm.value.target_roles);
  
  distributionRecords.value.unshift({
    distribution_id: distributionRecords.value.length + 1,
    report_names: reportNames,
    target_roles: distributeForm.value.target_roles.join(','),
    distribute_time: new Date().toLocaleString(),
    status: 'in_progress',
    notify_type: distributeForm.value.notify_type.join(','),
    description: distributeForm.value.description,
    recipients: recipients
  });
  
  // 重置表单
  distributeForm.value = {
    report_ids: [],
    target_roles: [],
    notify_type: ['邮件', '站内信'],
    description: ''
  };
};

const viewDistributionDetail = (row: any) => {
  // 实现查看分发详情逻辑
  distributionDetailData.value = { ...row };
  distributionDetailVisible.value = true;
};

// 生成模拟接收人列表
const generateRecipients = (roles: string[]) => {
  const recipientsMap: { [key: string]: { name: string, email: string }[] } = {
    admin: [
      { name: '校长', email: 'principal@example.com' },
      { name: '教务处长', email: 'dean@example.com' }
    ],
    dept_admin: [
      { name: '计算机学院院长', email: 'cs_dean@example.com' },
      { name: '电子工程学院院长', email: 'ee_dean@example.com' }
    ],
    supervisor: [
      { name: '教学督导A', email: 'supervisor1@example.com' },
      { name: '教学督导B', email: 'supervisor2@example.com' }
    ],
    teacher: [
      { name: '张三', email: 'zhangsan@example.com' },
      { name: '李四', email: 'lisi@example.com' }
    ]
  };
  
  const recipients: any[] = [];
  roles.forEach(role => {
    if (recipientsMap[role]) {
      recipientsMap[role].forEach(item => {
        recipients.push({
          name: item.name,
          role: getRoleName(role),
          email: item.email,
          status: 'delivered'
        });
      });
    }
  });
  
  return recipients;
};

// 获取角色名称
const getRoleName = (role: string) => {
  const roleMap: { [key: string]: string } = {
    admin: '校级管理员',
    dept_admin: '院系管理员',
    supervisor: '教学督导',
    teacher: '教师'
  };
  return roleMap[role] || role;
};

const searchImprovementPlans = () => {
  // 实现查询改进计划逻辑
  ElMessage.info('查询改进计划功能开发中');
};

const resetForm = () => {
  trackingForm.value = {
    teacher_id: '',
    academic_year: '2024-2025-1',
    status: ''
  };
};

const addImprovementPlan = () => {
  // 实现添加改进计划逻辑
  ElMessage.info('添加改进计划功能开发中');
};

const viewPlanDetail = (row: any) => {
  // 实现查看计划详情逻辑
  ElMessage.info('查看计划详情功能开发中');
};

const approvePlan = (row: any) => {
  // 实现审核计划逻辑
  row.status = 'completed';
  ElMessage.success('计划审核通过');
};

const getTagType = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'in_progress':
      return 'warning';
    case 'not_started':
      return 'info';
    default:
      return '';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return '已完成';
    case 'in_progress':
      return '进行中';
    case 'not_started':
      return '未开始';
    default:
      return '';
  }
};

const analyzeTrainingNeeds = () => {
  // 实现分析培训需求逻辑
  if (!trainingForm.value.data_period) {
    ElMessage.error('请输入数据周期');
    return;
  }
  
  // 模拟分析过程
  ElMessage.success('培训需求分析完成');
};

const viewCourseDetail = (row: any) => {
  // 实现查看课程详情逻辑
  ElMessage.info('查看课程详情功能开发中');
};
</script>

<style scoped>
.application-center {
  /* 样式已统一到 App.vue 的 page-container 类 */
}

/* 卡片头部样式继承自 App.vue */

.distribute-form,
.training-form {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.training-results {
  margin-top: 30px;
}

.empty-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}
</style>