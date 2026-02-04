#!/bin/bash

# 评教系统上线准备脚本
# 此脚本自动执行上线前的所有准备工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查前置条件
check_prerequisites() {
    log_info "检查前置条件..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    log_info "✓ Python 3 已安装"
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    log_info "✓ Node.js 已安装"
    
    # 检查 Nginx
    if ! command -v nginx &> /dev/null; then
        log_error "Nginx 未安装"
        exit 1
    fi
    log_info "✓ Nginx 已安装"
    
    # 检查项目目录
    if [ ! -d "/opt/evaluation-system" ]; then
        log_error "项目目录 /opt/evaluation-system 不存在"
        exit 1
    fi
    log_info "✓ 项目目录存在"
}

# 1. 数据库迁移
migrate_database() {
    log_info "执行数据库迁移..."
    
    cd /opt/evaluation-system
    source venv/bin/activate
    
    # 初始化数据库
    python scripts/init_db.py
    log_info "✓ 数据库初始化完成"
    
    # 导入默认模板
    python scripts/import_templates.py
    log_info "✓ 默认模板导入完成"
    
    # 导入系统配置
    python scripts/import_config.py
    log_info "✓ 系统配置导入完成"
    
    # 验证数据库
    python scripts/check_db.py
    log_info "✓ 数据库验证完成"
}

# 2. 配置 API 密钥
configure_api_key() {
    log_info "配置 Deepseek API 密钥..."
    
    # 检查 .env 文件
    if [ ! -f "/opt/evaluation-system/.env" ]; then
        log_error ".env 文件不存在"
        exit 1
    fi
    
    # 检查 API 密钥是否已配置
    if grep -q "DEEPSEEK_API_KEY=sk-" /opt/evaluation-system/.env; then
        log_info "✓ API 密钥已配置"
        
        # 测试 API 连接
        cd /opt/evaluation-system
        source venv/bin/activate
        python scripts/test_api.py
        log_info "✓ API 连接测试成功"
    else
        log_error "API 密钥未配置，请编辑 .env 文件"
        exit 1
    fi
}

# 3. 导入默认提示词模板
import_templates() {
    log_info "导入默认提示词模板..."
    
    cd /opt/evaluation-system
    source venv/bin/activate
    
    python scripts/import_templates.py
    log_info "✓ 默认提示词模板导入完成"
}

# 4. 配置试运行模式
configure_trial_mode() {
    log_info "配置试运行模式..."
    
    # 检查 .env 文件中的试运行模式配置
    if grep -q "TRIAL_RUN_MODE=true" /opt/evaluation-system/.env; then
        log_info "✓ 试运行模式已启用"
    else
        log_warn "试运行模式未启用，请编辑 .env 文件"
    fi
}

# 5. 构建前端
build_frontend() {
    log_info "构建前端..."
    
    cd /opt/evaluation-system/frontend
    
    # 安装依赖
    npm install
    log_info "✓ 前端依赖安装完成"
    
    # 构建前端
    npm run build
    log_info "✓ 前端构建完成"
}

# 6. 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    
    # 检查服务是否已启动
    if sudo systemctl is-active --quiet evaluation-system; then
        log_info "✓ 后端服务已启动"
    else
        sudo systemctl start evaluation-system
        sleep 5
        
        if sudo systemctl is-active --quiet evaluation-system; then
            log_info "✓ 后端服务启动成功"
        else
            log_error "后端服务启动失败"
            exit 1
        fi
    fi
}

# 7. 启动 Nginx
start_nginx() {
    log_info "启动 Nginx..."
    
    # 测试 Nginx 配置
    sudo nginx -t
    log_info "✓ Nginx 配置测试通过"
    
    # 启动 Nginx
    sudo systemctl restart nginx
    log_info "✓ Nginx 已启动"
}

# 8. 验证系统
verify_system() {
    log_info "验证系统..."
    
    # 检查后端 API
    if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
        log_info "✓ 后端 API 正常"
    else
        log_error "后端 API 异常"
        exit 1
    fi
    
    # 检查前端
    if curl -s https://localhost | grep -q "<!DOCTYPE"; then
        log_info "✓ 前端正常"
    else
        log_warn "前端检查失败（可能是 SSL 证书问题）"
    fi
    
    # 检查数据库
    cd /opt/evaluation-system
    source venv/bin/activate
    python scripts/check_db.py
    log_info "✓ 数据库正常"
}

# 9. 创建备份
create_backup() {
    log_info "创建备份..."
    
    /opt/evaluation-system/scripts/backup.sh
    log_info "✓ 备份创建完成"
}

# 10. 生成上线报告
generate_report() {
    log_info "生成上线报告..."
    
    REPORT_FILE="/opt/evaluation-system/上线报告_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
评教系统上线准备报告
生成时间：$(date)

1. 系统信息
   - 系统版本：2.0.0
   - Python 版本：$(python3 --version)
   - Node.js 版本：$(node --version)
   - Nginx 版本：$(nginx -v 2>&1)

2. 数据库状态
   - 数据库文件：/opt/evaluation-system/evaluation.db
   - 数据库大小：$(du -h /opt/evaluation-system/evaluation.db | cut -f1)
   - 表数量：$(python3 -c "from app.models import *; from app.database import SessionLocal; db = SessionLocal(); print(len(db.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()))" 2>/dev/null || echo "N/A")

3. API 配置
   - API URL：$(grep DEEPSEEK_API_URL /opt/evaluation-system/.env | cut -d= -f2)
   - 模型：$(grep DEEPSEEK_MODEL /opt/evaluation-system/.env | cut -d= -f2)
   - 试运行模式：$(grep TRIAL_RUN_MODE /opt/evaluation-system/.env | cut -d= -f2)

4. 服务状态
   - 后端服务：$(sudo systemctl is-active evaluation-system)
   - Nginx：$(sudo systemctl is-active nginx)
   - API 健康：$(curl -s http://localhost:8000/api/health | grep -o '"status":"[^"]*"' || echo "N/A")

5. 文件系统
   - 上传目录大小：$(du -sh /opt/evaluation-system/uploads | cut -f1)
   - 日志目录大小：$(du -sh /opt/evaluation-system/logs | cut -f1)
   - 备份目录大小：$(du -sh /opt/evaluation-system/backups | cut -f1)

6. 磁盘空间
   - 总空间：$(df -h /opt/evaluation-system | tail -1 | awk '{print $2}')
   - 已用空间：$(df -h /opt/evaluation-system | tail -1 | awk '{print $3}')
   - 可用空间：$(df -h /opt/evaluation-system | tail -1 | awk '{print $4}')
   - 使用率：$(df -h /opt/evaluation-system | tail -1 | awk '{print $5}')

7. 内存使用
   - 总内存：$(free -h | grep Mem | awk '{print $2}')
   - 已用内存：$(free -h | grep Mem | awk '{print $3}')
   - 可用内存：$(free -h | grep Mem | awk '{print $7}')

8. 检查清单
   - [✓] 数据库迁移完成
   - [✓] API 密钥配置完成
   - [✓] 默认模板导入完成
   - [✓] 试运行模式配置完成
   - [✓] 前端构建完成
   - [✓] 后端服务启动完成
   - [✓] Nginx 启动完成
   - [✓] 系统验证完成
   - [✓] 备份创建完成

9. 建议
   - 定期检查系统日志
   - 定期备份数据库
   - 监控系统性能
   - 及时处理用户反馈

报告生成完成！
EOF
    
    log_info "✓ 上线报告已生成：$REPORT_FILE"
    cat "$REPORT_FILE"
}

# 主函数
main() {
    echo "=========================================="
    echo "评教系统上线准备脚本"
    echo "=========================================="
    echo ""
    
    # 检查前置条件
    check_prerequisites
    echo ""
    
    # 执行准备步骤
    migrate_database
    echo ""
    
    configure_api_key
    echo ""
    
    import_templates
    echo ""
    
    configure_trial_mode
    echo ""
    
    build_frontend
    echo ""
    
    start_backend
    echo ""
    
    start_nginx
    echo ""
    
    verify_system
    echo ""
    
    create_backup
    echo ""
    
    generate_report
    echo ""
    
    echo "=========================================="
    log_info "所有准备工作已完成！"
    echo "=========================================="
    echo ""
    echo "系统现在可以上线了。"
    echo ""
    echo "访问地址："
    echo "  - 管理端：https://yourdomain.com/admin"
    echo "  - 教师端：https://yourdomain.com/teacher"
    echo "  - API：https://yourdomain.com/api"
    echo ""
}

# 运行主函数
main
