<template>
  <div>
    <div class="toolbar">
      <el-button type="primary" @click="openCreate">新建用例</el-button>
    </div>

    <el-table :data="cases" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column prop="method" label="方法" width="90" />
      <el-table-column prop="url" label="URL" min-width="220" show-overflow-tooltip />
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="success" @click="run(row)">执行</el-button>
          <el-button size="small" @click="viewHistory(row)">结果</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑用例' : '新建用例'" width="640px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="方法" required>
          <el-select v-model="form.method" style="width: 160px">
            <el-option v-for="m in methods" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="URL" required>
          <el-input v-model="form.url" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="请求头">
          <el-input
            v-model="headersText"
            type="textarea"
            placeholder='JSON，如 {"Content-Type":"application/json"}'
          />
        </el-form-item>
        <el-form-item label="请求体">
          <el-input v-model="form.body" type="textarea" />
        </el-form-item>
        <el-form-item label="断言">
          <el-input
            v-model="assertionsText"
            type="textarea"
            placeholder='JSON 数组，如 [{"type":"status","expected":200},{"type":"body","expected":"ok","operator":"contains"}]'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="historyVisible" title="执行结果" width="720px">
      <el-table :data="history" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="tagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="response_status" label="响应码" width="90" />
        <el-table-column prop="finished_at" label="时间" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD']

const cases = ref([])
const loading = ref(false)

const dialogVisible = ref(false)
const editing = ref(false)
const editingId = ref(null)
const form = reactive({ name: '', method: 'GET', url: '', description: '', body: '' })
const headersText = ref('')
const assertionsText = ref('')

const historyVisible = ref(false)
const history = ref([])

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/test-cases')
    cases.value = data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = false
  editingId.value = null
  Object.assign(form, { name: '', method: 'GET', url: '', description: '', body: '' })
  headersText.value = ''
  assertionsText.value = ''
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = true
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    method: row.method,
    url: row.url,
    description: row.description || '',
    body: row.body || ''
  })
  headersText.value = JSON.stringify(row.headers || {}, null, 2)
  assertionsText.value = JSON.stringify(row.assertions || [], null, 2)
  dialogVisible.value = true
}

function parseJson(text, fallback) {
  if (!text || !text.trim()) return fallback
  try {
    return JSON.parse(text)
  } catch {
    throw new Error('JSON 格式错误')
  }
}

async function save() {
  let payload
  try {
    payload = {
      name: form.name,
      method: form.method,
      url: form.url,
      description: form.description,
      body: form.body,
      headers: parseJson(headersText.value, {}),
      assertions: parseJson(assertionsText.value, [])
    }
  } catch (e) {
    ElMessage.error(e.message)
    return
  }
  if (editing.value) {
    await api.put(`/api/test-cases/${editingId.value}`, payload)
  } else {
    await api.post('/api/test-cases', payload)
  }
  ElMessage.success('已保存')
  dialogVisible.value = false
  load()
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(`确定删除用例「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  await api.delete(`/api/test-cases/${row.id}`)
  ElMessage.success('已删除')
  load()
}

async function run(row) {
  const { data } = await api.post(`/api/test-cases/${row.id}/execute`)
  ElMessageBox.alert(`执行结果：${data.status}`, '执行完成')
}

async function viewHistory(row) {
  const { data } = await api.get(`/api/test-cases/${row.id}/executions`)
  history.value = data
  historyVisible.value = true
}

function tagType(status) {
  if (status === 'pass') return 'success'
  if (status === 'fail') return 'danger'
  return 'warning'
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  margin-bottom: 12px;
}
</style>
