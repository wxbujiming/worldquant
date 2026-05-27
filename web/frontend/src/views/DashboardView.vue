<template>
  <div>
    <n-h2>仪表盘</n-h2>
    <n-p depth="3">WorldQuant Brain Web 管理界面</n-p>

    <n-space justify="space-between" style="margin-top: 16px">
      <span></span>
      <n-button size="small" @click="refreshStats" :loading="loading">
        刷新状态
      </n-button>
    </n-space>

    <n-grid :cols="4" x-gap="16" y-gap="16" style="margin-top: 16px">
      <n-gi v-for="item in cardItems" :key="item.key">
        <n-card :title="item.label">
          <n-number-animation :from="0" :to="stats[item.key]" />
          <div style="margin-top: 8px; font-size: 12px; color: #888">
            上次同步: {{ syncTime(item.key) || "从未同步" }}
          </div>
          <template #footer>
            <n-button
              size="small"
              type="primary"
              @click="handleSync(item.key)"
              :loading="syncing[item.key]"
              :disabled="syncing[item.key]"
            >
              同步
            </n-button>
          </template>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useMessage } from "naive-ui";
import {
  getCacheStats,
  syncOperators,
  syncDatasets,
  syncFields,
  syncAlphas,
} from "@/api/cache";

const message = useMessage();
const loading = ref(false);

const stats = reactive({
  operators: 0,
  datasets: 0,
  fields: 0,
  alphas: 0,
  last_sync: {} as Record<string, string>,
});

const syncing = reactive({
  operators: false,
  datasets: false,
  fields: false,
  alphas: false,
});

const cardItems = [
  { key: "operators", label: "算子" },
  { key: "datasets", label: "数据集" },
  { key: "fields", label: "数据字段" },
  { key: "alphas", label: "Alpha" },
];

const syncActions: Record<string, () => Promise<any>> = {
  operators: syncOperators,
  datasets: syncDatasets,
  fields: () => syncFields(),
  alphas: syncAlphas,
};

function syncTime(key: string): string {
  const t = stats.last_sync[key];
  return t ? new Date(t).toLocaleString("zh-CN") : "";
}

async function handleSync(key: string) {
  syncing[key] = true;
  try {
    const action = syncActions[key];
    if (!action) return;
    const res = await action();
    message.success(res.data.message);
    await refreshStats();
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "同步失败，请先登录");
  } finally {
    syncing[key] = false;
  }
}

async function refreshStats() {
  loading.value = true;
  try {
    const res = await getCacheStats();
    Object.assign(stats, res.data);
  } catch {
    // 首次运行时可能无缓存表，忽略
  } finally {
    loading.value = false;
  }
}

onMounted(refreshStats);
</script>
