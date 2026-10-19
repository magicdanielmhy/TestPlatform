<template>
  <div>
    <div class="toolbar">
      <el-button type="primary" @click="openCreate">新建案例集</el-button>
    </div>

    <el-table :data="sets" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
      <el-table-column prop="member_count" label="用例数" width="90" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="openDetail(row)">成员</el-button>
          <el-button size="small" type="success" @click="run(row)">执行</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="createVisible" title="新建案例集" width="420px">
      <el-form :model="createForm" label-width="70px">
        <el-form-item label="名称" required>
          <el-input v-model="createForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="create">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="案例集成员" width="720px">
      <div class="toolbar">
        <el-select v-model="selectedCaseId" placeholder="选择要添加的用例" filterable style="width: 320px">
          <el-option
            v-for="c in allCases"
            :key="c.id"
            :label="`${c.name} (${c.method})`"
            :value="c.id"
          />
        </el-select>
        <el-button type="primary" @click="addMember">添加</el-button>
      </div>
      <el-table :data="members" border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="method" label="方法" width="90" />
        <el-table-column prop="url" label="URL" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="90">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="removeMember(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="runVisible" title="执行结果" width="760px">
      <div v-if="runResult" class="summary">
        <el-tag type="success">通过 {{ runResult.passed }}</el-tag>
        <el-tag type="danger">失败 {{ runResult.failed }}</el-tag>
        <el-tag type="warning">错误 {{ runResult.errors }}</el-tag>
        <span>共 {{ runResult.total }} 条</span>
      </div>
      <el-table v-if="runResult" :data="runResult.results" border>
        <el-table-column prop="test_case_id" label="用例ID" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="tagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="response_status" label="响应码" width="90" />
        <el-table-column prop="error" label="错误" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const sets = ref([])
const allCases = ref([])
const loading = ref(false)

const createVisible = ref(false)
const createForm = reactive({ name: '', description: '' })

const detailVisible = ref(false)
const currentSetId = ref(null)
const members = ref([])
const selectedCaseId = ref(null)

const runVisible = ref(false)
const runResult = ref(null)

async function load() {
  loading.value = true
  try {
    const [setsRes, casesRes] = await Promise.all([
      api.get('/api/test-case-sets'),
      api.get('/api/test-cases')
    ])
    sets.value = setsRes.data
    allCases.value = casesRes.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(createForm, { name: '', description: '' })
  createVisible.value = true
}

async function create() {
  await api.post('/api/test-case-sets', createForm)
  ElMessage.success('已创建')
  createVisible.value = false
  load()
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(`确定删除案例集「${row.name}」？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  await api.delete(`/api/test-case-sets/${row.id}`)
  ElMessage.success('已删除')
  load()
}

async function openDetail(row) {
  currentSetId.value = row.id
  selectedCaseId.value = null
  const { data } = await api.get(`/api/test-case-sets/${row.id}`)
  members.value = data.members
  detailVisible.value = true
}

async function addMember() {
  if (!selectedCaseId.value) {
    ElMessage.warning('请先选择用例')
    return
  }
  await api.post(`/api/test-case-sets/${currentSetId.value}/members`, {
    test_case_id: selectedCaseId.value
  })
  ElMessage.success('已添加')
  await openDetail({ id: currentSetId.value })
  load()
}

async function removeMember(row) {
  await api.delete(`/api/test-case-sets/${currentSetId.value}/members/${row.id}`)
  ElMessage.success('已移除')
  await openDetail({ id: currentSetId.value })
  load()
}

async function run(row) {
  const { data } = await api.post(`/api/test-case-sets/${row.id}/execute`)
  runResult.value = data
  runVisible.value = true
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
.summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
</style>
