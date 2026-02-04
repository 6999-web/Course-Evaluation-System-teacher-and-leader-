<template>
  <div class="evaluation-task-list">
    <h2 class="page-title">考评任务管理</h2>
    
    <el-card class="task-card">
      <!-- 筛选条件 -->
      <div class="filters-section">
        <el-form :model="filters" label-width="100px" class="filters-form">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="5">
              <el-form-item label="任务状态">
                <el-select v-model="filters.status" placeholder="所有状态" clearable>
                  <el-option label="未查收" value="pending" />
                  <el-option label="已查收" value="viewed" />
                  <el-option label="已提交" value="submitted" />
                  <el-option label="已评分" value="scored" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="5">
              <el-form-item label="教师ID">
                <el-input v-model="filters.teacher_id" placeholder="输入教师ID" clearable />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="5">
              <el-form-item label="考评表">
                <el-input v-model="filters.template_id" placeholder="输入考评表ID" clearable />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="4">
              <el-form-item label="显示模式">
                <el-select v-model="viewMode" placeholder="选择模式" @change="handleViewModeChange">
                  <el-option label="按教师" value="teacher" />
                  <el-option label="按模板" value="template" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="5">
              <el-button type="primary" @click="loadTasks" :loading="loading">
                <el-icon><search /></el-icon>
                查询
              </el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-col>
          </el-row>
        </el-form>
      </div>
      
      <!-- 任务列表 - 按教师显示 -->
      <el-table 
        v-if="viewMode === 'teacher'"
        :data="tasks" 
        stripe 
        style="width: 100%"
        :loading="loading"
        class="task-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="task_id" label="任务ID" width="150" />
        <el-table-column prop="template_name" label="考评表名称" min-width="150" />
        <el-table-column prop="teacher_id" label="教师ID" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.display_status || row.status)">
              {{ getStatusText(row.display_status || row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ row.submitted_at || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止时间" width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                v-if="row.status === 'submitted'" 
                link 
                type="primary" 
                size="small"
                @click="autoScore(row)"
                :loading="row.autoScoring || false"
              >
                <el-icon><star /></el-icon>
                AI自动评分
              </el-button>
              <el-button 
                v-if="row.status === 'submitted'" 
                link 
                type="info" 
                size="small"
                @click="openScoreDialog(row)"
              >
                <el-icon><edit /></el-icon>
                手动评分
              </el-button>
              <el-button 
                v-if="row.status === 'scored'" 
                link 
                type="success" 
                size="small"
                @click="viewScore(row)"
              >
                <el-icon><view /></el-icon>
                查看评分
              </el-button>
              <el-button 
                link 
                type="info" 
                size="small"
                @click="viewDetail(row)"
              >
                <el-icon><document /></el-icon>
                详情
              </el-button>
              <el-button 
                v-if="row.submitted_files && row.submitted_files.length > 0"
                link 
                type="warning" 
                size="small"
                @click="viewFiles(row)"
              >
                <el-icon><folder /></el-icon>
                文件
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 任务列表 - 按模板分组显示 -->
      <el-table 
        v-else
        :data="groupedTasks" 
        stripe 
        style="width: 100%"
        :loading="loading"
        class="task-table"
      >
        <el-table-column prop="template_id" label="考评表ID" width="180" />
        <el-table-column prop="template_name" label="考评表名称" min-width="200" />
        <el-table-column prop="teacher_count" label="分配教师数" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.teacher_count }} 人</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_summary" label="状态统计" min-width="250">
          <template #default="{ row }">
            <div class="status-summary">
              <el-tag v-if="row.status_counts.pending > 0" type="info" size="small">
                未查收: {{ row.status_counts.pending }}
              </el-tag>
              <el-tag v-if="row.status_counts.viewed > 0" type="warning" size="small">
                已查收: {{ row.status_counts.viewed }}
              </el-tag>
              <el-tag v-if="row.status_counts.submitted > 0" type="warning" size="small">
                已提交: {{ row.status_counts.submitted }}
              </el-tag>
              <el-tag v-if="row.status_counts.scored > 0" type="success" size="small">
                已评分: {{ row.status_counts.scored }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                link 
                type="primary" 
                size="small"
                @click="viewTemplateDetails(row)"
              >
                <el-icon><view /></el-icon>
                查看详情
              </el-button>
              <el-button 
                link 
                type="info" 
                size="small"
                @click="switchToTeacherView(row.template_id)"
              >
                <el-icon><user /></el-icon>
                按教师查看
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 批量操作按钮 -->
      <div class="batch-operations" v-if="viewMode === 'teacher'">
        <div v-if="selectedTasks.length > 0">
          <el-button type="primary" @click="batchAutoScore" :loading="batchScoreLoading">
            <el-icon><star /></el-icon>
            AI批量自动评分 ({{ selectedTasks.length }})
          </el-button>
          <el-button type="info" @click="batchScore" :loading="batchScoreLoading">
            <el-icon><edit /></el-icon>
            批量手动评分 ({{ selectedTasks.length }})
          </el-button>
          <el-button @click="clearSelection">清除选择</el-button>
        </div>
        <el-button type="success" @click="openExportDialog">
          <el-icon><download /></el-icon>
          导出评分结果
        </el-button>
      </div>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
      />
    </el-card>
    
    <!-- 评分对话框 -->
    <el-dialog v-model="scoreDialogVisible" title="考评任务评分" width="800px" @close="resetScoreData">
      <div v-if="currentTask" class="score-dialog">
        <div class="task-info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="考评表">{{ currentTask.template_name }}</el-descriptions-item>
            <el-descriptions-item label="教师">{{ currentTask.teacher_id }}</el-descriptions-item>
            <el-descriptions-item label="提交时间">{{ currentTask.submitted_at }}</el-descriptions-item>
            <el-descriptions-item label="截止时间">{{ currentTask.deadline }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="scoring-section">
          <h4>
            <el-icon><edit /></el-icon>
            评分标准
          </h4>
          <div v-if="currentTask.scoring_criteria && currentTask.scoring_criteria.length > 0" class="score-items">
            <div v-for="(criterion, index) in currentTask.scoring_criteria" :key="index" class="score-item">
              <div class="criterion-info">
                <label class="criterion-label">{{ criterion.name }}</label>
                <span class="criterion-desc" v-if="criterion.description">{{ criterion.description }}</span>
              </div>
              <div class="score-input-group">
                <el-input-number 
                  v-model.number="scoreData.scores[criterion.name]" 
                  :min="0"
                  :max="criterion.max_score"
                  :precision="1"
                  :step="0.5"
                  class="score-input"
                  @change="onScoreChange"
                />
                <span class="score-max">/ {{ criterion.max_score }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-criteria">
            <el-alert
              title="暂无评分标准"
              type="warning"
              :closable="false"
              show-icon
            />
          </div>
          
          <div class="total-score-display">
            <div class="score-summary">
              <span class="score-label">总分：</span>
              <strong class="score-value">{{ calculateTotalScore() }}</strong>
              <span class="score-max">/ {{ currentTask.total_score || 100 }}</span>
            </div>
            <div class="score-percentage">
              <el-tag :type="getScoreType(calculatePercentage())" size="large">
                {{ calculatePercentage() }}%
              </el-tag>
            </div>
          </div>
        </div>
        
        <div class="feedback-section">
          <h4>
            <el-icon><chat-line-round /></el-icon>
            评分反馈
          </h4>
          <el-input 
            v-model="scoreData.feedback" 
            type="textarea"
            placeholder="请输入评分反馈和建议（可选）"
            :rows="4"
            maxlength="500"
            show-word-limit
          />
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="scoreDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitScore" :loading="scoreLoading">
            <el-icon><check /></el-icon>
            提交评分
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="任务详情" width="700px">
      <div v-if="currentTask" class="detail-dialog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ currentTask.task_id }}</el-descriptions-item>
          <el-descriptions-item label="考评表">{{ currentTask.template_name }}</el-descriptions-item>
          <el-descriptions-item label="教师ID">{{ currentTask.teacher_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTask.display_status || currentTask.status)">
              {{ getStatusText(currentTask.display_status || currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总分">{{ currentTask.total_score }}</el-descriptions-item>
          <el-descriptions-item label="当前得分">
            {{ currentTask.score || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTask.created_at }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ currentTask.submitted_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ currentTask.deadline }}</el-descriptions-item>
          <el-descriptions-item label="评分时间">{{ currentTask.scored_at || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentTask.scoring_criteria" class="criteria-section">
          <h4>评分标准</h4>
          <el-table :data="currentTask.scoring_criteria" stripe>
            <el-table-column prop="name" label="评分项" />
            <el-table-column prop="max_score" label="最高分" width="100" />
          </el-table>
        </div>
        
        <div v-if="currentTask.feedback" class="feedback-display">
          <h4>评分反馈</h4>
          <p>{{ currentTask.feedback }}</p>
        </div>
      </div>
    </el-dialog>
    
    <!-- 文件列表对话框 -->
    <el-dialog v-model="filesDialogVisible" title="提交文件" width="600px">
      <div v-if="currentTask" class="files-dialog">
        <el-table :data="currentTask.submitted_files || []" stripe>
          <el-table-column prop="filename" label="文件名" />
          <el-table-column prop="file_size" label="大小" width="100">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column prop="uploaded_at" label="上传时间" width="180" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="downloadFile(row)">
                下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
    
    <!-- 评分详情对话框 -->
    <el-dialog v-model="scoreDetailDialogVisible" title="评分详情" width="800px">
      <div v-if="currentTask" class="score-detail-dialog">
        <div class="score-header">
          <div class="score-display">
            <div class="score-main">
              <span class="score-label">总分</span>
              <span class="score-value">{{ currentTask.score !== undefined && currentTask.score !== null ? currentTask.score : 0 }}</span>
              <span class="score-max">/ {{ currentTask.total_score || 100 }}</span>
            </div>
            <div class="score-percentage">
              <el-tag :type="getScoreType(currentTask.total_score && currentTask.score !== undefined && currentTask.score !== null ? Math.round(((currentTask.score || 0) / currentTask.total_score) * 100) : 0)" size="large">
                {{ currentTask.total_score && currentTask.score !== undefined && currentTask.score !== null ? Math.round(((currentTask.score || 0) / currentTask.total_score) * 100) : 0 }}%
              </el-tag>
            </div>
          </div>
        </div>
        
        <div v-if="currentTask.scoring_criteria && currentTask.scoring_criteria.length > 0" class="criteria-scores">
          <h4>
            <el-icon><document /></el-icon>
            各项评分详情
          </h4>
          <div class="criteria-grid">
            <!-- 如果有AI评分的详细结果，使用AI评分结果 -->
            <template v-if="currentTask.scores && currentTask.scores.score_details && currentTask.scores.score_details.length > 0">
              <div v-for="detail in currentTask.scores.score_details" :key="detail.indicator" class="criterion-card">
                <div class="criterion-header">
                  <span class="criterion-name">{{ detail.indicator }}</span>
                  <span class="criterion-score">
                    {{ detail.score }} / {{ detail.max_score }}
                  </span>
                </div>
                <div class="criterion-progress">
                  <el-progress 
                    :percentage="detail.max_score ? Math.round((detail.score / detail.max_score) * 100) : 0"
                    :color="getProgressColor(detail.max_score ? Math.round((detail.score / detail.max_score) * 100) : 0)"
                    :stroke-width="8"
                  />
                </div>
                <div v-if="detail.reason" class="criterion-reason">
                  <el-text type="info" size="small">{{ detail.reason }}</el-text>
                </div>
              </div>
            </template>
            <!-- 否则使用考评表标准显示 -->
            <template v-else>
              <div v-for="criterion in currentTask.scoring_criteria" :key="criterion.name" class="criterion-card">
                <div class="criterion-header">
                  <span class="criterion-name">{{ criterion.name }}</span>
                  <span class="criterion-score">
                    {{ (currentTask.scores && currentTask.scores[criterion.name] !== undefined) ? currentTask.scores[criterion.name] : 0 }} / {{ criterion.max_score }}
                  </span>
                </div>
                <div class="criterion-progress">
                  <el-progress 
                    :percentage="criterion.max_score ? Math.round((((currentTask.scores && currentTask.scores[criterion.name]) || 0) / criterion.max_score) * 100) : 0"
                    :color="getProgressColor(criterion.max_score ? Math.round((((currentTask.scores && currentTask.scores[criterion.name]) || 0) / criterion.max_score) * 100) : 0)"
                    :stroke-width="8"
                  />
                </div>
              </div>
            </template>
          </div>
        </div>
        
        <div v-if="currentTask.scoring_feedback" class="feedback-section">
          <h4>
            <el-icon><chat-line-round /></el-icon>
            评分反馈
          </h4>
          <div class="feedback-content structured-feedback">
            <div v-html="formatFeedback(currentTask.scoring_feedback)"></div>
          </div>
        </div>
        
        <div class="score-meta">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="评分时间">
              {{ currentTask.scored_at || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="评分状态">
              <el-tag type="success">已完成</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
    
    <!-- 批量评分对话框 -->
    <el-dialog v-model="batchScoreDialogVisible" title="批量手动评分" width="900px" @close="resetBatchScoreData">
      <div class="batch-score-dialog">
        <el-alert
          title="批量手动评分说明"
          type="info"
          description="将对选中的所有任务进行手动评分。您需要为每个任务手动输入分数。如需AI自动评分，请使用AI批量自动评分功能。"
          :closable="false"
          show-icon
          class="batch-alert"
        />
        
        <div class="batch-tasks-list">
          <h4>待评分任务列表 ({{ selectedTasks.length }} 项)</h4>
          <el-table :data="selectedTasks" stripe max-height="300">
            <el-table-column prop="task_id" label="任务ID" width="120" />
            <el-table-column prop="template_name" label="考评表" min-width="150" />
            <el-table-column prop="teacher_id" label="教师ID" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.display_status || row.status)">
                  {{ getStatusText(row.display_status || row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="batch-options">
          <el-form :model="batchScoreOptions" label-width="120px">
            <el-form-item label="评分方式">
              <el-radio-group v-model="batchScoreOptions.scoreType">
                <el-radio label="manual">手动评分</el-radio>
                <el-radio label="template" disabled>使用模板 (开发中)</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="默认分数">
              <el-input-number v-model="batchScoreOptions.defaultScore" :min="0" :max="100" />
              <span class="form-hint">为所有任务设置相同的默认分数</span>
            </el-form-item>
            <el-form-item label="是否覆盖">
              <el-switch v-model="batchScoreOptions.overwrite" />
              <span class="form-hint">如果已有评分，是否覆盖</span>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="batchScoreDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="executeBatchScore" :loading="batchScoreLoading">
            <el-icon><check /></el-icon>
            开始评分
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 导出评分结果对话框 -->
    <el-dialog v-model="exportDialogVisible" title="导出评分结果" width="900px" @close="resetExportData">
      <div class="export-dialog">
        <el-alert
          title="导出说明"
          type="info"
          description="将导出所有评分结果为 Excel 文件。可以通过筛选条件来选择要导出的数据。"
          :closable="false"
          show-icon
          class="export-alert"
        />
        
        <!-- 筛选条件 -->
        <div class="export-filters">
          <h4>筛选条件</h4>
          <el-form :model="exportFilters" label-width="100px">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="文件类型">
                  <el-select v-model="exportFilters.fileType" placeholder="所有类型" clearable>
                    <el-option label="教案" value="教案" />
                    <el-option label="教学反思" value="教学反思" />
                    <el-option label="教研/听课记录" value="教研/听课记录" />
                    <el-option label="成绩/学情分析" value="成绩/学情分析" />
                    <el-option label="课件" value="课件" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="等级">
                  <el-select v-model="exportFilters.grade" placeholder="所有等级" clearable>
                    <el-option label="优秀" value="优秀" />
                    <el-option label="良好" value="良好" />
                    <el-option label="合格" value="合格" />
                    <el-option label="不合格" value="不合格" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="开始日期">
                  <el-date-picker 
                    v-model="exportFilters.startDate" 
                    type="date"
                    placeholder="选择开始日期"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="结束日期">
                  <el-date-picker 
                    v-model="exportFilters.endDate" 
                    type="date"
                    placeholder="选择结束日期"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="6">
                <el-button type="primary" @click="loadExportData" :loading="exportLoading">
                  <el-icon><search /></el-icon>
                  查询
                </el-button>
                <el-button @click="resetExportFilters">重置</el-button>
              </el-col>
            </el-row>
          </el-form>
        </div>
        
        <!-- 数据预览 -->
        <div class="export-preview" v-if="exportData.length > 0">
          <h4>导出数据预览 ({{ exportData.length }} 条)</h4>
          <el-table :data="exportData" stripe max-height="300">
            <el-table-column prop="submission_id" label="提交ID" width="120" />
            <el-table-column prop="file_name" label="文件名" min-width="150" />
            <el-table-column prop="file_type" label="文件类型" width="100" />
            <el-table-column prop="final_score" label="最终得分" width="100" />
            <el-table-column prop="grade" label="等级" width="80">
              <template #default="{ row }">
                <el-tag :type="getGradeType(row.grade)">
                  {{ row.grade }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="scored_at" label="评分时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.scored_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 导出统计 -->
        <div v-if="exportData.length > 0" class="export-stats">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6">
              <div class="stat-item">
                <span class="stat-label">总数</span>
                <span class="stat-value">{{ exportData.length }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <div class="stat-item">
                <span class="stat-label">平均分</span>
                <span class="stat-value">{{ calculateAverageScore().toFixed(2) }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <div class="stat-item">
                <span class="stat-label">最高分</span>
                <span class="stat-value">{{ calculateMaxScore() }}</span>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <div class="stat-item">
                <span class="stat-label">最低分</span>
                <span class="stat-value">{{ calculateMinScore() }}</span>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="success" @click="executeExport" :loading="exporting" :disabled="exportData.length === 0">
            <el-icon><download /></el-icon>
            导出Excel
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Edit, View, Document, Folder, ChatLineRound, Check, User, Download, Star } from '@element-plus/icons-vue'
import axios from 'axios'
import { waitForAuth } from '../utils/authState'

const filters = ref({
  status: '',
  teacher_id: '',
  template_id: ''
})

const tasks = ref([])
const loading = ref(false)
const scoreLoading = ref(false)
const viewMode = ref('template') // 默认按模板分组显示

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

// 计算按模板分组的任务
const groupedTasks = computed(() => {
  if (viewMode.value !== 'template') return []
  
  const groups = new Map()
  
  tasks.value.forEach((task: any) => {
    const templateId = task.template_id
    
    if (!groups.has(templateId)) {
      groups.set(templateId, {
        template_id: templateId,
        template_name: task.template_name,
        teacher_count: 0,
        status_counts: {
          pending: 0,
          viewed: 0,
          submitted: 0,
          scored: 0
        },
        deadline: task.deadline,
        tasks: []
      })
    }
    
    const group = groups.get(templateId)
    group.teacher_count++
    group.tasks.push(task)
    
    // 统计状态
    const status = task.display_status || task.status
    if (group.status_counts[status] !== undefined) {
      group.status_counts[status]++
    }
  })
  
  return Array.from(groups.values())
})

const scoreDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const filesDialogVisible = ref(false)
const scoreDetailDialogVisible = ref(false)  // ← 新增
const batchScoreDialogVisible = ref(false)
const selectedTasks = ref<any[]>([])
const batchScoreLoading = ref(false)
const batchScoreOptions = ref({
  scoreType: 'manual',
  defaultScore: 80,
  overwrite: false
})

// Export dialog state
const exportDialogVisible = ref(false)
const exportLoading = ref(false)
const exporting = ref(false)
const exportData = ref<any[]>([])
const exportFilters = ref({
  fileType: '',
  grade: '',
  startDate: null,
  endDate: null
})

const currentTask = ref<any>(null)
const scoreData = ref({
  scores: {} as Record<string, number>,
  feedback: ''
})

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '未查收',
    viewed: '已查收',
    submitted: '已提交',
    scored: '已评分'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    viewed: 'warning',
    submitted: 'warning',
    scored: 'success'
  }
  return typeMap[status] || 'info'
}

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8001/api/evaluation-tasks', {
      params: {
        ...filters.value,
        page: pagination.value.page,
        page_size: pagination.value.pageSize
      },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    })
    
    tasks.value = response.data.tasks || []
    pagination.value.total = response.data.total || 0
    
  } catch (error: any) {
    console.error('加载任务失败:', error)
    ElMessage.error(`加载任务失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    teacher_id: '',
    template_id: ''
  }
  pagination.value.page = 1
  loadTasks()
}

const openScoreDialog = (task: any) => {
  currentTask.value = task
  
  // 初始化评分数据 - 使用对象格式而不是数组
  if (task.scoring_criteria && task.scoring_criteria.length > 0) {
    const scoresObj: Record<string, number> = {}
    task.scoring_criteria.forEach((criterion: any) => {
      // 如果已有评分，使用已有的；否则初始化为0
      scoresObj[criterion.name] = (task.scores && task.scores[criterion.name]) || 0
    })
    scoreData.value = {
      scores: scoresObj,
      feedback: task.scoring_feedback || ''
    }
  } else {
    scoreData.value = {
      scores: {},
      feedback: ''
    }
  }
  
  scoreDialogVisible.value = true
}

const calculateTotalScore = () => {
  if (!currentTask.value?.scoring_criteria) return 0
  // scoreData.scores is now an object: { "完成度": 8, "准确性": 9, ... }
  const total = Object.values(scoreData.value.scores).reduce((sum: number, score: any) => sum + (score || 0), 0)
  return total
}

const calculatePercentage = () => {
  const total = calculateTotalScore()
  const maxScore = currentTask.value?.total_score || 100
  if (maxScore === 0) return 0
  const percentage = Math.round((total / maxScore) * 100)
  return percentage
}

const getScoreType = (percentage: number) => {
  if (percentage >= 90) return 'success'
  if (percentage >= 80) return 'primary'
  if (percentage >= 70) return 'warning'
  if (percentage >= 60) return 'info'
  return 'danger'
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 80) return '#409eff'
  if (percentage >= 70) return '#e6a23c'
  if (percentage >= 60) return '#909399'
  return '#f56c6c'
}

// 格式化反馈内容，将结构化文本转换为HTML
const formatFeedback = (feedback: string) => {
  if (!feedback) return ''
  
  // 替换【标题】为带样式的标题
  let formatted = feedback.replace(/【([^】]+)】/g, '<h5 class="feedback-title">$1</h5>')
  
  // 替换 • 开头的列表项
  formatted = formatted.replace(/^•\s+(.+)$/gm, '<li class="feedback-item">$1</li>')
  
  // 将连续的列表项包裹在 ul 标签中
  formatted = formatted.replace(/(<li class="feedback-item">.*?<\/li>\s*)+/gs, '<ul class="feedback-list">$&</ul>')
  
  // 替换换行符为 <br>
  formatted = formatted.replace(/\n/g, '<br>')
  
  // 包裹在段落中
  formatted = `<div class="formatted-feedback">${formatted}</div>`
  
  return formatted
}

const onScoreChange = () => {
  // 触发重新渲染
}

const resetScoreData = () => {
  scoreData.value = {
    scores: {},
    feedback: ''
  }
}

const submitScore = async () => {
  if (!currentTask.value) return

  scoreLoading.value = true
  try {
    // scoreData.scores 已经是对象格式: { "完成度": 8, "准确性": 9, ... }
    const scoresObj = scoreData.value.scores
    const scoresJson = JSON.stringify(scoresObj)

    // 构建Query参数
    const params = new URLSearchParams()
    params.append('scores', scoresJson)
    params.append('feedback', scoreData.value.feedback)

    const response = await axios.post(
      `http://localhost:8001/api/evaluation-tasks/${currentTask.value.task_id}/score?${params.toString()}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      }
    )

    ElMessage.success('评分成功')
    scoreDialogVisible.value = false
    loadTasks()
  } catch (error: any) {
    console.error('评分错误:', error)
    ElMessage.error(`评分失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    scoreLoading.value = false
  }
}

const viewDetail = (task: any) => {
  currentTask.value = task
  detailDialogVisible.value = true
}

const viewFiles = (task: any) => {
  currentTask.value = task
  filesDialogVisible.value = true
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const downloadFile = (file: any) => {
  ElMessage.info('下载功能开发中...')
}

// 监听评分数据变化，实时更新总分
watch(
  () => scoreData.value.scores,
  (newScores) => {
    // 触发重新渲染
  },
  { deep: true }
)

const viewScore = (task: any) => {
  currentTask.value = task
  scoreDetailDialogVisible.value = true
}

// 处理显示模式变化
const handleViewModeChange = () => {
  console.log('切换显示模式:', viewMode.value)
}

// 查看模板详情（按模板分组时）
const viewTemplateDetails = (group: any) => {
  ElMessage.info(`模板: ${group.template_name}, 共分配给 ${group.teacher_count} 位教师`)
  // 可以打开一个对话框显示详细信息
}

// 切换到按教师查看
const switchToTeacherView = (templateId: string) => {
  viewMode.value = 'teacher'
  filters.value.template_id = templateId
  loadTasks()
}

// 处理表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedTasks.value = selection
}

// 清除选择
const clearSelection = () => {
  selectedTasks.value = []
}

// AI自动评分单个任务
const autoScore = async (task: any) => {
  if (!task) return

  // 设置加载状态
  task.autoScoring = true
  
  try {
    ElMessage.info('正在调用DeepSeek AI进行自动评分，请稍候...')
    
    // 调用自动评分API
    const response = await axios.post(
      `http://localhost:8001/api/scoring/score/${task.task_id}`,
      [], // 空的加分项数组
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        timeout: 60000 // 60秒超时
      }
    )

    if (response.data.success) {
      const result = response.data.scoring_result
      
      // 显示评分结果
      ElMessage({
        type: 'success',
        message: `AI自动评分完成！得分: ${result.final_score}分 (${result.grade})`,
        duration: 5000
      })
      
      // 显示详细结果
      showAutoScoreResult(result, task)
      
      // 刷新任务列表
      loadTasks()
    } else {
      ElMessage.error('自动评分失败')
    }
  } catch (error: any) {
    console.error('自动评分错误:', error)
    let errorMsg = '自动评分失败'
    
    if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail
    } else if (error.message) {
      errorMsg = error.message
    }
    
    ElMessage.error(errorMsg)
  } finally {
    task.autoScoring = false
  }
}

// 显示自动评分结果
const showAutoScoreResult = (result: any, task: any) => {
  const h = ElMessage
  
  let message = `🎉 AI自动评分完成！\n\n`
  message += `📊 最终得分: ${result.final_score}分\n`
  message += `📈 评定等级: ${result.grade}\n`
  message += `⚠️ 触发否决: ${result.veto_triggered ? '是' : '否'}\n`
  
  if (result.veto_triggered) {
    message += `🚫 否决原因: ${result.veto_reason}\n`
  } else if (result.score_details && result.score_details.length > 0) {
    message += `\n📋 详细评分:\n`
    result.score_details.forEach((detail: any) => {
      message += `• ${detail.indicator}: ${detail.score}/${detail.max_score}分\n`
    })
  }
  
  if (result.summary) {
    message += `\n💬 AI评价: ${result.summary.substring(0, 100)}...\n`
  }
  
  ElMessageBox.alert(message, 'AI自动评分结果', {
    confirmButtonText: '查看详情',
    type: result.veto_triggered ? 'warning' : 'success',
    callback: () => {
      // 打开评分详情对话框
      viewScore(task)
    }
  })
}

// AI批量自动评分
const batchAutoScore = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择要评分的任务')
    return
  }

  // 确认对话框
  try {
    await ElMessageBox.confirm(
      `确定要对选中的 ${selectedTasks.value.length} 个任务进行AI自动评分吗？\n\n这将调用DeepSeek API对每个提交的文件进行智能评分。`,
      'AI批量自动评分确认',
      {
        confirmButtonText: '开始评分',
        cancelButtonText: '取消',
        type: 'info',
        beforeClose: (action, instance, done) => {
          if (action === 'confirm') {
            instance.confirmButtonLoading = true
            instance.confirmButtonText = '评分中...'
            executeBatchAutoScore().finally(() => {
              done()
            })
          } else {
            done()
          }
        }
      }
    )
  } catch {
    // 用户取消
    return
  }
}

// 执行AI批量自动评分
const executeBatchAutoScore = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择要评分的任务')
    return
  }

  batchScoreLoading.value = true
  
  try {
    // 获取提交ID列表
    const submission_ids = selectedTasks.value.map((task: any) => task.task_id)
    
    ElMessage.info(`开始AI批量评分 ${submission_ids.length} 个任务，请耐心等待...`)
    
    const response = await axios.post(
      'http://localhost:8001/api/scoring/batch-score',
      submission_ids,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        timeout: 300000 // 5分钟超时，因为批量评分需要更长时间
      }
    )

    const { total, success, failed, results } = response.data
    
    // 显示结果统计
    let message = `🎉 AI批量评分完成！\n\n`
    message += `📊 总数: ${total}\n`
    message += `✅ 成功: ${success}\n`
    message += `❌ 失败: ${failed}\n`
    message += `📈 成功率: ${Math.round((success / total) * 100)}%\n`
    
    if (results && results.length > 0) {
      message += `\n📋 详细结果:\n`
      results.slice(0, 5).forEach((result: any, index: number) => {
        if (result.success) {
          const scoring = result.scoring_result
          message += `${index + 1}. ✅ ${scoring.final_score}分 (${scoring.grade})\n`
        } else {
          message += `${index + 1}. ❌ ${result.error}\n`
        }
      })
      
      if (results.length > 5) {
        message += `... 还有 ${results.length - 5} 个结果\n`
      }
    }
    
    ElMessageBox.alert(message, 'AI批量评分结果', {
      confirmButtonText: '确定',
      type: success > 0 ? 'success' : 'warning'
    })
    
    // 清除选择并刷新列表
    selectedTasks.value = []
    loadTasks()
    
  } catch (error: any) {
    console.error('AI批量评分错误:', error)
    let errorMsg = 'AI批量评分失败'
    
    if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail
    } else if (error.message) {
      errorMsg = error.message
    }
    
    ElMessage.error(errorMsg)
  } finally {
    batchScoreLoading.value = false
  }
}

// 批量评分
const batchScore = () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择要评分的任务')
    return
  }
  batchScoreDialogVisible.value = true
}

// 执行批量评分
const executeBatchScore = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择要评分的任务')
    return
  }

  batchScoreLoading.value = true
  try {
    const submission_ids = selectedTasks.value.map((task: any) => task.task_id)
    
    const response = await axios.post(
      'http://localhost:8001/api/scoring/batch-score',
      {
        submission_ids: submission_ids
      },
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      }
    )

    ElMessage.success(`批量评分完成: 成功 ${response.data.success} 项，失败 ${response.data.failed} 项`)
    batchScoreDialogVisible.value = false
    selectedTasks.value = []
    loadTasks()
  } catch (error: any) {
    console.error('批量评分错误:', error)
    ElMessage.error(`批量评分失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    batchScoreLoading.value = false
  }
}

// 重置批量评分数据
const resetBatchScoreData = () => {
  batchScoreOptions.value = {
    scoreType: 'manual',
    defaultScore: 80,
    overwrite: false
  }
}

// 打开导出对话框
const openExportDialog = () => {
  exportDialogVisible.value = true
  exportData.value = []
  resetExportFilters()
}

// 重置导出筛选条件
const resetExportFilters = () => {
  exportFilters.value = {
    fileType: '',
    grade: '',
    startDate: null,
    endDate: null
  }
  exportData.value = []
}

// 重置导出数据
const resetExportData = () => {
  exportData.value = []
  resetExportFilters()
}

// 加载导出数据
const loadExportData = async () => {
  exportLoading.value = true
  try {
    const params: any = {}
    
    if (exportFilters.value.fileType) {
      params.file_type = exportFilters.value.fileType
    }
    if (exportFilters.value.grade) {
      params.grade = exportFilters.value.grade
    }
    if (exportFilters.value.startDate) {
      params.start_date = exportFilters.value.startDate.toISOString().split('T')[0]
    }
    if (exportFilters.value.endDate) {
      params.end_date = exportFilters.value.endDate.toISOString().split('T')[0]
    }
    
    const response = await axios.get('http://localhost:8001/api/scoring/export', {
      params,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    })
    
    exportData.value = response.data.data || []
    ElMessage.success(`加载成功: ${exportData.value.length} 条数据`)
  } catch (error: any) {
    console.error('加载导出数据失败:', error)
    ElMessage.error(`加载导出数据失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    exportLoading.value = false
  }
}

// 计算平均分
const calculateAverageScore = () => {
  if (exportData.value.length === 0) return 0
  const sum = exportData.value.reduce((acc, item) => acc + (item.final_score || 0), 0)
  return sum / exportData.value.length
}

// 计算最高分
const calculateMaxScore = () => {
  if (exportData.value.length === 0) return 0
  return Math.max(...exportData.value.map(item => item.final_score || 0))
}

// 计算最低分
const calculateMinScore = () => {
  if (exportData.value.length === 0) return 0
  return Math.min(...exportData.value.map(item => item.final_score || 0))
}

// 获取等级类型
const getGradeType = (grade: string) => {
  const typeMap: Record<string, string> = {
    '优秀': 'success',
    '良好': 'primary',
    '合格': 'warning',
    '不合格': 'danger'
  }
  return typeMap[grade] || 'info'
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 执行导出
const executeExport = async () => {
  if (exportData.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  exporting.value = true
  try {
    // 创建工作簿数据
    const headers = [
      '提交ID',
      '文件名',
      '文件类型',
      '基础分',
      '加分',
      '最终得分',
      '等级',
      '评分类型',
      '评分时间',
      '已确认'
    ]
    
    const rows = exportData.value.map(item => [
      item.submission_id,
      item.file_name,
      item.file_type,
      item.base_score,
      item.bonus_score,
      item.final_score,
      item.grade,
      item.scoring_type === 'auto' ? '自动' : '手动',
      formatDate(item.scored_at),
      item.is_confirmed ? '是' : '否'
    ])
    
    // 创建CSV内容
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')
    
    // 创建Blob并下载
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', `评分结果_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
    exportDialogVisible.value = false
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(`导出失败: ${error.message}`)
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  // 等待认证准备就绪
  await waitForAuth();
  loadTasks()
})
</script>

<style scoped>
.evaluation-task-list {
  width: 100%;
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #003366;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.task-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.filters-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.filters-form {
  margin: 0;
}

.task-table {
  margin-bottom: 1.5rem;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.score-dialog {
  padding: 1rem 0;
}

.task-info {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.task-info p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.scoring-section {
  margin-bottom: 1.5rem;
}

.scoring-section h4 {
  margin-bottom: 1rem;
  color: #212121;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.score-item label {
  min-width: 100px;
  font-weight: 500;
}

.score-input {
  width: 120px;
}

.score-max {
  color: #757575;
  font-size: 0.9rem;
}

.total-score-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  margin-top: 1rem;
  font-size: 0.95rem;
}

.total-score-display strong {
  color: #ff3b30;
  font-size: 1.1rem;
}

.feedback-section {
  margin-bottom: 1rem;
}

.feedback-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.detail-dialog {
  padding: 1rem 0;
}

.criteria-section {
  margin-top: 1.5rem;
}

.criteria-section h4 {
  margin-bottom: 1rem;
  color: #212121;
}

.feedback-display {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.feedback-display h4 {
  margin-top: 0;
  color: #212121;
}

.feedback-display p {
  margin: 0;
  color: #424242;
  line-height: 1.8;
  white-space: pre-wrap; /* 保留换行符和空格 */
  word-wrap: break-word; /* 自动换行 */
}

.files-dialog {
  padding: 1rem 0;
}

.score-detail-dialog {
  padding: 1rem 0;
}

.score-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f6f8fb 0%, #e8f0f8 100%);
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.score-label {
  font-size: 0.9rem;
  color: #757575;
}

.score-value {
  font-size: 2rem;
  font-weight: bold;
  color: #ff3b30;
}

.score-max {
  font-size: 0.9rem;
  color: #757575;
}

.score-percentage {
  font-size: 1.5rem;
  font-weight: bold;
  color: #4CAF50;
}

.criteria-scores {
  margin-bottom: 1.5rem;
}

.criteria-scores h4 {
  margin-bottom: 1rem;
  color: #212121;
}

.criterion-score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #f0f0f0;
}

.criterion-name {
  font-weight: 500;
  color: #212121;
  min-width: 100px;
}

.criterion-value {
  color: #ff3b30;
  font-weight: bold;
  min-width: 80px;
  text-align: center;
}

.criterion-percentage {
  color: #4CAF50;
  font-weight: bold;
  min-width: 60px;
  text-align: right;
}

.feedback-section {
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.feedback-section h4 {
  margin-top: 0;
  color: #212121;
}

.feedback-section p {
  margin: 0;
  color: #424242;
  line-height: 1.6;
}

.score-info {
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.score-info p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
  color: #424242;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.action-buttons .el-button {
  margin: 0;
  padding: 4px 8px;
  font-size: 0.85rem;
}

.action-buttons .el-button .el-icon {
  margin-right: 2px;
}

/* 评分对话框样式 */
.score-dialog {
  padding: 0;
}

.task-info {
  margin-bottom: 1.5rem;
}

.scoring-section h4,
.feedback-section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  color: #212121;
  font-size: 1rem;
  font-weight: 600;
}

.score-items {
  margin-bottom: 1.5rem;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  margin-bottom: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.criterion-info {
  flex: 1;
  margin-right: 1rem;
}

.criterion-label {
  display: block;
  font-weight: 500;
  color: #212121;
  margin-bottom: 0.25rem;
}

.criterion-desc {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.4;
}

.score-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-input {
  width: 120px;
}

.score-max {
  color: #757575;
  font-size: 0.9rem;
  font-weight: 500;
}

.no-criteria {
  margin-bottom: 1.5rem;
}

.total-score-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f6f8fb 0%, #e8f0f8 100%);
  border-radius: 8px;
  margin-top: 1rem;
  border: 2px solid #e3f2fd;
}

.score-summary {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.score-label {
  font-size: 1rem;
  color: #424242;
  font-weight: 500;
}

.score-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #1976d2;
}

.score-percentage .el-tag {
  font-size: 1.1rem;
  font-weight: bold;
  padding: 8px 16px;
}

.feedback-section {
  margin-top: 1.5rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* 评分详情对话框样式 */
.score-detail-dialog {
  padding: 0;
}

.score-header {
  margin-bottom: 2rem;
}

.score-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.score-main {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.score-detail-dialog .score-label {
  font-size: 1rem;
  opacity: 0.9;
}

.score-detail-dialog .score-value {
  font-size: 2.5rem;
  font-weight: bold;
}

.score-detail-dialog .score-max {
  font-size: 1.2rem;
  opacity: 0.8;
}

.criteria-scores {
  margin-bottom: 2rem;
}

.criteria-scores h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  color: #212121;
  font-size: 1.1rem;
  font-weight: 600;
}

.criteria-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.criterion-card {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.criterion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.criterion-name {
  font-weight: 600;
  color: #212121;
  font-size: 0.95rem;
}

.criterion-score {
  font-weight: bold;
  color: #1976d2;
  font-size: 1rem;
}

.criterion-progress {
  margin-top: 0.5rem;
}

.criterion-reason {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background-color: #ffffff;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.criterion-reason .el-text {
  line-height: 1.6;
  display: block;
}

.feedback-section {
  margin-bottom: 2rem;
}

.feedback-section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  color: #212121;
  font-size: 1.1rem;
  font-weight: 600;
}

.feedback-content {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.feedback-content p {
  margin: 0;
  color: #424242;
  line-height: 1.8;
  font-size: 0.95rem;
  white-space: pre-wrap; /* 保留换行符和空格 */
  word-wrap: break-word; /* 自动换行 */
}

/* 结构化反馈样式 */
.structured-feedback .formatted-feedback {
  line-height: 1.8;
}

.structured-feedback .feedback-title {
  margin: 1.5rem 0 0.75rem 0;
  padding: 0.5rem 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.structured-feedback .feedback-title:first-child {
  margin-top: 0;
}

.structured-feedback .feedback-list {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
  list-style: none;
}

.structured-feedback .feedback-item {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
  color: #424242;
  line-height: 1.8;
}

.structured-feedback .feedback-item::before {
  content: "•";
  position: absolute;
  left: 0;
  color: #409eff;
  font-weight: bold;
  font-size: 1.2em;
}

.score-meta {
  margin-top: 1.5rem;
}

.status-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.status-summary .el-tag {
  font-size: 0.85rem;
}

/* 批量操作样式 */
.batch-operations {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.batch-score-dialog {
  padding: 0;
}

.batch-alert {
  margin-bottom: 1.5rem;
}

.batch-tasks-list {
  margin-bottom: 1.5rem;
}

.batch-tasks-list h4 {
  margin-bottom: 1rem;
  color: #212121;
  font-weight: 600;
}

.batch-options {
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.batch-options .form-hint {
  margin-left: 0.5rem;
  color: #757575;
  font-size: 0.85rem;
}

/* AI自动评分按钮样式 */
.action-buttons .el-button[type="primary"] {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 500;
}

.action-buttons .el-button[type="primary"]:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.batch-operations .el-button[type="primary"] {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 500;
  padding: 10px 20px;
}

.batch-operations .el-button[type="primary"]:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 加载状态样式 */
.el-button.is-loading {
  pointer-events: none;
}

.el-button.is-loading .el-icon {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.export-dialog {
  padding: 0;
}

.export-alert {
  margin-bottom: 1.5rem;
}

.export-filters {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.export-filters h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #212121;
  font-weight: 600;
}

.export-preview {
  margin-bottom: 1.5rem;
}

.export-preview h4 {
  margin-bottom: 1rem;
  color: #212121;
  font-weight: 600;
}

.export-stats {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.9rem;
  color: #757575;
  margin-bottom: 0.5rem;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #1976d2;
}
</style>
