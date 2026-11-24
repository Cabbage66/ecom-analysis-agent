<template>
  <div class="page-container chat-page">
    <!-- 对话区 -->
    <div class="content-card chat-main">
      <div ref="scrollRef" class="chat-scroll">
        <p v-if="!messages.length" class="chat-hint-empty">
          输入关于商品、订单或评价的问题，例如「洗衣液 2L 有哪些评价？」
        </p>

        <!-- 一轮对话：我的提问 + 分析过程 + 助手回答 -->
        <div v-for="m in messages" :key="m.id" class="turn">
          <div class="msg msg--user">
            <div class="msg__label">我</div>
            <div class="msg__bubble">{{ m.question }}</div>
          </div>

          <div v-if="m.steps.length" class="process">
            <div class="process__head">
              <span class="process__summary">
                <i class="process__dot" />
                {{ m.done ? '已处理' : '处理中' }} · {{ m.steps.length }} 步 ·
                {{ m.elapsed.toFixed(1) }} 秒
              </span>
              <el-button link type="primary" size="small" @click="m.collapsed = !m.collapsed">
                {{ m.collapsed ? '展开' : '收起' }}
              </el-button>
            </div>

            <div v-show="!m.collapsed" class="process__body">
              <p v-for="(step, index) in m.steps" :key="index" class="step">
                <span v-if="step.role" class="step__role" :class="step.roleClass">{{
                  step.role
                }}</span>
                <span v-if="step.node" class="step__node">{{ step.node }}</span>
                <span class="step__text">{{ step.text }}</span>
              </p>
            </div>
          </div>

          <div v-if="m.answer" class="msg msg--assistant">
            <div class="msg__label">助手</div>
            <div class="msg__bubble msg__bubble--plain">
              <p class="msg__content">{{ m.answer }}</p>
              <div v-if="m.done || m.error" class="msg__foot">
                <el-button link size="small" :icon="CopyDocument" @click="copyAnswer(m.answer)">
                  复制
                </el-button>
              </div>
            </div>
          </div>

          <el-alert
            v-if="m.error"
            class="turn__alert"
            type="error"
            :closable="false"
            show-icon
            :title="m.error"
          />

          <p v-if="m.id === activeId && sending && !m.answer" class="chat-typing">正在思考…</p>
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="content-card chat-composer">
      <el-input
        v-model="question"
        type="textarea"
        :rows="3"
        resize="none"
        maxlength="1000"
        :disabled="sending"
        placeholder="输入关于商品、订单或评价的问题..."
        @keydown="handleKeydown"
      />
      <div class="chat-actions">
        <span class="chat-tip">Enter 发送 · Shift + Enter 换行</span>
        <span class="chat-count">{{ question.length }} /1000</span>
        <div class="toolbar-spacer" />
        <el-button :disabled="sending || !question.trim()" @click="clearInput">清空</el-button>
        <el-button
          type="primary"
          :loading="sending"
          :disabled="sending || !question.trim()"
          @click="handleSend"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({ name: 'Chat' })
import { CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { chatStream } from '@/api/chat'
import { nextTick, onUnmounted, reactive, ref } from 'vue'

// 过程区里的角色配色：角色名出现在消息开头时按它上色
const ROLE_RULES = [
  { name: '查询分析 Agent', roleClass: 'step__role--query' },
  { name: '报告决策 Agent', roleClass: 'step__role--report' },
  { name: '调度', roleClass: 'step__role--route' }
]

/**
 * 把一条过程消息拆成 角色 / 节点 / 描述
 * 后端给了 role、node 就直接用，否则从消息文本里认
 */
function parseStep(message, payload = {}) {
  const text = String(message ?? '').trim()
  if (payload.role || payload.node) {
    const hit = ROLE_RULES.find((r) => r.name === payload.role)
    return {
      role: payload.role || '',
      roleClass: hit ? hit.roleClass : '',
      node: payload.node || '',
      text: payload.message ?? text
    }
  }

  const hit = ROLE_RULES.find((r) => text.startsWith(r.name))
  if (!hit) {
    // 有些步骤没有角色前缀，本身就是以节点名开头的
    const bare = text.match(/^([a-z][a-z0-9_]*)\s+([\s\S]+)$/i)
    if (bare) return { role: '', roleClass: '', node: bare[1], text: bare[2] }
    return { role: '', roleClass: '', node: '', text }
  }

  const rest = text.slice(hit.name.length).trim()
  // 节点名是 preparing_evidence 这种下划线写法，紧跟在角色名后面
  const matched = rest.match(/^([a-z][a-z0-9_]*)\s+([\s\S]*)$/i)
  return {
    role: hit.name,
    roleClass: hit.roleClass,
    node: matched ? matched[1] : '',
    text: matched ? matched[2] : rest
  }
}

// 每一轮对话一个对象，新问题追加到列表末尾，历史不会被覆盖
const messages = ref([])
const question = ref('')
const sending = ref(false)
const scrollRef = ref()

let timer = null
let startedAt = 0
let seq = 0
let activeId = 0
let activeRequest = null

const clearInput = () => {
  question.value = ''
}

const scrollToBottom = () => {
  nextTick(() => {
    const el = scrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

const stopTimer = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

const handleSend = async () => {
  if (sending.value) return
  const value = question.value.trim()
  if (!value) {
    ElMessage.warning('请先输入问题')
    return
  }

  // reactive 包一层，直接改字段才会触发视图更新
  const round = reactive({
    id: ++seq,
    question: value,
    steps: [],
    answer: '',
    error: '',
    done: false,
    elapsed: 0,
    collapsed: false
  })
  messages.value.push(round)
  activeId = round.id

  question.value = ''
  sending.value = true
  scrollToBottom()

  startedAt = Date.now()
  stopTimer()
  timer = setInterval(() => {
    round.elapsed = (Date.now() - startedAt) / 1000
  }, 100)

  activeRequest = chatStream(value, {
    onStatus: (message, payload) => {
      round.steps.push(parseStep(message, payload))
      scrollToBottom()
    },
    // token 是增量，只追加不覆盖
    onToken: (content) => {
      round.answer += content
      scrollToBottom()
    },
    onError: (message) => {
      round.error = message || '分析失败，请稍后重试'
      round.answer = ''
    },
    onDone: () => {
      round.done = true
      scrollToBottom()
    },
    onFinish: () => {
      // 无论 done、error、401、500 还是网络异常都会走到这里，
      // 统一收尾：标记结束、停止计时、解除加载态
      round.done = true
      round.elapsed = (Date.now() - startedAt) / 1000
      sending.value = false
      stopTimer()
      scrollToBottom()
    }
  })
  activeRequest.run()
}

const handleKeydown = (event) => {
  // 输入法确认候选词和 Shift + Enter 换行都不触发发送。
  if (event.isComposing || event.key !== 'Enter' || event.shiftKey) return
  event.preventDefault()
  handleSend()
}

const copyAnswer = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制回答')
  } catch {
    ElMessage.error('复制失败，请手动选择文本')
  }
}

onUnmounted(() => {
  activeRequest?.abort()
  stopTimer()
})
</script>

<style scoped>
/* 顶栏 60px + 内容区上下内边距 16px×2 */
.chat-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: calc(100vh - 92px);
}

/* —— 对话区 —— */
.chat-main {
  flex: 1;
  min-height: 0;
  display: flex;
  padding: 0;
  overflow: hidden;
}

.chat-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: var(--app-space-card);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-hint-empty {
  margin: auto;
  font-size: 13px;
  color: var(--app-text-secondary);
}

/* 一轮对话 */
.turn {
  display: flex;
  flex-direction: column;
  gap: 12px;
  /* 滚动容器是列向 flex：不锁住高度会被压扁 */
  flex-shrink: 0;
}

/* —— 消息气泡 —— */
.msg,
.process {
  flex-shrink: 0;
}

/* 过程卡片不铺满整行 */
.process {
  max-width: 70%;
}

.msg {
  display: flex;
  flex-direction: column;
  gap: 4px;
  /* 正文不铺满整行，否则一行太长不好读 */
  max-width: 70%;
}

.msg--user {
  align-self: flex-end;
  align-items: flex-end;
}

.msg--assistant {
  align-self: flex-start;
  /* 固定占 70%，不随内容长短伸缩 */
  width: 70%;
}

.msg__label {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.msg__bubble {
  padding: 10px 14px;
  border-radius: var(--app-radius-sm);
  background: #eff6ff;
  color: var(--app-text);
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
}

.msg__bubble--plain {
  padding: 0;
  background: transparent;
}

.msg__content {
  white-space: pre-wrap;
}

.msg__foot {
  margin-top: 6px;
}

.chat-typing {
  font-size: 13px;
  color: var(--app-text-secondary);
}

/* 错误提示跟着它所属的那一轮 */
.turn__alert {
  align-self: flex-start;
  max-width: 70%;
  flex-shrink: 0;
}

/* —— 分析过程 —— */
.process {
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: #f8fafc;
  overflow: hidden;
}

.process__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--app-border);
}

.process__summary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--app-text-secondary);
  font-variant-numeric: tabular-nums;
}

.process__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--app-primary);
}

.process__body {
  max-height: 260px;
  overflow-y: auto;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step {
  font-size: 13px;
  line-height: 1.6;
  color: var(--app-text);
}

.step__role {
  font-weight: 600;
  margin-right: 6px;
}

.step__role--query {
  color: var(--app-primary);
}

.step__role--report {
  color: #d97706;
}

.step__role--route {
  color: var(--app-text-secondary);
}

.step__node {
  margin-right: 6px;
  color: var(--app-text-secondary);
  font-family: Consolas, Monaco, monospace;
  font-size: 12px;
}

.step__text {
  word-break: break-word;
}

/* —— 输入区 —— */
.chat-composer {
  flex-shrink: 0;
}

.chat-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.chat-tip,
.chat-count {
  font-size: 12px;
  color: var(--app-text-secondary);
  font-variant-numeric: tabular-nums;
}
</style>
