<template>
  <div class="page-container">
    <div class="content-card">
      <div class="toolbar-row">
        <el-input
          class="search-input"
          placeholder="请输入订单号、买家或商品名查询"
          aria-label="请输入订单号、买家或商品名查询"
          v-model="params.keywords"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" :icon="Search" :loading="loading" @click="handleSearch"
          >查询</el-button
        >
      </div>

      <el-table
        :header-cell-style="tableHeaderStyle"
        :data="tableData"
        row-key="id"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="order_no" label="订单号" min-width="180" show-overflow-tooltip />
        <el-table-column prop="product_name" label="商品名" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.product_name || '—' }}</template>
        </el-table-column>
        <el-table-column prop="buyer_name" label="买家" min-width="120" show-overflow-tooltip />
        <el-table-column prop="quantity" label="数量" width="90" align="right" />
        <el-table-column prop="amount" label="实付" width="120" align="right">
          <template #default="{ row }">￥{{ Number(row.amount).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="light"
              round
              :type="row.status === 'completed' ? 'success' : 'info'"
            >
              {{ statusLabels[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="下单时间" width="180">
          <template #default="{ row }"
            ><span class="time-text">{{ row.create_time || '—' }}</span></template
          >
        </el-table-column>
        <template #empty>
          <el-empty
            :description="loadFailed ? '加载失败，请重新查询' : '暂无订单数据'"
            :image-size="80"
          />
        </template>
      </el-table>

      <div class="table-footer">
        <el-pagination
          v-model:current-page="params.page"
          v-model:page-size="params.pageSize"
          :total="total"
          :disabled="loading"
          background
          small
          layout="total, prev, pager, next"
          @current-change="load"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({ name: 'OrderList' })
import { Search } from '@element-plus/icons-vue'
import { getOrderPageList } from '@/api/ecommerce'
import { ref, reactive, onMounted } from 'vue'

const tableHeaderStyle = {
  backgroundColor: '#f8fafc',
  color: '#475569',
  fontWeight: 600
}

const statusLabels = { completed: '已完成' }

const params = reactive({
  page: 1,
  pageSize: 10,
  keywords: ''
})
const loading = ref(false)
const loadFailed = ref(false)
const tableData = ref([])
const total = ref(0)
let requestId = 0

const load = async () => {
  const currentRequest = ++requestId
  loading.value = true
  loadFailed.value = false
  try {
    const res = await getOrderPageList({
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords.trim()
    })
    if (currentRequest !== requestId) return
    if (res.code === 200) {
      tableData.value = res.data?.list ?? []
      total.value = res.data?.total ?? 0
    } else {
      tableData.value = []
      total.value = 0
      loadFailed.value = true
    }
  } catch {
    if (currentRequest !== requestId) return
    tableData.value = []
    total.value = 0
    loadFailed.value = true
  } finally {
    if (currentRequest === requestId) loading.value = false
  }
}

const handleSearch = () => {
  params.page = 1
  load()
}

onMounted(load)
</script>
