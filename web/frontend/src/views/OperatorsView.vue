<template>
  <div>
    <n-h2>算子浏览器</n-h2>

    <n-card style="margin-bottom: 16px">
      <n-space>
        <n-input
          v-model:value="searchText"
          placeholder="搜索算子..."
          clearable
          style="flex: 1"
          @input="filterOperators"
        />
        <n-button
          v-if="!useCache"
          type="primary"
          @click="handleSync"
          :loading="syncing"
        >
          缓存到本地
        </n-button>
        <n-button
          :type="useCache ? 'primary' : 'default'"
          @click="toggleSource"
        >
          {{ useCache ? "查看在线数据" : "查看本地缓存" }}
        </n-button>
      </n-space>
      <n-text v-if="useCache" depth="3" style="font-size: 12px">
        当前显示本地缓存数据（{{ operators.length }} 条）
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
import { ref, onMounted } from "vue";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { searchOperators } from "@/api/operators";
import { getCachedOperators, syncOperators } from "@/api/cache";

const message = useMessage();
const loading = ref(true);
const syncing = ref(false);
const operators = ref<any[]>([]);
const filtered = ref<any[]>([]);
const searchText = ref("");
const useCache = ref(false);

const columns: DataTableColumn[] = [
  { title: "名称", key: "name", width: 200 },
  { title: "说明", key: "description", ellipsis: { tooltip: true } },
  { title: "类型", key: "type", width: 100 },
  { title: "分类", key: "category", width: 100 },
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

async function loadOnline() {
  loading.value = true;
  try {
    const res = await searchOperators();
    const data = res.data;
    operators.value = data.results ?? data.operators ?? data;
    filtered.value = operators.value;
  } catch (err: any) {
    message.error("加载算子失败");
  } finally {
    loading.value = false;
  }
}

async function loadCached() {
  loading.value = true;
  try {
    const res = await getCachedOperators();
    operators.value = res.data.results ?? [];
    filtered.value = operators.value;
    if (operators.value.length === 0) {
      message.warning("本地暂无缓存数据，请先同步");
      useCache.value = false;
      await loadOnline();
      return;
    }
  } catch {
    message.error("读取缓存失败");
  } finally {
    loading.value = false;
  }
}

async function toggleSource() {
  useCache.value = !useCache.value;
  if (useCache.value) {
    await loadCached();
  } else {
    await loadOnline();
  }
}

async function handleSync() {
  syncing.value = true;
  try {
    const res = await syncOperators();
    message.success(res.data.message);
    if (useCache.value) await loadCached();
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "同步失败");
  } finally {
    syncing.value = false;
  }
}

onMounted(loadOnline);
</script>
