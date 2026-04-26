// 消息类型定义
export type MessageRole = 'user' | 'assistant' | 'system' | 'tool'

export interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: number
  agent?: string
  toolName?: string
  toolResult?: string
  toolCallId?: ReturnType<typeof setTimeout>  // 定时器ID，用于超时处理
  isThinking?: boolean
  isError?: boolean
}

// 工作流节点状态
export type NodeStatus = 'pending' | 'running' | 'success' | 'failed'

export interface WorkflowNode {
  id: string
  label: string
  type: string
  status: NodeStatus
  data?: {
    input?: any
    output?: any
    error?: string
    duration?: number
  }
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  type?: string
  animated?: boolean
}

// SSE 事件类型
export interface SSEEvent {
  type: 'agent' | 'content' | 'tool' | 'tool_result' | 'confirm' | 'error' | 'end' | 'thinking'
  [key: string]: any
}

// 用户信息
export interface UserInfo {
  id: number
  username: string
  token: string
  phone?: string
  real_name?: string
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 注册请求
export interface RegisterRequest {
  username: string
  password: string
  phone?: string
  real_name?: string
}