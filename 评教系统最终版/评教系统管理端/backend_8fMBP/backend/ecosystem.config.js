// module.exports = {
//   apps: [{
//     name: "backend-api",        // 进程名（方便后续管理）
//     script: "uvicorn",          // 启动命令
//   // args: "app.main:app --host 0.0.0.0 --port 8000 --workers 4",  // 启动参数（多进程提升性能）
//     args: "main:app --host 0.0.0.0 --port 8000 --workers 4",
//     interpreter: "python",     // 指定Python解释器
//     autorestart: true,          // 服务崩溃自动重启
//     watch: false,               // 生产环境关闭文件监听
//     max_memory_restart: "1G",   // 内存超1G自动重启
//     log_date_format: "YYYY-MM-DD HH:mm:ss",
//     error_file: "./logs/err.log",  // 错误日志路径
//     out_file: "./logs/out.log"     // 正常日志路径
//   }]
// };
module.exports = {
  apps: [
    {
      name: "backend",        // 服务名称
      script: "python",       // 执行脚本的命令
      args: "-m uvicorn app.main:app --host 0.0.0.0 --port 8000",  // 命令参数
      cwd: "/www/wwwroot/backend",   // 项目目录
      instances: 1,           // 启动实例数
      autorestart: true,      // 崩溃后自动重启
      watch: false,           // 禁用文件监听（避免代码变动时频繁重启）
      max_memory_restart: "1G", // 内存使用超过 1G 时重启
      env: {
        NODE_ENV: "production"
      }
    }
  ]
};