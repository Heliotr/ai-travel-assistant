import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Message, UserInfo } from '../types'
import { agentAPI } from '../api/agent'

export const useConversationStore = defineStore('conversation', () => {
  // 状态
  const messages = ref<Message[]>([])
  const isStreaming = ref(false)
  const currentAgent = ref<string>('')
  const currentTool = ref<string>('')
  const user = ref<UserInfo | null>(null)
  const isLoggedIn = computed(() => !!user.value)

  // 生成唯一ID
  const generateId = () => crypto.randomUUID()

  // 添加消息
  const addMessage = (msg: Omit<Message, 'id' | 'timestamp'>) => {
    messages.value.push({
      ...msg,
      id: generateId(),
      timestamp: Date.now()
    })
  }

  // 更新最后一条助手消息
  const updateLastAssistantMessage = (content: string, extra?: Partial<Message>) => {
    const lastMsg = messages.value.filter(m => m.role === 'assistant').pop()
    if (lastMsg) {
      lastMsg.content = content
      Object.assign(lastMsg, extra)
    }
  }

  // 添加思考中消息
  const addThinkingMessage = () => {
    const msg: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      isThinking: true
    }
    messages.value.push(msg)
    return msg
  }

  // 移除思考中消息
  const removeThinkingMessage = () => {
    const idx = messages.value.findIndex(m => m.isThinking)
    if (idx !== -1) {
      messages.value.splice(idx, 1)
    }
  }

  // 发送消息并处理流式响应
  const sendMessage = async (content: string) => {
    if (isStreaming.value || !content.trim()) return

    // 添加用户消息
    addMessage({ role: 'user', content: content.trim() })
    isStreaming.value = true

    try {
      addThinkingMessage()
      let currentContent = ''

      for await (const event of agentAPI.streamChat(content)) {
        switch (event.type) {
          case 'agent':
            currentAgent.value = event.agent
            break

          case 'content':
            currentContent += event.content
            // 过滤掉交接细节的系统消息（包含"现在助手是"、"请回顾上述"等关键词）
            const isHandoverMessage = currentContent.includes('现在助手是') ||
                                       currentContent.includes('请回顾上述') ||
                                       currentContent.includes('代理')

            // 如果是交接消息，不创建新消息，只更新agent
            if (isHandoverMessage) {
              // 更新当前agent但不显示这个消息
              break
            }

            // 找到当前正在思考的消息并更新
            const msgIndex = messages.value.findIndex(m => m.isThinking)
            if (msgIndex !== -1) {
              messages.value[msgIndex] = {
                ...messages.value[msgIndex],
                isThinking: false,
                content: currentContent,
                agent: currentAgent.value
              }
            } else if (currentContent.trim()) {
              // 如果没有思考中的消息，但有内容，创建新消息
              addMessage({
                role: 'assistant',
                content: currentContent,
                agent: currentAgent.value
              })
            }
            break

          case 'tool':
            currentTool.value = event.tool
            // 添加工具调用消息
            addMessage({
              role: 'tool',
              content: '',
              toolName: event.tool,
              agent: currentAgent.value,
              // 添加超时处理：30秒后如果没收到结果，自动标记为失败
              toolCallId: setTimeout(() => {
                const idx = messages.value.findLastIndex(m => m.role === 'tool' && m.toolName === event.tool)
                if (idx !== -1 && !messages.value[idx].toolResult) {
                  messages.value[idx] = {
                    ...messages.value[idx],
                    content: '工具调用超时或失败',
                    toolResult: '工具调用超时或失败'
                  }
                }
              }, 30000)
            })
            break

          case 'tool_result':
            // 找到最后一个工具消息并更新其内容，移除转圈状态
            const lastToolMsgIndex = messages.value.findLastIndex(m => m.role === 'tool' && m.toolName === event.tool)
            if (lastToolMsgIndex !== -1) {
              // 清除超时定时器
              const msg = messages.value[lastToolMsgIndex]
              if (msg.toolCallId) {
                clearTimeout(msg.toolCallId)
              }
              messages.value[lastToolMsgIndex] = {
                ...messages.value[lastToolMsgIndex],
                content: event.content,
                toolResult: event.content
              }
            } else {
              // 如果没找到匹配的，创建新消息
              addMessage({
                role: 'tool',
                content: event.content,
                toolName: event.tool,
                agent: currentAgent.value,
                toolResult: event.content
              })
            }
            break

          case 'thinking':
            // 找到当前正在思考的消息并更新
            const thinkingMsgIndex = messages.value.findIndex(m => m.isThinking)
            if (thinkingMsgIndex !== -1) {
              messages.value[thinkingMsgIndex].content = event.content
            }
            break

          case 'error':
            addMessage({
              role: 'assistant',
              content: `错误: ${event.message}`,
              isError: true
            })
            break

          case 'confirm':
            // 找到当前正在思考的消息
            const confirmMsgIndex = messages.value.findIndex(m => m.isThinking)
            if (confirmMsgIndex !== -1) {
              messages.value[confirmMsgIndex].content = event.content
              messages.value[confirmMsgIndex].isThinking = false
            }
            break

          case 'end':
            isStreaming.value = false
            break
        }
      }
    } catch (error: any) {
      addMessage({
        role: 'assistant',
        content: `请求失败: ${error.message}`,
        isError: true
      })
    } finally {
      isStreaming.value = false
    }
  }

  // 停止生成
  const stopGeneration = () => {
    isStreaming.value = false
    removeThinkingMessage()
  }

  // 登录
  const login = async (username: string, password: string) => {
    const userInfo = await agentAPI.login({ username, password })
    user.value = userInfo
    agentAPI.setToken(userInfo.token)
    localStorage.setItem('ctrip_token', userInfo.token)
    localStorage.setItem('ctrip_user', JSON.stringify(userInfo))
  }

  // 注册
  const register = async (data: { username: string; password: string; phone?: string; real_name?: string }) => {
    return agentAPI.register(data)
  }

  // 登出
  const logout = () => {
    user.value = null
    agentAPI.setToken(null)
    localStorage.removeItem('ctrip_token')
    localStorage.removeItem('ctrip_user')
  }

  // 初始化（检查本地存储）
  const init = () => {
    const token = localStorage.getItem('ctrip_token')
    const userStr = localStorage.getItem('ctrip_user')
    if (token && userStr) {
      try {
        user.value = JSON.parse(userStr)
        agentAPI.setToken(token)
      } catch (e) {
        logout()
      }
    }
  }

  // 清空对话
  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages,
    isStreaming,
    currentAgent,
    currentTool,
    user,
    isLoggedIn,
    addMessage,
    sendMessage,
    stopGeneration,
    login,
    register,
    logout,
    init,
    clearMessages
  }
})