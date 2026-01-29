<template>
  <div class="peer-experience-exchange">
    <!-- 同行经验交流主卡片 -->
    <el-card class="exchange-card" shadow="hover">
      <template #header>
        <div class="exchange-header">
          <el-icon name="ChatDotRound"></el-icon>
          <span class="exchange-title">同行经验交流</span>
          <el-button type="primary" size="small" @click="showPostDialog = true">
            <el-icon name="EditPen"></el-icon>发布经验
          </el-button>
        </div>
      </template>
      
      <div class="exchange-content">
        <!-- 筛选和搜索区域 -->
        <div class="filter-search-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索经验分享..."
                size="large"
                prefix-icon="Search"
                @input="handleSearch"
              >
                <template #append>
                  <el-button @click="handleSearch">搜索</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select v-model="selectedCategory" placeholder="选择分类" size="large" @change="handleFilter">
                <el-option label="全部" value="all" />
                <el-option label="教学方法" value="teaching-method" />
                <el-option label="课程设计" value="course-design" />
                <el-option label="学生管理" value="student-management" />
                <el-option label="学术研究" value="academic-research" />
                <el-option label="职业发展" value="career-development" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="sortBy" placeholder="排序方式" size="large" @change="handleSort">
                <el-option label="最新发布" value="latest" />
                <el-option label="最多点赞" value="most-liked" />
                <el-option label="最多评论" value="most-commented" />
              </el-select>
            </el-col>
          </el-row>
        </div>
        
        <!-- 经验分享列表 -->
        <div class="posts-list">
          <el-card
            v-for="post in filteredPosts"
            :key="post.id"
            class="post-card"
            shadow="hover"
            size="small"
          >
            <div class="post-header">
              <div class="post-author">
                <el-avatar :size="40" :src="post.authorAvatar">{{ post.authorName.charAt(0) }}</el-avatar>
                <div class="author-info">
                  <div class="author-name">{{ post.authorName }}</div>
                  <div class="post-meta">
                    <span class="post-time">{{ post.publishTime }}</span>
                    <el-tag :type="getCategoryType(post.category)">{{ getCategoryName(post.category) }}</el-tag>
                  </div>
                </div>
              </div>
              <div class="post-actions">
                <el-dropdown @command="handlePostAction">
                  <el-button type="text" size="small">
                    <el-icon name="More"></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'report', postId: post.id }">举报</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'share', postId: post.id }">分享</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            
            <div class="post-body">
              <div class="post-title">{{ post.title }}</div>
              <div class="post-content">{{ post.content }}</div>
              
              <!-- 经验分享图片 -->
              <div v-if="post.images.length > 0" class="post-images">
                <el-image
                  v-for="(image, imgIndex) in post.images"
                  :key="imgIndex"
                  :src="image"
                  fit="cover"
                  :preview-src-list="post.images"
                  class="post-image"
                ></el-image>
              </div>
              
              <!-- 经验分享标签 -->
              <div v-if="post.tags.length > 0" class="post-tags">
                <el-tag size="small" v-for="(tag, tagIndex) in post.tags" :key="tagIndex">{{ tag }}</el-tag>
              </div>
            </div>
            
            <div class="post-footer">
              <div class="post-stats">
                <div class="stat-item" @click="toggleLike(post.id)">
                  <el-icon :name="post.isLiked ? 'StarFilled' : 'Star'" :color="post.isLiked ? '#e6a23c' : '#909399'" />
                  <span>{{ post.likes }}</span>
                </div>
                <div class="stat-item" @click="toggleFavorite(post.id)">
                  <el-icon :name="post.isFavorited ? 'CollectionFilled' : 'Collection'" :color="post.isFavorited ? '#f56c6c' : '#909399'" />
                  <span>{{ post.favorites }}</span>
                </div>
                <div class="stat-item" @click="showComments(post.id)">
                  <el-icon name="ChatLineRound" />
                  <span>{{ post.comments.length }}</span>
                </div>
                <div class="stat-item">
                  <el-icon name="View" />
                  <span>{{ post.views }}</span>
                </div>
              </div>
            </div>
            
            <!-- 评论区域 -->
            <div class="comments-section" v-if="post.showComments">
              <div class="comments-list">
                <div
                  v-for="(comment, commentIndex) in post.comments"
                  :key="commentIndex"
                  class="comment-item"
                >
                  <el-avatar :size="30" :src="comment.authorAvatar">{{ comment.authorName.charAt(0) }}</el-avatar>
                  <div class="comment-content">
                    <div class="comment-header">
                      <span class="comment-author">{{ comment.authorName }}</span>
                      <span class="comment-time">{{ comment.commentTime }}</span>
                    </div>
                    <div class="comment-text">{{ comment.text }}</div>
                    <div class="comment-actions">
                      <el-button type="text" size="small" @click="toggleCommentLike(post.id, commentIndex)">
                        <el-icon :name="comment.isLiked ? 'StarFilled' : 'Star'" :color="comment.isLiked ? '#e6a23c' : '#909399'" />
                        {{ comment.likes }}
                      </el-button>
                      <el-button type="text" size="small" @click="replyToComment(post.id, commentIndex)">
                        回复
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 评论输入框 -->
              <div class="comment-input-section">
                <el-input
                  v-model="newComments[post.id]"
                  placeholder="写下你的评论..."
                  type="textarea"
                  :rows="2"
                  @keyup.enter="addComment(post.id)"
                >
                  <template #append>
                    <el-button @click="addComment(post.id)">发表评论</el-button>
                  </template>
                </el-input>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 分页区域 -->
        <div class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredPosts.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          ></el-pagination>
        </div>
      </div>
    </el-card>
    
    <!-- 发布经验对话框 -->
    <el-dialog v-model="showPostDialog" title="发布经验分享" width="70%">
      <el-form :model="newPost" :rules="postRules" ref="postFormRef" label-width="120px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="newPost.title" placeholder="请输入经验分享标题" size="large" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="newPost.category" placeholder="选择分类" size="large">
                <el-option label="教学方法" value="teaching-method" />
                <el-option label="课程设计" value="course-design" />
                <el-option label="学生管理" value="student-management" />
                <el-option label="学术研究" value="academic-research" />
                <el-option label="职业发展" value="career-development" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标签" prop="tags">
              <el-select v-model="newPost.tags" placeholder="选择或输入标签" multiple collapse-tags size="large">
                <el-option label="翻转课堂" value="翻转课堂" />
                <el-option label="案例教学" value="案例教学" />
                <el-option label="混合式教学" value="混合式教学" />
                <el-option label="MOOC" value="MOOC" />
                <el-option label="PBL" value="PBL" />
                <el-option label="教学设计" value="教学设计" />
                <el-option label="课程思政" value="课程思政" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="newPost.content"
            type="textarea"
            :rows="8"
            placeholder="请输入经验分享内容..."
            size="large"
          />
        </el-form-item>
        
        <el-form-item label="图片">
          <el-upload
            v-model:file-list="newPost.images"
            action="#"
            list-type="picture-card"
            :auto-upload="false"
            :limit="5"
          >
            <el-icon name="Plus" class="avatar-uploader-icon"></el-icon>
            <template #file="{ file }">
              <img :src="file.url" alt="" class="el-upload-list__item-thumbnail" />
              <span class="el-upload-list__item-actions">
                <span class="el-upload-list__item-preview" @click="handlePictureCardPreview(file)">
                  <el-icon name="View"></el-icon>
                </span>
                <span class="el-upload-list__item-delete" @click="handleRemove(file)">
                  <el-icon name="Delete"></el-icon>
                </span>
              </span>
            </template>
          </el-upload>
          <el-dialog v-model="previewImageVisible">
            <img w-full :src="previewImageUrl" alt="preview" />
          </el-dialog>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showPostDialog = false">取消</el-button>
          <el-button type="primary" @click="submitPost">发布</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick } from 'vue'
import { ElMessage, FormInstance } from 'element-plus'

// 发布经验对话框
const showPostDialog = ref(false)
const postFormRef = ref<FormInstance | null>(null)
const newPost = reactive({
  title: '',
  category: '',
  tags: [] as string[],
  content: '',
  images: [] as any[]
})

const postRules = reactive({
  title: [{ required: true, message: '请输入经验分享标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入经验分享内容', trigger: 'blur' }]
})

// 图片预览
const previewImageVisible = ref(false)
const previewImageUrl = ref('')

const handlePictureCardPreview = (file: any) => {
  previewImageUrl.value = file.url
  previewImageVisible.value = true
}

const handleRemove = (file: any) => {
  const index = newPost.images.indexOf(file)
  if (index !== -1) {
    newPost.images.splice(index, 1)
  }
}

// 搜索和筛选
const searchKeyword = ref('')
const selectedCategory = ref('all')
const sortBy = ref('latest')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 评论
const newComments = ref<Record<number, string>>({})

// 经验分享帖子数据
const posts = ref([
  {
    id: 1,
    title: '如何有效开展翻转课堂教学',
    content: '翻转课堂是一种创新的教学模式，通过将传统课堂的教学内容提前让学生自学，课堂上专注于讨论和实践...',
    authorName: '李教授',
    authorAvatar: '',
    category: 'teaching-method',
    tags: ['翻转课堂', '教学创新', '混合式教学'],
    images: [],
    publishTime: '2024-01-15 14:30',
    likes: 45,
    favorites: 23,
    comments: [
      {
        id: 1,
        authorName: '王老师',
        authorAvatar: '',
        text: '非常实用的经验分享，我也尝试过翻转课堂，但效果不太理想，您能分享更多关于如何引导学生自学的技巧吗？',
        commentTime: '2024-01-16 09:20',
        likes: 12,
        isLiked: false
      },
      {
        id: 2,
        authorName: '张老师',
        authorAvatar: '',
        text: '我觉得翻转课堂最大的挑战是如何确保学生真的完成了课前学习任务，您有什么好的监督方法吗？',
        commentTime: '2024-01-16 14:45',
        likes: 8,
        isLiked: false
      }
    ],
    views: 320,
    isLiked: false,
    isFavorited: false,
    showComments: false
  },
  {
    id: 2,
    title: '课程思政融入刑法学教学的实践与思考',
    content: '课程思政是当前高校教学改革的重要方向，如何将思政元素自然融入专业课程教学中，是每个教师都需要思考的问题...',
    authorName: '刘教授',
    authorAvatar: '',
    category: 'course-design',
    tags: ['课程思政', '刑法学', '教学设计'],
    images: [],
    publishTime: '2024-01-10 09:15',
    likes: 62,
    favorites: 35,
    comments: [
      {
        id: 1,
        authorName: '陈老师',
        authorAvatar: '',
        text: '非常感谢您的分享，我也在尝试将课程思政融入我的课程中，但总觉得有些生硬，您能分享更多关于如何自然融入的技巧吗？',
        commentTime: '2024-01-10 11:30',
        likes: 15,
        isLiked: false
      }
    ],
    views: 480,
    isLiked: false,
    isFavorited: false,
    showComments: false
  },
  {
    id: 3,
    title: '如何激发学生的学习兴趣',
    content: '在长期的教学实践中，我发现学生的学习兴趣是影响教学效果的关键因素之一...',
    authorName: '赵老师',
    authorAvatar: '',
    category: 'student-management',
    tags: ['学习兴趣', '学生管理', '教学方法'],
    images: [],
    publishTime: '2024-01-05 16:45',
    likes: 38,
    favorites: 18,
    comments: [],
    views: 250,
    isLiked: false,
    isFavorited: false,
    showComments: false
  },
  {
    id: 4,
    title: '学术论文写作的技巧与方法',
    content: '学术论文写作是高校教师的必备技能之一，掌握一定的写作技巧可以提高论文的质量和发表成功率...',
    authorName: '孙教授',
    authorAvatar: '',
    category: 'academic-research',
    tags: ['学术论文', '写作技巧', '研究方法'],
    images: [],
    publishTime: '2024-01-01 10:00',
    likes: 29,
    favorites: 15,
    comments: [
      {
        id: 1,
        authorName: '周老师',
        authorAvatar: '',
        text: '非常实用的分享，我正准备写一篇论文，您的经验对我很有帮助，谢谢！',
        commentTime: '2024-01-02 08:45',
        likes: 5,
        isLiked: false
      }
    ],
    views: 190,
    isLiked: false,
    isFavorited: false,
    showComments: false
  }
])

// 筛选后的帖子
const filteredPosts = computed(() => {
  let result = [...posts.value]
  
  // 分类筛选
  if (selectedCategory.value !== 'all') {
    result = result.filter(post => post.category === selectedCategory.value)
  }
  
  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(post => 
      post.title.toLowerCase().includes(keyword) || 
      post.content.toLowerCase().includes(keyword) ||
      post.tags.some(tag => tag.toLowerCase().includes(keyword))
    )
  }
  
  // 排序
  switch (sortBy.value) {
    case 'latest':
      result.sort((a, b) => new Date(b.publishTime).getTime() - new Date(a.publishTime).getTime())
      break
    case 'most-liked':
      result.sort((a, b) => b.likes - a.likes)
      break
    case 'most-commented':
      result.sort((a, b) => b.comments.length - a.comments.length)
      break
  }
  
  return result
})

// 分页处理
// const paginatedPosts = computed(() => {
//   const start = (currentPage.value - 1) * pageSize.value
//   const end = start + pageSize.value
//   return filteredPosts.value.slice(start, end)
// })

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
}

// 处理筛选
const handleFilter = () => {
  currentPage.value = 1
}

// 处理排序
const handleSort = () => {
  currentPage.value = 1
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

// 处理当前页变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 切换点赞状态
const toggleLike = (postId: number) => {
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    post.isLiked = !post.isLiked
    post.likes += post.isLiked ? 1 : -1
    ElMessage.success(post.isLiked ? '点赞成功' : '取消点赞')
  }
}

// 切换收藏状态
const toggleFavorite = (postId: number) => {
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    post.isFavorited = !post.isFavorited
    post.favorites += post.isFavorited ? 1 : -1
    ElMessage.success(post.isFavorited ? '收藏成功' : '取消收藏')
  }
}

// 显示/隐藏评论
const showComments = (postId: number) => {
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    post.showComments = !post.showComments
  }
}

// 添加评论
const addComment = (postId: number) => {
  const post = posts.value.find(p => p.id === postId)
  const commentText = newComments.value[postId]
  
  if (post && commentText) {
    post.comments.push({
      id: post.comments.length + 1,
      authorName: '张老师', // 当前登录用户
      authorAvatar: '',
      text: commentText,
      commentTime: new Date().toLocaleString(),
      likes: 0,
      isLiked: false
    })
    
    newComments.value[postId] = ''
    ElMessage.success('评论成功')
  }
}

// 切换评论点赞状态
const toggleCommentLike = (postId: number, commentIndex: number) => {
  const post = posts.value.find(p => p.id === postId)
  if (post && post.comments[commentIndex]) {
    const comment = post.comments[commentIndex]
    comment.isLiked = !comment.isLiked
    comment.likes += comment.isLiked ? 1 : -1
  }
}

// 回复评论
const replyToComment = (postId: number, commentIndex: number) => {
  const post = posts.value.find(p => p.id === postId)
  if (post && post.comments[commentIndex]) {
    const comment = post.comments[commentIndex]
    newComments.value[postId] = `@${comment.authorName} `
    
    // 显示评论区域
    post.showComments = true
    
    // 聚焦到评论输入框
    nextTick(() => {
      const inputElement = document.querySelector(`.comment-input-section textarea`)
      if (inputElement) {
        (inputElement as HTMLTextAreaElement).focus()
      }
    })
  }
}

// 处理帖子操作
const handlePostAction = (command: any) => {
  const { action, postId } = command
  const post = posts.value.find(p => p.id === postId)
  
  if (post) {
    switch (action) {
      case 'report':
        ElMessage.warning('举报功能开发中...')
        break
      case 'share':
        ElMessage.success('分享成功')
        break
    }
  }
}

// 提交新帖子
const submitPost = () => {
  if (!postFormRef.value) return
  
  postFormRef.value.validate((valid) => {
    if (valid) {
      // 创建新帖子
      const newPostId = posts.value.length + 1
      
      posts.value.unshift({
        id: newPostId,
        title: newPost.title,
        content: newPost.content,
        authorName: '张老师', // 当前登录用户
        authorAvatar: '',
        category: newPost.category,
        tags: newPost.tags,
        images: [],
        publishTime: new Date().toLocaleString(),
        likes: 0,
        favorites: 0,
        comments: [],
        views: 0,
        isLiked: false,
        isFavorited: false,
        showComments: false
      })
      
      // 关闭对话框并重置表单
      showPostDialog.value = false
      postFormRef.value?.resetFields()
      newPost.images = []
      
      ElMessage.success('经验分享发布成功')
    }
  })
}

// 生成预测报告
// const generatePredictionReport = () => {
//   ElMessage.success('预测报告生成功能开发中...')
// }

// 获取分类名称
const getCategoryName = (category: string) => {
  const categoryMap: Record<string, string> = {
    'teaching-method': '教学方法',
    'course-design': '课程设计',
    'student-management': '学生管理',
    'academic-research': '学术研究',
    'career-development': '职业发展'
  }
  return categoryMap[category] || category
}

// 获取分类类型
const getCategoryType = (category: string) => {
  const typeMap: Record<string, string> = {
    'teaching-method': 'primary',
    'course-design': 'success',
    'student-management': 'warning',
    'academic-research': 'info',
    'career-development': 'danger'
  }
  return typeMap[category] || 'primary'
}
</script>

<style scoped>
.peer-experience-exchange {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.exchange-card {
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e9ecef;
}

.exchange-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.exchange-title {
  margin-left: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.exchange-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 筛选和搜索区域 */
.filter-search-section {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

/* 经验分享列表 */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 15px;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.author-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.post-time {
  font-size: 12px;
}

.post-body {
  margin-bottom: 20px;
}

.post-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.post-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  display: box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  box-orient: vertical;
}

.post-images {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.post-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  object-fit: cover;
}

.post-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.post-footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
}

.post-stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.3s ease;
}

.stat-item:hover {
  color: #409eff;
}

/* 评论区域 */
.comments-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.comment-item {
  display: flex;
  gap: 15px;
}

.comment-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-author {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.comment-actions {
  display: flex;
  gap: 20px;
}

.comment-input-section {
  margin-top: 15px;
}

/* 分页区域 */
.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-search-section .el-row {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-search-section .el-col {
    width: 100% !important;
  }
  
  .post-stats {
    gap: 20px;
  }
  
  .post-title {
    font-size: 16px;
  }
  
  .post-content {
    -webkit-line-clamp: 3;
    line-clamp: 3;
  }
  
  .post-images {
    flex-wrap: wrap;
  }
  
  .post-image {
    width: 80px;
    height: 80px;
  }
}
</style>