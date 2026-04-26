<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <div class="app-container">
          <!-- 顶部导航 -->
          <header class="app-header">
            <div class="header-left">
              <div class="logo">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%232080f0'/%3E%3Cpath d='M30 50 L45 65 L70 35' stroke='white' stroke-width='8' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E" alt="logo" />
                <span>智能旅行客服</span>
              </div>
            </div>
            <div class="header-right">
              <n-button size="small" quaternary @click="showTestCases = true">
                <template #icon>
                  <n-icon><DocumentIcon /></n-icon>
                </template>
                测试用例说明
              </n-button>
              <template v-if="conversationStore.isLoggedIn">
                <n-dropdown :options="userMenuOptions" @select="handleUserMenu">
                  <n-button text>
                    <n-avatar round size="small">{{ conversationStore.user?.username?.charAt(0) }}</n-avatar>
                    <span class="username">{{ conversationStore.user?.username }}</span>
                  </n-button>
                </n-dropdown>
              </template>
              <template v-else>
                <n-button size="small" @click="showLogin = true">登录</n-button>
                <n-button size="small" type="primary" @click="showRegister = true">注册</n-button>
              </template>
            </div>
          </header>

          <!-- 主内容区 -->
          <main class="app-main">
            <!-- 左侧对话区 (65%) -->
            <div class="chat-panel">
              <div class="chat-messages" ref="messagesContainer">
                <ChatMessage
                  v-for="msg in conversationStore.messages"
                  :key="msg.id"
                  :message="msg"
                />
                <!-- 欢迎语 -->
                <div v-if="conversationStore.messages.length === 0" class="welcome">
                  <template v-if="conversationStore.isLoggedIn">
                    <h2>欢迎回来，{{ conversationStore.user?.username }}！</h2>
                    <p>我可以帮您：</p>
                    <ul>
                      <li>🔍 查询航班信息、预订和改签</li>
                      <li>🏨 搜索酒店、预订和修改</li>
                      <li>🚗 租车服务</li>
                      <li>🎯 景点推荐和预订</li>
                    </ul>
                    <p class="hint">请告诉我您需要什么帮助？</p>
                  </template>
                  <template v-else>
                    <h2>欢迎使用智能旅行客服助手</h2>
                    <p>我可以帮您：</p>
                    <ul>
                      <li>🔍 查询航班信息、预订和改签</li>
                      <li>🏨 搜索酒店、预订和修改</li>
                      <li>🚗 租车服务</li>
                      <li>🎯 景点推荐和预订</li>
                    </ul>
                    <p class="hint">请先登录后开始使用</p>
                  </template>
                </div>
              </div>
              <ChatInput
                :is-streaming="conversationStore.isStreaming"
                @send="handleSend"
                @stop="handleStop"
              />
            </div>

            <!-- 右侧信息面板 (35%) -->
            <div class="info-panel">
              <!-- 开发者消息 -->
              <div class="info-card developer-card">
                <div class="card-header">
                  <n-icon :size="18"><MessageIcon /></n-icon>
                  <span>开发者消息</span>
                </div>
                <div class="card-content">
                  <p >基于 LangGraph 多 Agent 架构的智能旅行客服系统</p>
                  <p>版本: v1.0</p>
                  <p>1.当前界面主要用于演示基于 LangGraph 中 Workflow 的拆分与工具调用的效果。</p>
                  <p>2.构建工作流与自定义工具可直接迁移到其他项目中使用。</p>
                  <p class="highlight">2.0 版本将引入 Supervisor 监督者，对所有子 Agent 进行业务调度，管理维护更便捷。</p>
                </div>
              </div>

              <!-- 快捷测试 -->
              <div class="info-card quick-test-card">
                <div class="card-header">
                  <n-icon :size="18"><FlashIcon /></n-icon>
                  <span>快捷测试</span>
                </div>
                <div class="card-content">
                  <div class="test-buttons">
                    <n-button size="small" quaternary @click="quickTest('查询从上海到北京的航班')">
                      航班查询
                    </n-button>
                    <n-button size="small" quaternary @click="quickTest('帮我预订上海外滩附近的三星级酒店')">
                      酒店预订
                    </n-button>
                    <n-button size="small" quaternary @click="quickTest('我要租一辆商务车')">
                      租车服务
                    </n-button>
                    <n-button size="small" quaternary @click="quickTest('推荐杭州西湖附近的景点')">
                      景点推荐
                    </n-button>
                  </div>
                </div>
              </div>

              <!-- 对话历史 -->
              <div class="info-card history-card">
                <div class="card-header">
                  <n-icon :size="18"><HistoryIcon /></n-icon>
                  <span>对话历史</span>
                  <n-button v-if="conversationStore.messages.length > 0" text size="tiny" @click="conversationStore.clearMessages()" style="margin-left: auto;">
                    清空
                  </n-button>
                </div>
                <div class="card-content history-list">
                  <template v-if="conversationStore.messages.length > 0">
                    <div
                      v-for="(msg, index) in conversationStore.messages"
                      :key="msg.id"
                      class="history-item"
                      :class="`role-${msg.role}`"
                      @click="scrollToMessage(index)"
                    >
                      <span class="history-role">{{ getRoleLabel(msg.role) }}</span>
                      <span class="history-text">{{ truncate(msg.content, 30) }}</span>
                    </div>
                  </template>
                  <div v-else class="empty-history">
                    暂无对话记录
                  </div>
                </div>
              </div>
            </div>
          </main>

          <!-- 登录弹窗 -->
          <n-modal v-model:show="showLogin" preset="card" title="用户登录" style="width: 400px">
            <n-form ref="loginFormRef" :model="loginForm" :rules="loginRules">
              <n-form-item label="用户名" path="username">
                <n-input v-model:value="loginForm.username" placeholder="请输入用户名" />
              </n-form-item>
              <n-form-item label="密码" path="password">
                <n-input v-model:value="loginForm.password" type="password" placeholder="请输入密码" />
              </n-form-item>
            </n-form>
            <template #footer>
              <n-button @click="showLogin = false">取消</n-button>
              <n-button type="primary" @click="handleLogin" :loading="logging">登录</n-button>
            </template>
          </n-modal>

          <!-- 注册弹窗 -->
          <n-modal v-model:show="showRegister" preset="card" title="用户注册" style="width: 400px">
            <n-form ref="registerFormRef" :model="registerForm" :rules="registerRules">
              <n-form-item label="用户名" path="username">
                <n-input v-model:value="registerForm.username" placeholder="请输入用户名" />
              </n-form-item>
              <n-form-item label="密码" path="password">
                <n-input v-model:value="registerForm.password" type="password" placeholder="请输入密码" />
              </n-form-item>
              <n-form-item label="手机号" path="phone">
                <n-input v-model:value="registerForm.phone" placeholder="请输入手机号（可选）" />
              </n-form-item>
              <n-form-item label="真实姓名" path="real_name">
                <n-input v-model:value="registerForm.real_name" placeholder="请输入真实姓名（可选）" />
              </n-form-item>
            </n-form>
            <template #footer>
              <n-button @click="showRegister = false">取消</n-button>
              <n-button type="primary" @click="handleRegister" :loading="registering">注册</n-button>
            </template>
          </n-modal>

          <!-- 测试用例说明弹窗 -->
          <n-modal v-model:show="showTestCases" preset="card" title="项目与测试说明" style="width: 700px; max-height: 80vh;">
            <div class="test-cases-content">
              <n-tabs type="line" animated>
                <n-tab-pane name="intro" tab="📖 项目描述">
                  <div class="test-case">
                    <h4>系统架构</h4>
                    <p>基于 LangGraph 多 Agent 架构的智能旅行客服系统，支持航班、酒店、租车、景点等业务的智能问答与预订。</p>
                  </div>
                  <div class="test-case">
                    <h4>核心功能</h4>
                    <ul class="feature-list">
                      <li>🤖 多 Agent 协作：航班 Agent、酒店 Agent、租车 Agent、景点 Agent</li>
                      <li>🔧 自定义工具：工作流与工具可直接迁移到其他项目</li>
                      <li>💬 流式响应：实时展示 AI 生成内容</li>
                      <li>🔐 用户管理：支持登录注册、会话历史</li>
                    </ul>
                  </div>
                  <div class="test-case">
                    <h4>版本信息</h4>
                    <p>v1.0 - 当前版本演示 LangGraph Workflow 的定义与拆分</p>
                    <p>v2.0（规划中）- 引入 Supervisor 监督者，统一调度所有子 Agent</p>
                  </div>
                </n-tab-pane>
                <n-tab-pane name="api" tab="🔌 API 接口规范">
                  <div class="test-case">
                    <h4>基础配置</h4>
                    <p>Base URL: <code>/api</code></p>
                    <p>Content-Type: <code>application/json</code></p>
                  </div>
                  <div class="test-case">
                    <h4>用户接口</h4>
                    <div class="api-item">
                      <span class="method get">GET</span>
                      <span class="path">/api/users/profile</span>
                      <span class="desc">获取当前用户信息</span>
                    </div>
                    <div class="api-item">
                      <span class="method post">POST</span>
                      <span class="path">/api/users/register</span>
                      <span class="desc">用户注册</span>
                    </div>
                    <div class="api-item">
                      <span class="method post">POST</span>
                      <span class="path">/api/users/login</span>
                      <span class="desc">用户登录</span>
                    </div>
                  </div>
                  <div class="test-case">
                    <h4>对话接口</h4>
                    <div class="api-item">
                      <span class="method post">POST</span>
                      <span class="path">/api/chat/send</span>
                      <span class="desc">发送消息（非流式）</span>
                    </div>
                    <div class="api-item">
                      <span class="method post">POST</span>
                      <span class="path">/api/chat/stream</span>
                      <span class="desc">流式对话（SSE）</span>
                    </div>
                    <div class="api-item">
                      <span class="method get">GET</span>
                      <span class="path">/api/chat/history</span>
                      <span class="desc">获取对话历史</span>
                    </div>
                  </div>
                  <div class="test-case">
                    <h4>旅行服务接口</h4>
                    <div class="api-item">
                      <span class="method get">GET</span>
                      <span class="path">/api/flight/search</span>
                      <span class="desc">航班搜索</span>
                    </div>
                    <div class="api-item">
                      <span class="method get">GET</span>
                      <span class="path">/api/hotel/search</span>
                      <span class="desc">酒店搜索</span>
                    </div>
                    <div class="api-item">
                      <span class="method get">GET</span>
                      <span class="path">/api/car/rental</span>
                      <span class="desc">租车服务查询</span>
                    </div>
                    <div class="api-item">
                      <span class="method get">GET</span>
                      <span class="path">/api/attraction/recommend</span>
                      <span class="desc">景点推荐</span>
                    </div>
                  </div>
                </n-tab-pane>
                <n-tab-pane name="flight" tab="✈️ 航班查询">
                  <div class="test-case">
                    <h4>单程航班查询</h4>
                    <p>"查询明天上海到北京的航班"</p>
                  </div>
                  <div class="test-case">
                    <h4>往返航班查询</h4>
                    <p>"帮我查一下3月25日北京到上海，3月28日返回的航班"</p>
                  </div>
                  <div class="test-case">
                    <h4>航班预订</h4>
                    <p>"预订明天上午上海到北京的航班，要求国航"</p>
                  </div>
                </n-tab-pane>
                <n-tab-pane name="hotel" tab="🏨 酒店预订">
                  <div class="test-case">
                    <h4>酒店搜索</h4>
                    <p>"帮我找一下上海外滩附近的三星级酒店"</p>
                  </div>
                  <div class="test-case">
                    <h4>酒店详情查询</h4>
                    <p>"查看上海外滩酒店的详情和价格"</p>
                  </div>
                  <div class="test-case">
                    <h4>酒店预订</h4>
                    <p>"预订上海外滩酒店，3月25日入住，3月27日退房"</p>
                  </div>
                </n-tab-pane>
                <n-tab-pane name="car" tab="🚗 租车服务">
                  <div class="test-case">
                    <h4>租车查询</h4>
                    <p>"上海有哪些租车服务？"</p>
                  </div>
                  <div class="test-case">
                    <h4>租车预订</h4>
                    <p>"我要租一辆商务车，3月25日开始租3天"</p>
                  </div>
                </n-tab-pane>
                <n-tab-pane name="attraction" tab="🎯 景点推荐">
                  <div class="test-case">
                    <h4>景点推荐</h4>
                    <p>"推荐杭州西湖附近的景点"</p>
                  </div>
                  <div class="test-case">
                    <h4>景点预订</h4>
                    <p>"帮我预订灵隐寺的门票，3月26日，2张成人票"</p>
                  </div>
                </n-tab-pane>
              </n-tabs>
            </div>
          </n-modal>
        </div>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, onMounted, h, computed } from 'vue'
import { darkTheme, NConfigProvider, NButton, NIcon, NModal, NForm, NFormItem, NInput, NDropdown, NAvatar, NDialogProvider, NMessageProvider, NTabs, NTabPane, createDiscreteApi } from 'naive-ui'
import { useConversationStore } from './stores/conversation'
import ChatMessage from './components/Chat/ChatMessage.vue'
import ChatInput from './components/Chat/ChatInput.vue'

const conversationStore = useConversationStore()

// 消息提示 API
const { message } = createDiscreteApi(['message'], {
  configProviderProps: { theme: darkTheme }
})

// 主题配置
const themeOverrides = {
  common: {
    primaryColor: '#2080f0',
    primaryColorHover: '#4098fc',
    primaryColorPressed: '#1060d0',
    bodyColor: '#0a0a0f',
    cardColor: 'rgba(30, 30, 40, 0.8)',
    modalColor: 'rgba(20, 20, 30, 0.95)',
    popoverColor: 'rgba(30, 30, 40, 0.9)',
    tableColor: 'rgba(30, 30, 40, 0.8)',
    inputColor: 'rgba(40, 40, 55, 0.8)',
    actionColor: 'rgba(35, 35, 50, 0.8)'
  }
}

// 状态
const showLogin = ref(false)
const showRegister = ref(false)
const showTestCases = ref(false)
const logging = ref(false)
const registering = ref(false)
const messagesContainer = ref<HTMLElement>()

// 表单
const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', phone: '', real_name: '' })

// 表单验证规则
const loginRules = {
  username: { required: true, message: '请输入用户名' },
  password: { required: true, message: '请输入密码' }
}

const registerRules = {
  username: { required: true, message: '请输入用户名' },
  password: { required: true, message: '请输入密码' }
}

// 用户菜单
const userMenuOptions = [
  { label: '清空对话', key: 'clear' },
  { type: 'divider', key: 'd1' },
  { label: '退出登录', key: 'logout' }
]

const handleUserMenu = (key: string) => {
  switch (key) {
    case 'logout':
      conversationStore.logout()
      break
    case 'clear':
      conversationStore.clearMessages()
      break
  }
}

// 处理登录
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) return
  logging.value = true
  try {
    await conversationStore.login(loginForm.value.username, loginForm.value.password)
    showLogin.value = false
    loginForm.value = { username: '', password: '' }
  } catch (e: any) {
    message.error(e.message || '登录失败')
  } finally {
    logging.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) return
  registering.value = true
  try {
    await conversationStore.register(registerForm.value)
    message.success('注册成功，请登录')
    showRegister.value = false
    registerForm.value = { username: '', password: '', phone: '', real_name: '' }
  } catch (e: any) {
    message.error(e.message || '注册失败')
  } finally {
    registering.value = false
  }
}

// 发送消息
const handleSend = async (text: string) => {
  try {
    const res = await fetch('/api/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_input: text,
        user_id: conversationStore.user?.id?.toString() || 'default_user'
      })
    })
    const result = await res.json()
    if (result.assistant) {
      conversationStore.addMessage({
        role: 'assistant',
        content: result.assistant,
        agent: 'deep-agent'
      })
    }
  } catch (e: any) {
    message.error(e.message || '请求失败')
  }

  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 100)
}

// 停止生成
const handleStop = () => {
  conversationStore.stopGeneration()
}

// 快捷测试
const quickTest = (text: string) => {
  handleSend(text)
}

// 滚动到指定消息
const scrollToMessage = (index: number) => {
  if (messagesContainer.value) {
    const msgElements = messagesContainer.value.querySelectorAll('.chat-message')
    if (msgElements[index]) {
      msgElements[index].scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
}

// 获取角色标签
const getRoleLabel = (role: string) => {
  switch (role) {
    case 'user': return '你'
    case 'assistant': return 'AI'
    case 'tool': return '工具'
    default: return role
  }
}

// 截断文本
const truncate = (text: string, length: number) => {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

// 图标组件
const MessageIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z' })
])

const DocumentIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z' })
])

// 初始化
onMounted(() => {
  conversationStore.init()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body {
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f0f1a 100%);
  color: #e0e0e0;
  min-height: 100vh;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(10, 10, 15, 0.95) 0%, rgba(26, 26, 46, 0.9) 50%, rgba(15, 15, 26, 0.95) 100%);
}

/* 顶部导航 */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  background: rgba(20, 20, 35, 0.85);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  flex-shrink: 0;
}

.header-left .logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
}

.header-left .logo img {
  width: 32px;
  height: 32px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right .username {
  margin-left: 8px;
  font-size: 14px;
}

/* 主内容区 */
.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 16px;
  gap: 16px;
}

/* 左侧对话区 */
.chat-panel {
  flex: 0 0 65%;
  display: flex;
  flex-direction: column;
  background: rgba(25, 25, 40, 0.7);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome {
  max-width: 500px;
  margin: 60px auto;
  padding: 40px;
  background: rgba(30, 30, 50, 0.6);
  border-radius: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.welcome h2 {
  margin-bottom: 20px;
  font-size: 26px;
  background: linear-gradient(135deg, #60a5fa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome p {
  color: #9ca3af;
  margin-bottom: 14px;
}

.welcome ul {
  text-align: left;
  padding-left: 48px;
  margin: 24px 0;
}

.welcome li {
  margin-bottom: 10px;
  color: #d1d5db;
}

.welcome .hint {
  margin-top: 28px;
  color: #60a5fa;
  font-size: 14px;
}

/* 右侧信息面板 */
.info-panel {
  flex: 0 0 35%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.info-card {
  background: rgba(25, 25, 40, 0.7);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  background: rgba(35, 35, 55, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 14px;
  font-weight: 500;
  color: #e5e7eb;
}

.card-content {
  padding: 16px;
}

/* 开发者消息卡片 */
.developer-card {
  flex-shrink: 0;
}

.developer-card .card-content p {
  color: #9ca3af;
  font-size: 13px;
  line-height: 1.6;
}

.developer-card .version {
  margin-top: 12px;
  color: #6b7280;
  font-size: 12px;
}

.developer-card .highlight {
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
  color: #4ade80;
  font-size: 12px;
  line-height: 1.5;
}

/* 快捷测试卡片 */
.quick-test-card {
  flex-shrink: 0;
}

.test-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.test-buttons .n-button {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  transition: all 0.2s;
}

.test-buttons .n-button:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-1px);
}

/* 对话历史卡片 */
.history-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.history-card .card-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.history-role {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  flex-shrink: 0;
}

.history-item.role-user .history-role {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.history-item.role-tool .history-role {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.history-text {
  font-size: 12px;
  color: #9ca3af;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-history {
  text-align: center;
  color: #6b7280;
  font-size: 13px;
  padding: 24px;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* 测试用例说明弹窗 */
.test-cases-content {
  padding: 8px 0;
}

.test-cases-content .n-tab-pane {
  padding: 16px 0;
}

.test-case {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: rgba(30, 30, 45, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.test-case h4 {
  color: #60a5fa;
  font-size: 14px;
  margin-bottom: 8px;
  font-weight: 500;
}

.test-case p {
  color: #9ca3af;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
}

.test-case ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.test-case li {
  color: #9ca3af;
  font-size: 13px;
  line-height: 1.8;
}

.test-case code {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.api-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.api-item:last-child {
  border-bottom: none;
}

.api-item .method {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  min-width: 50px;
  text-align: center;
}

.api-item .method.get {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.api-item .method.post {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.api-item .path {
  color: #e5e7eb;
  font-size: 13px;
  font-family: monospace;
}

.api-item .desc {
  color: #6b7280;
  font-size: 12px;
  margin-left: auto;
}

/* 响应式 */
@media (max-width: 1024px) {
  .app-main {
    flex-direction: column;
  }

  .chat-panel,
  .info-panel {
    flex: none;
    width: 100% !important;
  }

  .chat-panel {
    height: 60vh;
  }

  .info-panel {
    height: auto;
    max-height: 35vh;
  }
}
</style>