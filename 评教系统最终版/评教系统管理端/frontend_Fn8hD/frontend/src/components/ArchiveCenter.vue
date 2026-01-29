<template>
  <div class="archive-center page-container">
    <div class="content-container">
      <div class="page-title">归档审计中心</div>
      <el-card>
      <template #header>
        <div class="card-header">
          <span>数据归档与审计</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="数据归档管理" name="archive">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>归档策略配置</span>
                <el-button type="primary" @click="saveArchivePolicy">保存策略</el-button>
              </div>
            </template>
            
            <el-form :model="archivePolicy" label-width="120px" class="policy-form">
              <el-form-item label="自动归档策略">
                <el-radio-group v-model="archivePolicy.auto_archive">
                  <el-radio label="true">启用</el-radio>
                  <el-radio label="false">禁用</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="归档时间" v-if="archivePolicy.auto_archive === 'true'">
                <el-select v-model="archivePolicy.archive_time" placeholder="选择归档时间">
                  <el-option label="学期结束后1周" value="1_week"></el-option>
                  <el-option label="学期结束后2周" value="2_weeks"></el-option>
                  <el-option label="学期结束后1个月" value="1_month"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="归档类型">
                <el-checkbox-group v-model="archivePolicy.archive_types">
                  <el-checkbox label="评教数据">评教数据</el-checkbox>
                  <el-checkbox label="分析报告">分析报告</el-checkbox>
                  <el-checkbox label="操作日志">操作日志</el-checkbox>
                  <el-checkbox label="配置文件">配置文件</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="归档保留期限">
                <el-select v-model="archivePolicy.retention_period" placeholder="选择保留期限">
                  <el-option label="1年" value="1_year"></el-option>
                  <el-option label="3年" value="3_years"></el-option>
                  <el-option label="5年" value="5_years"></el-option>
                  <el-option label="永久" value="permanent"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="归档存储位置">
                <el-input v-model="archivePolicy.storage_location" placeholder="输入存储路径"></el-input>
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>归档数据管理</span>
                <el-button type="primary" @click="manualArchive">手动归档</el-button>
              </div>
            </template>
            
            <el-form :model="archiveQuery" label-width="120px" style="margin-bottom: 20px;">
              <el-form-item label="归档时间范围">
                <el-date-picker v-model="archiveQuery.date_range" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"></el-date-picker>
              </el-form-item>
              
              <el-form-item label="归档类型">
                <el-select v-model="archiveQuery.archive_type" placeholder="选择归档类型">
                  <el-option label="全部" value=""></el-option>
                  <el-option label="评教数据" value="evaluation_data"></el-option>
                  <el-option label="分析报告" value="analysis_report"></el-option>
                  <el-option label="操作日志" value="operation_log"></el-option>
                  <el-option label="配置文件" value="config_file"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="queryArchiveData">查询</el-button>
                <el-button @click="resetArchiveQuery">重置</el-button>
              </el-form-item>
            </el-form>
            
            <el-table :data="archivedData" style="width: 100%">
              <el-table-column prop="archive_id" label="归档ID"></el-table-column>
              <el-table-column prop="archive_type" label="归档类型"></el-table-column>
              <el-table-column prop="archive_time" label="归档时间"></el-table-column>
              <el-table-column prop="data_period" label="数据周期"></el-table-column>
              <el-table-column prop="file_size" label="文件大小"></el-table-column>
              <el-table-column prop="storage_location" label="存储位置" width="300"></el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'valid' ? 'success' : 'danger'">
                    {{ scope.row.status === 'valid' ? '有效' : '损坏' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="viewArchive(scope.row)">查看</el-button>
                  <el-button type="info" size="small" @click="downloadArchive(scope.row)">下载</el-button>
                  <el-button type="danger" size="small" @click="deleteArchive(scope.row)">删除</el-button>
                  <el-button type="warning" size="small" @click="verifyArchive(scope.row)">校验</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="操作审计日志" name="audit">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>审计日志查询</span>
              </div>
            </template>
            
            <el-form :model="auditQuery" label-width="120px" style="margin-bottom: 20px;">
              <el-form-item label="操作时间范围">
                <el-date-picker v-model="auditQuery.date_range" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"></el-date-picker>
              </el-form-item>
              
              <el-form-item label="操作人">
                <el-input v-model="auditQuery.operator" placeholder="输入操作人"></el-input>
              </el-form-item>
              
              <el-form-item label="操作类型">
                <el-select v-model="auditQuery.operation_type" placeholder="选择操作类型">
                  <el-option label="全部" value=""></el-option>
                  <el-option label="登录" value="login"></el-option>
                  <el-option label="配置修改" value="config_modify"></el-option>
                  <el-option label="数据查询" value="data_query"></el-option>
                  <el-option label="报告生成" value="report_generate"></el-option>
                  <el-option label="结果分发" value="result_distribute"></el-option>
                  <el-option label="异常操作" value="abnormal"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="IP地址">
                <el-input v-model="auditQuery.ip_address" placeholder="输入IP地址"></el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="queryAuditLogs">查询</el-button>
                <el-button @click="resetAuditQuery">重置</el-button>
                <el-button type="info" @click="exportAuditLogs">导出日志</el-button>
              </el-form-item>
            </el-form>
            
            <el-table :data="auditLogs" style="width: 100%">
              <el-table-column prop="log_id" label="日志ID"></el-table-column>
              <el-table-column prop="operator" label="操作人"></el-table-column>
              <el-table-column prop="operation_type" label="操作类型"></el-table-column>
              <el-table-column prop="operation_content" label="操作内容" width="300"></el-table-column>
              <el-table-column prop="ip_address" label="IP地址"></el-table-column>
              <el-table-column prop="operation_time" label="操作时间"></el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                    {{ scope.row.status === 'success' ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="viewLogDetail(scope.row)">查看详情</el-button>
                  <el-button type="danger" size="small" v-if="scope.row.operation_type === 'abnormal'" @click="handleAbnormal(scope.row)">处理异常</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalLogs"
              style="margin-top: 20px;"
            ></el-pagination>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="隐私保护管理" name="privacy">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>隐私保护配置</span>
                <el-button type="primary" @click="savePrivacyConfig">保存配置</el-button>
              </div>
            </template>
            
            <el-form :model="privacyConfig" label-width="120px" class="privacy-form">
              <el-form-item label="数据脱敏规则">
                <el-checkbox-group v-model="privacyConfig.desensitization_rules">
                  <el-checkbox label="student_id">学生ID</el-checkbox>
                  <el-checkbox label="teacher_id">教师ID</el-checkbox>
                  <el-checkbox label="phone">手机号码</el-checkbox>
                  <el-checkbox label="email">邮箱地址</el-checkbox>
                  <el-checkbox label="ip_address">IP地址</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="脱敏方式" v-if="privacyConfig.desensitization_rules.length > 0">
                <el-select v-model="privacyConfig.desensitization_method" placeholder="选择脱敏方式">
                  <el-option label="部分替换为*" value="partial"></el-option>
                  <el-option label="哈希处理" value="hash"></el-option>
                  <el-option label="随机替换" value="random"></el-option>
                </el-select>
              </el-form-item>
              
              <el-form-item label="访问权限控制">
                <el-radio-group v-model="privacyConfig.access_control">
                  <el-radio label="strict">严格模式（仅授权人员可访问）</el-radio>
                  <el-radio label="normal">普通模式（院系级以上可访问）</el-radio>
                  <el-radio label="relaxed">宽松模式（所有管理员可访问）</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="定期权限审查">
                <el-radio-group v-model="privacyConfig.permission_review">
                  <el-radio label="true">启用</el-radio>
                  <el-radio label="false">禁用</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="审查周期" v-if="privacyConfig.permission_review === 'true'">
                <el-select v-model="privacyConfig.review_period" placeholder="选择审查周期">
                  <el-option label="每月" value="monthly"></el-option>
                  <el-option label="每季度" value="quarterly"></el-option>
                  <el-option label="每半年" value="half_yearly"></el-option>
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>合规性自查报告</span>
                <el-button type="primary" @click="generateComplianceReport">生成报告</el-button>
              </div>
            </template>
            
            <el-table :data="complianceReports" style="width: 100%">
              <el-table-column prop="report_id" label="报告ID"></el-table-column>
              <el-table-column prop="report_time" label="生成时间"></el-table-column>
              <el-table-column prop="compliance_score" label="合规得分">
                <template #default="scope">
                  <el-progress :percentage="scope.row.compliance_score" :stroke-width="10"></el-progress>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'compliant' ? 'success' : 'warning'">
                    {{ scope.row.status === 'compliant' ? '合规' : '部分不合规' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="issues" label="存在问题" width="300"></el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="viewComplianceReport(scope.row)">查看报告</el-button>
                  <el-button type="info" size="small" @click="downloadComplianceReport(scope.row)">下载</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';

const activeTab = ref('archive');

// 归档策略配置
const archivePolicy = ref({
  auto_archive: 'true',
  archive_time: '1_month',
  archive_types: ['评教数据', '分析报告', '操作日志'],
  retention_period: '5_years',
  storage_location: '/archives'
});

// 归档查询表单
const archiveQuery = ref({
  date_range: [],
  archive_type: '',
  data_period: ''
});

// 归档数据列表
const archivedData = ref([
  {
    archive_id: 1,
    archive_type: '评教数据',
    archive_time: '2024-12-01 10:00:00',
    data_period: '2024-2025-1',
    file_size: '128MB',
    storage_location: '/archives/2024-2025-1_evaluation_data.zip',
    status: 'valid'
  },
  {
    archive_id: 2,
    archive_type: '分析报告',
    archive_time: '2024-12-01 10:30:00',
    data_period: '2024-2025-1',
    file_size: '64MB',
    storage_location: '/archives/2024-2025-1_analysis_reports.zip',
    status: 'valid'
  },
  {
    archive_id: 3,
    archive_type: '操作日志',
    archive_time: '2024-12-01 11:00:00',
    data_period: '2024-2025-1',
    file_size: '256MB',
    storage_location: '/archives/2024-2025-1_operation_logs.zip',
    status: 'valid'
  },
  {
    archive_id: 4,
    archive_type: '评教数据',
    archive_time: '2024-07-01 09:00:00',
    data_period: '2023-2024-2',
    file_size: '112MB',
    storage_location: '/archives/2023-2024-2_evaluation_data.zip',
    status: 'valid'
  }
]);

// 审计日志查询表单
const auditQuery = ref({
  date_range: [],
  operator: '',
  operation_type: '',
  ip_address: ''
});

// 审计日志列表
const auditLogs = ref([
  {
    log_id: 1,
    operator: 'admin',
    operation_type: 'login',
    operation_content: '登录系统',
    ip_address: '192.168.1.100',
    operation_time: '2024-12-19 10:00:00',
    status: 'success'
  },
  {
    log_id: 2,
    operator: 'admin',
    operation_type: 'config_modify',
    operation_content: '修改评教方案配置',
    ip_address: '192.168.1.100',
    operation_time: '2024-12-19 10:30:00',
    status: 'success'
  },
  {
    log_id: 3,
    operator: 'dept_admin_cs',
    operation_type: 'data_query',
    operation_content: '查询计算机学院评教数据',
    ip_address: '192.168.1.101',
    operation_time: '2024-12-19 11:00:00',
    status: 'success'
  },
  {
    log_id: 4,
    operator: 'user123',
    operation_type: 'login',
    operation_content: '登录系统',
    ip_address: '192.168.1.200',
    operation_time: '2024-12-19 11:30:00',
    status: 'failure'
  },
  {
    log_id: 5,
    operator: 'admin',
    operation_type: 'report_generate',
    operation_content: '生成校级综合报告',
    ip_address: '192.168.1.100',
    operation_time: '2024-12-19 12:00:00',
    status: 'success'
  },
  {
    log_id: 6,
    operator: 'unknown',
    operation_type: 'abnormal',
    operation_content: '尝试访问未授权资源',
    ip_address: '192.168.1.300',
    operation_time: '2024-12-19 12:30:00',
    status: 'failure'
  }
]);

// 分页参数
const currentPage = ref(1);
const pageSize = ref(10);
const totalLogs = ref(100);

// 隐私保护配置
const privacyConfig = ref({
  desensitization_rules: ['student_id', 'phone', 'email'],
  desensitization_method: 'partial',
  access_control: 'normal',
  permission_review: 'true',
  review_period: 'quarterly'
});

// 合规性自查报告
const complianceReports = ref([
  {
    report_id: 1,
    report_time: '2024-12-01 10:00:00',
    compliance_score: 95,
    status: 'compliant',
    issues: '无重大问题，仅需优化部分权限设置'
  },
  {
    report_id: 2,
    report_time: '2024-09-01 10:00:00',
    compliance_score: 88,
    status: 'compliant',
    issues: '部分脱敏规则未生效，已修复'
  },
  {
    report_id: 3,
    report_time: '2024-06-01 10:00:00',
    compliance_score: 75,
    status: 'non_compliant',
    issues: '访问权限控制不严格，存在未授权访问风险'
  }
]);

const saveArchivePolicy = () => {
  // 实现保存归档策略逻辑
  ElMessage.success('归档策略保存成功');
};

const manualArchive = () => {
  // 实现手动归档逻辑
  ElMessage.success('手动归档任务已启动');
};

const queryArchiveData = () => {
  // 实现查询归档数据逻辑
  ElMessage.info('查询归档数据功能开发中');
};

const resetArchiveQuery = () => {
  archiveQuery.value = {
    date_range: [],
    archive_type: '',
    data_period: ''
  };
};

const viewArchive = (row: any) => {
  // 实现查看归档逻辑
  ElMessage.info('查看归档功能开发中');
};

const downloadArchive = (row: any) => {
  // 实现下载归档逻辑
  ElMessage.info('下载归档功能开发中');
};

const deleteArchive = (row: any) => {
  // 实现删除归档逻辑
  ElMessage.success('归档删除成功');
};

const verifyArchive = (row: any) => {
  // 实现校验归档逻辑
  ElMessage.success('归档校验通过，数据完整');
};

const queryAuditLogs = () => {
  // 实现查询审计日志逻辑
  ElMessage.info('查询审计日志功能开发中');
};

const resetAuditQuery = () => {
  auditQuery.value = {
    date_range: [],
    operator: '',
    operation_type: '',
    ip_address: ''
  };
};

const exportAuditLogs = () => {
  // 实现导出审计日志逻辑
  ElMessage.success('审计日志导出成功');
};

const viewLogDetail = (row: any) => {
  // 实现查看日志详情逻辑
  ElMessage.info('查看日志详情功能开发中');
};

const handleAbnormal = (row: any) => {
  // 实现处理异常操作逻辑
  ElMessage.success('异常操作已处理');
};

const savePrivacyConfig = () => {
  // 实现保存隐私保护配置逻辑
  ElMessage.success('隐私保护配置保存成功');
};

const generateComplianceReport = () => {
  // 实现生成合规性自查报告逻辑
  ElMessage.success('合规性自查报告生成成功');
  
  // 添加到报告列表
  complianceReports.value.unshift({
    report_id: complianceReports.value.length + 1,
    report_time: new Date().toLocaleString(),
    compliance_score: 92,
    status: 'compliant',
    issues: '无重大问题，系统运行正常'
  });
};

const viewComplianceReport = (row: any) => {
  // 实现查看合规性报告逻辑
  ElMessage.info('查看合规性报告功能开发中');
};

const downloadComplianceReport = (row: any) => {
  // 实现下载合规性报告逻辑
  ElMessage.success('合规性报告下载成功');
};
</script>

<style scoped>
.archive-center {
  /* 样式已统一到 App.vue 的 page-container 类 */
}

/* 卡片头部样式继承自 App.vue */

.policy-form,
.privacy-form {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.empty-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}
</style>