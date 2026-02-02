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
        <el-tab-pane label="评分结果归档" name="scores">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>评分结果归档管理</span>
                <el-button type="primary" @click="archiveScores" :loading="archiving">
                  <el-icon><folder-add /></el-icon>
                  归档已评分任务
                </el-button>
              </div>
            </template>
            
            <!-- 筛选条件 -->
            <el-form :model="scoreFilters" label-width="100px" style="margin-bottom: 20px;">
              <el-row :gutter="20">
                <el-col :span="6">
                  <el-form-item label="学期">
                    <el-select v-model="scoreFilters.semester" placeholder="选择学期" clearable>
                      <el-option label="2025-2026-1" value="2025-2026-1" />
                      <el-option label="2024-2025-2" value="2024-2025-2" />
                      <el-option label="2024-2025-1" value="2024-2025-1" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="考评表">
                    <el-input v-model="scoreFilters.template_name" placeholder="考评表名称" clearable />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="教师">
                    <el-input v-model="scoreFilters.teacher_id" placeholder="教师ID" clearable />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-button type="primary" @click="loadArchivedScores">
                    <el-icon><search /></el-icon>
                    查询
                  </el-button>
                  <el-button @click="resetScoreFilters">重置</el-button>
                </el-col>
              </el-row>
            </el-form>
            
            <!-- 归档统计 -->
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="6">
                <el-statistic title="已归档任务" :value="scoreStats.total" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="归档教师数" :value="scoreStats.teachers" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="平均得分" :value="scoreStats.avgScore" :precision="1" suffix="分" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="归档数据量" :value="scoreStats.dataSize" suffix="MB" />
              </el-col>
            </el-row>
            
            <!-- 归档列表 -->
            <el-table :data="archivedScores" stripe style="width: 100%" :loading="loading">
              <el-table-column type="index" width="50" label="#" />
              <el-table-column prop="archive_id" label="归档ID" width="180" />
              <el-table-column prop="teacher_id" label="教师ID" width="120" />
              <el-table-column prop="teacher_name" label="教师姓名" width="120" />
              <el-table-column prop="template_name" label="考评表" min-width="150" />
              <el-table-column prop="score" label="得分" width="100">
                <template #default="{ row }">
                  <el-tag :type="getScoreTagType(row.score, row.total_score)">
                    {{ row.score }} / {{ row.total_score }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="percentage" label="得分率" width="100">
                <template #default="{ row }">
                  <el-progress 
                    :percentage="Math.round((row.score / row.total_score) * 100)" 
                    :stroke-width="8"
                    :color="getProgressColor(Math.round((row.score / row.total_score) * 100))"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="semester" label="学期" width="120" />
              <el-table-column prop="archived_at" label="归档时间" width="180" />
              <el-table-column label="操作" width="250" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="viewScoreDetail(row)">
                    <el-icon><view /></el-icon>
                    查看详情
                  </el-button>
                  <el-button link type="success" size="small" @click="exportScore(row)">
                    <el-icon><download /></el-icon>
                    导出
                  </el-button>
                  <el-button link type="danger" size="small" @click="deleteArchivedScore(row)">
                    <el-icon><delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 分页 -->
            <el-pagination
              v-model:current-page="scorePagination.page"
              v-model:page-size="scorePagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="scorePagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              style="margin-top: 20px;"
              @size-change="loadArchivedScores"
              @current-change="loadArchivedScores"
            />
          </el-card>
        </el-tab-pane>
        
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
                  <el-radio value="true">启用</el-radio>
                  <el-radio value="false">禁用</el-radio>
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
                  <el-checkbox :label="'评教数据'">评教数据</el-checkbox>
                  <el-checkbox :label="'分析报告'">分析报告</el-checkbox>
                  <el-checkbox :label="'操作日志'">操作日志</el-checkbox>
                  <el-checkbox :label="'配置文件'">配置文件</el-checkbox>
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
                  <el-checkbox :label="'student_id'">学生ID</el-checkbox>
                  <el-checkbox :label="'teacher_id'">教师ID</el-checkbox>
                  <el-checkbox :label="'phone'">手机号码</el-checkbox>
                  <el-checkbox :label="'email'">邮箱地址</el-checkbox>
                  <el-checkbox :label="'ip_address'">IP地址</el-checkbox>
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
                  <el-radio value="strict">严格模式（仅授权人员可访问）</el-radio>
                  <el-radio value="normal">普通模式（院系级以上可访问）</el-radio>
                  <el-radio value="relaxed">宽松模式（所有管理员可访问）</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="定期权限审查">
                <el-radio-group v-model="privacyConfig.permission_review">
                  <el-radio value="true">启用</el-radio>
                  <el-radio value="false">禁用</el-radio>
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
    
    <!-- 评分详情对话框 -->
    <el-dialog v-model="scoreDetailVisible" title="评分详情" width="800px">
      <div v-if="currentScore" class="score-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="归档ID">{{ currentScore.archive_id }}</el-descriptions-item>
          <el-descriptions-item label="任务ID">{{ currentScore.task_id }}</el-descriptions-item>
          <el-descriptions-item label="教师ID">{{ currentScore.teacher_id }}</el-descriptions-item>
          <el-descriptions-item label="教师姓名">{{ currentScore.teacher_name }}</el-descriptions-item>
          <el-descriptions-item label="考评表">{{ currentScore.template_name }}</el-descriptions-item>
          <el-descriptions-item label="学期">{{ currentScore.semester }}</el-descriptions-item>
          <el-descriptions-item label="总分">
            <el-tag type="success" size="large">{{ currentScore.score }} / {{ currentScore.total_score }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="得分率">
            <el-tag :type="getScoreTagType(currentScore.score, currentScore.total_score)" size="large">
              {{ Math.round((currentScore.score / currentScore.total_score) * 100) }}%
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="评分时间">{{ currentScore.scored_at }}</el-descriptions-item>
          <el-descriptions-item label="归档时间">{{ currentScore.archived_at }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentScore.scores" class="score-items" style="margin-top: 20px;">
          <h4>各项得分</h4>
          <el-table :data="formatScoreItems(currentScore.scores)" stripe>
            <el-table-column prop="name" label="评分项" />
            <el-table-column prop="score" label="得分" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.score }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="max_score" label="满分" width="100">
              <template #default="{ row }">
                {{ row.max_score }}
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="得分率" width="150">
              <template #default="{ row }">
                <el-progress 
                  :percentage="Math.round((row.score / row.max_score) * 100)" 
                  :stroke-width="8"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div v-if="currentScore.feedback" class="feedback-section" style="margin-top: 20px;">
          <h4>评分反馈</h4>
          <el-card>
            <p>{{ currentScore.feedback }}</p>
          </el-card>
        </div>
      </div>
    </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { FolderAdd, Search, View, Download, Delete } from '@element-plus/icons-vue';
import axios from 'axios';
import { waitForAuth } from '../utils/authState';

const activeTab = ref('scores'); // 默认显示评分归档

// 评分归档相关
const scoreFilters = ref({
  semester: '',
  template_name: '',
  teacher_id: ''
});

const archivedScores = ref([]);
const loading = ref(false);
const archiving = ref(false);
const scoreDetailVisible = ref(false);
const currentScore = ref<any>(null);

const scorePagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
});

const scoreStats = ref({
  total: 0,
  teachers: 0,
  avgScore: 0,
  dataSize: 0
});

// 加载已归档的评分
const loadArchivedScores = async () => {
  loading.value = true;
  try {
    const response = await axios.get('http://localhost:8001/api/archived-scores', {
      params: {
        ...scoreFilters.value,
        page: scorePagination.value.page,
        page_size: scorePagination.value.pageSize
      },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    });
    
    archivedScores.value = response.data.scores || [];
    scorePagination.value.total = response.data.total || 0;
    scoreStats.value = response.data.stats || scoreStats.value;
    
  } catch (error: any) {
    console.error('加载归档评分失败:', error);
    ElMessage.error(`加载失败: ${error.response?.data?.detail || error.message}`);
  } finally {
    loading.value = false;
  }
};

// 归档已评分任务
const archiveScores = async () => {
  try {
    const result = await ElMessageBox.confirm(
      '确定要归档所有已评分的任务吗？归档后数据将被永久保存。',
      '确认归档',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    if (result) {
      archiving.value = true;
      const response = await axios.post(
        'http://localhost:8001/api/archive-scores',
        {},
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
          }
        }
      );
      
      ElMessage.success(`成功归档 ${response.data.archived_count} 条评分记录`);
      loadArchivedScores();
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('归档失败:', error);
      ElMessage.error(`归档失败: ${error.response?.data?.detail || error.message}`);
    }
  } finally {
    archiving.value = false;
  }
};

// 重置筛选条件
const resetScoreFilters = () => {
  scoreFilters.value = {
    semester: '',
    template_name: '',
    teacher_id: ''
  };
  scorePagination.value.page = 1;
  loadArchivedScores();
};

// 查看评分详情
const viewScoreDetail = async (row: any) => {
  try {
    const response = await axios.get(`http://localhost:8001/api/archived-scores/${row.archive_id}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    });
    
    currentScore.value = response.data;
    scoreDetailVisible.value = true;
  } catch (error: any) {
    console.error('加载详情失败:', error);
    ElMessage.error(`加载详情失败: ${error.response?.data?.detail || error.message}`);
  }
};

// 导出评分
const exportScore = (row: any) => {
  ElMessage.info('导出功能开发中...');
  // TODO: 实现导出功能
};

// 删除归档评分
const deleteArchivedScore = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除归档ID为 ${row.archive_id} 的记录吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    await axios.delete(`http://localhost:8001/api/archived-scores/${row.archive_id}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    });
    
    ElMessage.success('删除成功');
    loadArchivedScores();
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error(`删除失败: ${error.response?.data?.detail || error.message}`);
    }
  }
};

// 获取得分标签类型
const getScoreTagType = (score: number, totalScore: number) => {
  const percentage = (score / totalScore) * 100;
  if (percentage >= 90) return 'success';
  if (percentage >= 80) return 'primary';
  if (percentage >= 70) return 'warning';
  if (percentage >= 60) return 'info';
  return 'danger';
};

// 获取进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a';
  if (percentage >= 80) return '#409eff';
  if (percentage >= 70) return '#e6a23c';
  if (percentage >= 60) return '#909399';
  return '#f56c6c';
};

// 格式化评分项
const formatScoreItems = (scores: any) => {
  if (!scores || typeof scores !== 'object') return [];
  
  return Object.entries(scores).map(([name, score]: [string, any]) => ({
    name,
    score: score,
    max_score: 10, // 假设满分为10，实际应从评分标准获取
    percentage: (score / 10) * 100
  }));
};

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

// 组件挂载时加载数据
onMounted(async () => {
  await waitForAuth();
  if (activeTab.value === 'scores') {
    loadArchivedScores();
  }
});
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

.score-detail {
  padding: 10px 0;
}

.score-detail h4 {
  margin: 20px 0 10px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.score-items {
  margin-top: 20px;
}

.feedback-section {
  margin-top: 20px;
}

.feedback-section p {
  margin: 0;
  line-height: 1.6;
  color: #606266;
}
</style>