<template>
  <div>
    <el-table :data="executions" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="test_case_id" label="用例ID" width="90" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="tagType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="response_status" label="响应码" width="90" />
      <el-table-column prop="error" label="错误" min-width="180" show-overflow-tooltip />
      <el-table-column prop="finished_at" label="时间" width="220" />
      <el-table-column label="操作" width="90">
        <template #default="{ row }">
          <el-button size="small" @click="view(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" title="执行详情" width="760px">
      <pre v-if="detail" class="detail">{{ JSON.stringify(detail, null, 2) }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const executions = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const detail = ref(null)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/executions')
    executions.value = data
  } finally {
    loading.value = false
  }
}

async function view(row) {
  const { data } = await api.get(`/api/executions/${row.id}`)
  detail.value = data
  detailVisible.value = true
}

function tagType(status) {
  if (status === 'pass') return 'success'
  if (status === 'fail') return 'danger'
  return 'warning'
}

onMounted(load)
</script>

<style scoped>
.detail {
  max-height: 480px;
  overflow: auto;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
}
</style>
