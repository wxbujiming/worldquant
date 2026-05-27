<template>
  <div>
    <n-h2>仪表盘</n-h2>
    <n-p depth="3">WorldQuant Brain Web 管理界面</n-p>

    <n-grid :cols="2" x-gap="16" y-gap="16" style="margin-top: 16px">
      <n-gi>
        <n-card title="本地缓存">
          <n-descriptions label-placement="left" :column="1">
            <n-descriptions-item label="算子">
              <n-number-animation :from="0" :to="stats.operators" />
            </n-descriptions-item>
            <n-descriptions-item label="数据集">
              <n-number-animation :from="0" :to="stats.datasets" />
            </n-descriptions-item>
            <n-descriptions-item label="数据字段">
              <n-number-animation :from="0" :to="stats.fields" />
            </n-descriptions-item>
            <n-descriptions-item label="Alpha">
              <n-number-animation :from="0" :to="stats.alphas ?? 0" />
            </n-descriptions-item>
            <n-descriptions-item label="上次同步">
              {{ lastSyncText || "从未同步" }}
            </n-descriptions-item>
          </n-descriptions>
          <template #footer>
            <n-space>
              <n-button size="small" @click="refreshStats" :loading="loading">
                刷新状态
              </n-button>
              <n-button
                size="small"
                type="primary"
                @click="syncAll"
                :loading="syncing"
                :disabled="syncing"
              >
                同步所有数据
              </n-button>
            </n-space>
          </template>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card title="快速操作">
          <n-space vertical>
            <n-button block @click="$router.push('/datasets')">
              浏览数据集
            </n-button>
            <n-button block @click="$router.push('/operators')">
              浏览算子
            </n-button>
            <n-button block @click="$router.push('/alphas')">
              管理 Alpha
            </n-button>
            <n-button block @click="$router.push('/simulate')">
              模拟控制台
            </n-button>
          </n-space>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { useMessage } from "naive-ui";
import { getCacheStats, syncOperators, syncDatasets, syncFields, syncAlphas } from "@/api/cache";

const message = useMessage();
const loading = ref(false);
const syncing = ref(false);

const stats = reactive({
  operators: 0,
  datasets: 0,
  fields: 0,
  alphas: 0,
  last_sync: {} as Record<string, string>,
});

const lastSyncText = computed(() => {
  const times = Object.values(stats.last_sync);
  if (times.length === 0) return "";
  const latest = times.sort().reverse()[0];
  return new Date(latest).toLocaleString("zh-CN");
});

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

async function syncAll() {
  syncing.value = true;
  try {
    const op = await syncOperators();
    message.success(op.data.message);
    const ds = await syncDatasets();
    message.success(ds.data.message);
    const f = await syncFields();
    message.success(f.data.message);
    const a = await syncAlphas();
    message.success(a.data.message);
    await refreshStats();
    message.success("全部同步完成");
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "同步失败，请先登录");
  } finally {
    syncing.value = false;
  }
}

onMounted(refreshStats);
</script>
