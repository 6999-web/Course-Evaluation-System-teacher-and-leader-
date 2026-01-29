<template>
  <div class="template-library page-container">
    <div class="content-container">
      <!-- 页面标题 -->
      <h2 class="page-title">
        评教模板参考库
      </h2>

    <!-- 筛选和搜索区域 -->
    <div class="template-header">
      <!-- 分类标签 -->
      <div class="category-tabs">
        <button 
          v-for="category in categories" 
          :key="category.id"
          :class="['category-tab', { active: activeCategory === category.id }]"
          @click="activeCategory = category.id"
        >
          {{ category.name }}
        </button>
      </div>

      <!-- 搜索框 -->
      <div class="search-container">
        <input
          type="text"
          v-model="searchKeyword"
          placeholder="输入模板名称或关键词..."
          class="search-input"
        />
      </div>
    </div>

    <!-- 模板列表 -->
    <div class="template-grid">
      <div 
        v-for="template in filteredTemplates" 
        :key="template.id"
        class="template-card"
      >
        <!-- 模板名称 -->
        <h3 class="template-name">{{ template.name }}</h3>
        
        <!-- 模板描述 -->
        <p class="template-description">{{ template.description }}</p>
        
        <!-- 模板信息 -->
        <div class="template-info">
          <div class="template-format">
            <span class="format-icon">{{ template.format === 'docx' ? '📄' : '📊' }}</span>
            <span class="format-text">{{ template.format.toUpperCase() }}</span>
          </div>
          <div class="template-version">
            系统版本：{{ template.lastUpdate }}
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="template-actions">
          <button 
            class="action-btn preview-btn"
            @click="previewTemplate(template)"
          >
            预览
          </button>
          <button 
            class="action-btn download-btn"
            @click="downloadTemplate(template)"
          >
            下载
          </button>
        </div>
      </div>
    </div>

    <!-- 无结果提示 -->
    <div v-if="filteredTemplates.length === 0" class="no-results">
      未找到匹配的模板
    </div>

    <!-- 预览弹窗 -->
    <div v-if="previewTemplateData" class="preview-modal">
      <div class="preview-modal-content">
        <div class="preview-modal-header">
          <h3>{{ previewTemplateData.name }}</h3>
          <button class="close-btn" @click="previewTemplateData = null">&times;</button>
        </div>
        <div class="preview-modal-body">
          <p class="preview-description">{{ previewTemplateData.description }}</p>
          <div class="preview-info">
            <p>格式：{{ previewTemplateData.format.toUpperCase() }}</p>
            <p>分类：{{ getCategoryName(previewTemplateData.category) }}</p>
            <p>版本：{{ previewTemplateData.lastUpdate }}</p>
          </div>
          <div class="preview-actions">
            <button class="action-btn download-btn" @click="downloadTemplate(previewTemplateData)">
              下载模板
            </button>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import { templateList } from '../data/templateData.js';

export default {
  name: 'TemplateLibrary',
  data() {
    return {
      activeCategory: 'all',
      searchKeyword: '',
      previewTemplateData: null,
      categories: [
        { id: 'all', name: '全部' },
        { id: '课堂教学评价', name: '课堂教学' },
        { id: '课程评估', name: '课程评估' },
        { id: '专项检查', name: '专项检查' },
        { id: '实践教学', name: '实践教学' },
        { id: '综合调研', name: '综合调研' }
      ]
    };
  },
  computed: {
    filteredTemplates() {
      return templateList.filter(template => {
        // 分类筛选
        const categoryMatch = this.activeCategory === 'all' || template.category === this.activeCategory;
        
        // 关键词搜索
        const keywordMatch = !this.searchKeyword || 
          template.name.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          template.description.toLowerCase().includes(this.searchKeyword.toLowerCase());
        
        return categoryMatch && keywordMatch;
      });
    }
  },
  methods: {
    previewTemplate(template) {
      this.previewTemplateData = template;
    },
    downloadTemplate(template) {
      // 模拟下载功能
      console.log('下载模板:', template.name);
      // 实际项目中，这里应该使用 a 标签或其他方式触发文件下载
      const link = document.createElement('a');
      link.href = template.filePath;
      link.download = template.name + '.' + template.format;
      link.click();
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(cat => cat.id === categoryId);
      return category ? category.name : categoryId;
    }
  }
};
</script>

<style scoped>
.template-library {
  padding: 20px;
}

.template-header {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.category-tab {
  padding: 8px 16px;
  border: 1px solid #d0d0d0;
  border-radius: 20px;
  background-color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.category-tab:hover {
  background-color: #f5f5f5;
  border-color: #003366;
}

.category-tab.active {
  background-color: #003366;
  color: #ffffff;
  border-color: #003366;
}

.search-container {
  width: 100%;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid #d0d0d0;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: #003366;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.template-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.template-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.template-name {
  font-size: 16px;
  font-weight: 600;
  color: #003366;
  margin: 0 0 10px 0;
}

.template-description {
  font-size: 14px;
  color: #666666;
  margin: 0 0 15px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.template-format {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999999;
}

.format-icon {
  font-size: 16px;
}

.template-version {
  font-size: 12px;
  color: #999999;
}

.template-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.preview-btn {
  background-color: #f0f0f0;
  color: #333333;
}

.preview-btn:hover {
  background-color: #e0e0e0;
}

.download-btn {
  background-color: #003366;
  color: #ffffff;
}

.download-btn:hover {
  background-color: #002244;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  color: #999999;
  font-size: 16px;
}

/* 预览弹窗 */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.preview-modal-content {
  background-color: #ffffff;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.preview-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.preview-modal-header h3 {
  margin: 0;
  color: #003366;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999999;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background-color: #f0f0f0;
  color: #333333;
}

.preview-modal-body {
  padding: 20px;
}

.preview-description {
  margin-bottom: 20px;
  line-height: 1.5;
  color: #666666;
}

.preview-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.preview-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #666666;
}

.preview-actions {
  display: flex;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .template-header {
    gap: 15px;
  }

  .category-tabs {
    gap: 8px;
  }

  .category-tab {
    padding: 6px 12px;
    font-size: 12px;
  }

  .template-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .template-card {
    padding: 16px;
  }

  .template-name {
    font-size: 15px;
  }

  .template-description {
    font-size: 13px;
  }
}
</style>