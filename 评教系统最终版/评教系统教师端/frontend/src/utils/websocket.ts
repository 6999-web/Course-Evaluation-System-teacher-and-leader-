import { io, Socket } from 'socket.io-client'

class WebSocketService {
  private socket: Socket | null = null
  private listeners: Map<string, ((data: any) => void)[]> = new Map()

  // 连接WebSocket服务器
  connect(departmentId?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // 创建WebSocket连接
        this.socket = io('/ws/monitoring', {
          query: { department_id: departmentId },
          transports: ['websocket'],
          timeout: 5000
        })

        // 连接成功事件
        this.socket.on('connect', () => {
          console.log('WebSocket连接成功')
          resolve()
        })

        // 连接错误事件
        this.socket.on('connect_error', (error) => {
          console.error('WebSocket连接错误:', error)
          reject(error)
        })

        // 断开连接事件
        this.socket.on('disconnect', () => {
          console.log('WebSocket连接断开')
        })

        // 实时更新事件
        this.socket.on('REALTIME_UPDATE', (data) => {
          this.notifyListeners('REALTIME_UPDATE', data)
        })

        // 异常预警事件
        this.socket.on('WARNING_ALERT', (data) => {
          this.notifyListeners('WARNING_ALERT', data)
        })

        // 状态变更事件
        this.socket.on('STATUS_CHANGE', (data) => {
          this.notifyListeners('STATUS_CHANGE', data)
        })
      } catch (error) {
        console.error('WebSocket初始化错误:', error)
        reject(error)
      }
    })
  }

  // 断开WebSocket连接
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.listeners.clear()
    }
  }

  // 发送消息
  emit(event: string, data: any): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.socket) {
        reject(new Error('WebSocket未连接'))
        return
      }

      try {
        this.socket.emit(event, data, () => {
          resolve()
        })
      } catch (error) {
        reject(error)
      }
    })
  }

  // 监听事件
  on(event: string, callback: (data: any) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)?.push(callback)
  }

  // 取消监听事件
  off(event: string, callback?: (data: any) => void): void {
    if (!this.listeners.has(event)) {
      return
    }

    if (callback) {
      // 移除特定回调
      const callbacks = this.listeners.get(event)?.filter(cb => cb !== callback)
      if (callbacks) {
        this.listeners.set(event, callbacks)
      }
    } else {
      // 移除所有回调
      this.listeners.delete(event)
    }
  }

  // 通知所有监听器
  private notifyListeners(event: string, data: any): void {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`WebSocket事件处理错误 [${event}]:`, error)
        }
      })
    }
  }

  // 获取连接状态
  get isConnected(): boolean {
    return this.socket?.connected || false
  }

  // 重新连接
  reconnect(departmentId?: string): Promise<void> {
    this.disconnect()
    return this.connect(departmentId)
  }
}

// 创建单例实例
export const websocketService = new WebSocketService()