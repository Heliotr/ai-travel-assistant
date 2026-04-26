import type { SSEEvent, LoginRequest, RegisterRequest, UserInfo } from '../types'

const API_BASE = '/api'

class AgentAPI {
  private token: string | null = null

  setToken(token: string | null) {
    this.token = token
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = { 'Content-Type': 'application/json' }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }
    return headers
  }

  // 登录
  async login(data: LoginRequest): Promise<UserInfo> {
    const res = await fetch(`${API_BASE}/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || '登录失败')
    }
    return res.json()
  }

  // 注册
  async register(data: RegisterRequest): Promise<any> {
    const res = await fetch(`${API_BASE}/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || '注册失败')
    }
    return res.json()
  }

  // 流式调用新工作流
  async *streamChat(userInput: string, config?: any): AsyncGenerator<SSEEvent> {
    const response = await fetch(`${API_BASE}/new_graph/stream/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        user_input: userInput,
        config: config || { configurable: { passenger_id: '3442 587242', thread_id: crypto.randomUUID() } }
      })
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || '请求失败')
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('无法读取响应')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            yield data as SSEEvent
          } catch (e) {
            console.error('解析 SSE 数据失败:', e)
          }
        }
      }
    }
  }

  // 确认操作（用于敏感操作）
  async confirmAction(confirm: boolean): Promise<any> {
    const response = await fetch(`${API_BASE}/new_graph/stream/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        user_input: confirm ? 'y' : 'n',
        config: {}
      })
    })
    return response.json()
  }
}

export const agentAPI = new AgentAPI()