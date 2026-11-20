<template>
  <div class="page-container">
    <div class="content-card">
      <div class="toolbar-row">
        <el-input
          class="search-input"
          placeholder="请输入商品名称或类目查询"
          aria-label="请输入商品名称或类目查询"
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
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="category" label="类目" min-width="100" />
        <el-table-column prop="price" label="售价" width="110" align="right">
          <template #default="{ row }">￥{{ Number(row.price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="90" align="right" />
        <el-table-column prop="shelf_status" label="上下架" width="110">
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="light"
              round
              :type="row.shelf_status === 'on_sale' ? 'success' : 'info'"
            >
              {{ shelfStatusLabels[row.shelf_status] || row.shelf_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="review_status" label="复核状态" min-width="130">
          <template #default="{ row }">
            <el-tag
              size="small"
              effect="light"
              round
              :type="row.review_status === 'pending_review' ? 'warning' : 'info'"
            >
              {{ reviewStatusLabels[row.review_status] || row.review_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }"
            ><span class="time-text">{{ row.create_time || '—' }}</span></template
          >
        </el-table-column>
        <template #empty>
          <el-empty
            :description="loadFailed ? '加载失败，请重新查询' : '暂无商品数据'"
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
defineOptions({ name: 'ProductList' })
import { Search } from '@element-plus/icons-vue'
import { getProductPageList } from '@/api/ecommerce'
import { ref, reactive, onMounted } from 'vue'

const tableHeaderStyle = {
  backgroundColor: '#f8fafc',
  color: '#475569',
  fontWeight: 600
}

const shelfStatusLabels = { on_sale: '在售', off_sale: '下架' }
const reviewStatusLabels = { normal: '正常', pending_review: '待人工复核' }

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
    const res = await getProductPageList({
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
