import router from '@/router'
import { ElMessage } from 'element-plus'
import { getToken, logout } from '@/utils/auth'

// 每个事件包含 event 行和 JSON data，格式错误的事件独立丢弃。
function parseBlock(block) {
  let event = ''
  const dataLines = []
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
  }
  if (!event) return null
  try {
    const data = JSON.parse(dataLines.join('\n') || '{}')
    if (!data || typeof data !== 'object' || Array.isArray(data)) return null
    return { event, data }
  } catch {
    return null
  }
}

export function chatStream(question, handlers = {}) {
  const controller = new AbortController()
  const run = async () => {
    let reader
    try {
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`
        },
        body: JSON.stringify({ question }),
        signal: controller.signal
      })
      // fetch 不经过 Axios 拦截器，需要自行清理过期登录态。
      if (res.status === 401) {
        ElMessage.error('登录状态已失效，请重新登录')
        logout()
        router.push('/login')
        return
      }
      if (!res.ok) {
        throw new Error(`请求失败（HTTP ${res.status}）`)
      }

      reader = res.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      let terminal = false
      const dispatch = (block) => {
        // done 或 error 后不再接收后续事件。
        if (terminal) return
        const parsed = parseBlock(block)
        if (!parsed) return
        const { event, data } = parsed
        if (event === 'status') handlers.onStatus?.(data.message ?? '', data)
        else if (event === 'token') handlers.onToken?.(data.content ?? '')
        else if (event === 'done') {
          terminal = true
          handlers.onDone?.(data)
        } else if (event === 'error') {
          terminal = true
          handlers.onError?.(data.message || '对话处理失败')
        }
      }

      while (!terminal) {
        const { done, value } = await reader.read()
        if (done) break
        // 先累积再统一换行，兼容 CRLF 恰好被网络分块拆开的情况。
        buffer = (buffer + decoder.decode(value, { stream: true })).replace(/\r\n/g, '\n')
        let index
        while (!terminal && (index = buffer.indexOf('\n\n')) !== -1) {
          dispatch(buffer.slice(0, index))
          buffer = buffer.slice(index + 2)
        }
      }
      buffer += decoder.decode()
      if (!terminal && buffer.trim()) dispatch(buffer)
      // 连接关闭不等于正常完成，只有收到终止事件才能按协议结束。
      if (!terminal) handlers.onError?.('对话连接提前结束，请重试')
    } catch (err) {
      if (err?.name !== 'AbortError') {
        handlers.onError?.(err?.message || '网络异常，请检查后端服务')
      }
    } finally {
      if (reader) {
        try {
          await reader.cancel()
        } catch {
          // 连接已断开时仍需释放读取锁并执行页面收尾。
        }
        reader.releaseLock()
      }
      handlers.onFinish?.()
    }
  }
  return { run, abort: () => controller.abort() }
}
