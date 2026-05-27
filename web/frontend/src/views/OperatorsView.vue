<template>
  <div>
    <n-h2>算子浏览器</n-h2>

    <n-card style="margin-bottom: 16px">
      <n-space justify="space-between">
        <n-input
          v-model:value="searchText"
          placeholder="搜索算子..."
          clearable
          style="min-width: 300px; flex: 1"
          @input="filterOperators"
        />
        <n-button type="primary" @click="handleSync" :loading="syncing">
          同步
        </n-button>
      </n-space>
      <n-text depth="3" style="font-size: 12px">
        共 {{ operators.length }} 条
      </n-text>
    </n-card>

    <n-data-table
      :columns="columns"
      :data="filtered"
      :loading="loading"
      :bordered="false"
      :single-line="false"
      size="small"
      :pagination="{ pageSize: 50 }"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from "vue";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { getCachedOperators, syncOperators, updateOperatorRemarks } from "@/api/cache";

const message = useMessage();
const loading = ref(true);
const syncing = ref(false);
const operators = ref<any[]>([]);
const filtered = ref<any[]>([]);
const searchText = ref("");

const columns: DataTableColumn[] = [
  { title: "名称", key: "name", width: 160 },
  { title: "描述", key: "definition", ellipsis: { tooltip: true }, width: 260 },
  { title: "说明", key: "description", ellipsis: { tooltip: true }, minWidth: 200 },
  { title: "类型", key: "type", width: 100 },
  { title: "分类", key: "category", width: 110 },
  { title: "备注", key: "remarks", width: 200,
    render: (row: any) =>
      h("div", { style: "display:flex;gap:4px;align-items:center" }, [
        h("input", {
          value: row.remarks ?? "",
          style: "flex:1;border:none;border-bottom:1px solid #d9d9d9;outline:none;background:transparent;padding:2px 4px",
          onInput: (e: any) => { row.remarks = e.target.value; },
          onChange: () => handleRemarksChange(row),
        }),
      ]),
  },
];

function filterOperators() {
  const t = searchText.value.toLowerCase();
  if (!t) {
    filtered.value = operators.value;
  } else {
    filtered.value = operators.value.filter(
      (o) =>
        (o.name && o.name.toLowerCase().includes(t)) ||
        (o.description && o.description.toLowerCase().includes(t)) ||
        (o.category && o.category.toLowerCase().includes(t))
    );
  }
}

async function loadData() {
  loading.value = true;
  try {
    const res = await getCachedOperators();
    operators.value = res.data.results ?? [];
    filtered.value = operators.value;
  } catch {
    message.error("读取缓存失败");
  } finally {
    loading.value = false;
  }
}

async function handleSync() {
  syncing.value = true;
  try {
    const res = await syncOperators();
    message.success(res.data.message);
    await loadData();
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "同步失败");
  } finally {
    syncing.value = false;
  }
}

async function handleRemarksChange(row: any) {
  try {
    await updateOperatorRemarks(row.name, row.remarks ?? "");
  } catch {
    message.error("备注更新失败");
  }
}

onMounted(loadData);
</script>
