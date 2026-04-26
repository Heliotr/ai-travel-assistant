<template>
  <div class="chat-input-container">
    <div class="input-wrapper">
      <n-input
        v-model:value="inputText"
        type="textarea"
        placeholder="请输入您的问题..."
        :autosize="{ minRows: 1, maxRows: 6 }"
        @keydown.enter.exact.prevent="handleSend"
        @keydown.enter.shift.prevent="handleNewLine"
      />
      <div class="input-actions">
        <n-button
          v-if="isStreaming"
          type="error"
          size="small"
          @click="handleStop"
        >
          <template #icon>
            <n-icon><StopIcon /></n-icon>
          </template>
          停止
        </n-button>
        <n-button
          type="primary"
          :disabled="!inputText.trim() || isStreaming"
          @click="handleSend"
        >
          <template #icon>
            <n-icon class="send-icon"><SendIcon /></n-icon>
          </template>
          <span class="send-text">发送</span>
        </n-button>
      </div>
    </div>
    <div class="input-hint">
      <span>按 Enter 发送，Shift + Enter 换行</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, h } from 'vue'
import { NInput, NButton, NIcon } from 'naive-ui'

const props = defineProps<{
  isStreaming: boolean
}>()

const emit = defineEmits<{
  (e: 'send', text: string): void
  (e: 'stop'): void
}>()

const inputText = ref('')

const handleSend = () => {
  if (!inputText.value.trim() || props.isStreaming) return
  emit('send', inputText.value)
  inputText.value = ''
}

const handleStop = () => {
  emit('stop')
}

const handleNewLine = (e: KeyboardEvent) => {
  const target = e.target as HTMLTextAreaElement
  const start = target.selectionStart
  const end = target.selectionEnd
  const value = inputText.value
  inputText.value = value.substring(0, start) + '\n' + value.substring(end)
  // 下次渲染后设置光标位置
  setTimeout(() => {
    target.selectionStart = target.selectionEnd = start + 1
  }, 0)
}

// 图标
const SendIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M2.01 21L23 12 2.01 3 2 10l15 2-15 2z' })
])

const StopIcon = () => h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('rect', { x: '6', y: '6', width: '12', height: '12' })
])
</script>

<style scoped>
.chat-input-container {
  padding: 16px 20px;
  background: linear-gradient(180deg, rgba(35, 35, 55, 0.9) 0%, rgba(25, 25, 45, 0.95) 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.input-wrapper {
  display: flex;
  gap: 14px;
  align-items: flex-end;
}

.input-wrapper :deep(.n-input) {
  --n-border-radius: 14px;
  --n-color: rgba(45, 45, 65, 0.9);
  --n-color-focus: rgba(50, 50, 75, 0.95);
  --n-border: 1px solid rgba(100, 120, 180, 0.3);
  --n-border-focus: 1px solid #60a5fa;
  --n-box-shadow-focus: 0 0 0 3px rgba(96, 165, 250, 0.2);
  --n-text-color: #f0f0f0;
  --n-placeholder-color: rgba(160, 170, 190, 0.6);
  background: linear-gradient(135deg, rgba(40, 40, 60, 0.8) 0%, rgba(35, 35, 55, 0.9) 100%);
  transition: all 0.3s ease;
}

.input-wrapper :deep(.n-input:hover) {
  --n-border: 1px solid rgba(100, 140, 200, 0.5);
  background: linear-gradient(135deg, rgba(50, 50, 70, 0.9) 0%, rgba(40, 40, 60, 0.95) 100%);
}

.input-wrapper :deep(.n-input__textarea-el) {
  font-size: 14px;
  line-height: 1.6;
  color: #f5f5f5;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-actions :deep(.n-button--primary-type) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.input-actions :deep(.n-button--primary-type:hover) {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.input-actions :deep(.n-button--primary-type:active) {
  transform: translateY(0);
}

.input-actions :deep(.n-button--primary-type[disabled]) {
  background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
  box-shadow: none;
  opacity: 0.6;
}

.input-hint {
  margin-top: 10px;
  font-size: 12px;
  color: rgba(160, 170, 190, 0.5);
  text-align: center;
}

.send-icon {
  color: #e0f2fe;
  filter: drop-shadow(0 0 2px rgba(96, 165, 250, 0.8));
}

.send-text {
  background: linear-gradient(135deg, #e0f2fe 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
}
</style>