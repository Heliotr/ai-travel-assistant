<template>
  <div :class="['chat-message', `role-${message.role}`, { 'is-thinking': message.isThinking, 'is-error': message.isError }]">
    <!-- 用户消息 -->
    <template v-if="message.role === 'user'">
      <div class="message-avatar user-avatar">
        <n-icon :size="20"><UserIcon /></n-icon>
      </div>
      <div class="message-content">
        <div class="message-bubble">{{ message.content }}</div>
        <div class="message-time">{{ formatTime(message.timestamp) }}</div>
      </div>
    </template>

    <!-- AI/助手消息 -->
    <template v-else-if="message.role === 'assistant'">
      <div class="message-avatar ai-avatar">
        <n-icon :size="20"><BotIcon /></n-icon>
      </div>
      <div class="message-content">
        <div class="message-agent" v-if="message.agent">{{ message.agent }}</div>
        <div class="message-bubble" v-if="!message.isThinking" v-html="renderContent(message.content)"></div>
        <div class="thinking-indicator" v-else>
          <n-spin size="small" />
          <span>AI 思考中...</span>
        </div>
        <div class="message-time">{{ formatTime(message.timestamp) }}</div>
      </div>
    </template>

    <!-- 工具消息 -->
    <template v-else-if="message.role === 'tool'">
      <div class="tool-card">
        <div class="tool-header">
          <n-icon :size="14"><ToolIcon /></n-icon>
          <span class="tool-name">{{ message.toolName }}</span>
          <span class="tool-agent" v-if="message.agent">· {{ message.agent }}</span>
        </div>
        <div class="tool-content" v-if="message.toolResult">
          <pre>{{ message.toolResult }}</pre>
        </div>
        <div class="tool-calling" v-else>
          <n-spin size="small" />
          <span>调用工具中...</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { NIcon, NSpin } from 'naive-ui'
import type { Message } from '../../types'

const props = defineProps<{
  message: Message
}>()

// 图标组件
const UserIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' })
])

const BotIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2zM7.5 13A2.5 2.5 0 005 15.5 2.5 2.5 0 007.5 18a2.5 2.5 0 002.5-2.5A2.5 2.5 0 007.5 13zm9 0a2.5 2.5 0 00-2.5 2.5 2.5 2.5 0 002.5 2.5 2.5 2.5 0 002.5-2.5 2.5 2.5 0 00-2.5-2.5z' })
])

const ToolIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z' })
])

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const renderContent = (content: string) => {
  // 简单渲染，支持换行
  return content.replace(/\n/g, '<br>')
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  animation: fadeIn 0.3s ease;
  max-width: 85%;
}

/* 用户消息靠右 */
.role-user {
  flex-direction: row-reverse;
  margin-left: auto;
}

/* AI消息靠左 */
.role-assistant {
  margin-right: auto;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar {
  background: linear-gradient(135deg, #2080f0, #1060d0);
  color: white;
}

.ai-avatar {
  background: linear-gradient(135deg, #18a058, #106040);
  color: white;
}

.message-content {
  flex: 1;
  min-width: 0;
}

/* 用户消息内容右对齐 */
.role-user .message-content {
  text-align: right;
}

.message-agent {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.message-bubble {
  background: #2a2a2a;
  border-radius: 12px;
  padding: 12px 16px;
  line-height: 1.6;
  word-break: break-word;
  display: inline-block;
  max-width: 100%;
}

.role-user .message-bubble {
  background: #2080f0;
  color: white;
}

.is-error .message-bubble {
  background: #5c2d2d;
  color: #f0a0a0;
}

.message-time {
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #999;
  font-size: 13px;
}

/* 工具卡片 */
.tool-card {
  background: #1e1e1e;
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
  margin-left: 48px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #252525;
  border-bottom: 1px solid #333;
  font-size: 13px;
  color: #2080f0;
}

.tool-name {
  font-weight: 500;
}

.tool-agent {
  color: #888;
}

.tool-content {
  padding: 12px;
  max-height: 200px;
  overflow: auto;
}

.tool-content pre {
  margin: 0;
  font-size: 12px;
  font-family: 'Consolas', monospace;
  color: #aaa;
  white-space: pre-wrap;
  word-break: break-all;
}

.tool-calling {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  color: #888;
  font-size: 13px;
}
</style>