<template>
  <div>
    <n-h2>仪表盘</n-h2>
    <n-p depth="3">WorldQuant Brain Web 管理界面</n-p>

    <n-card v-if="profile || simQuota" style="margin-bottom: 16px">
      <n-grid :cols="6" x-gap="16" y-gap="12">
        <n-gi>
          <n-statistic label="剩余模拟测试次数">
            <template #default>
              <span v-if="simQuota?.remaining != null" style="font-size: 24px; font-weight: 700; color: #2d8cf0">
                {{ simQuota.remaining }}
              </span>
              <span v-else>—</span>
            </template>
          </n-statistic>
        </n-gi>
        <n-gi>
          <n-statistic label="分数">
            <template #default>
              <n-number-animation :from="0" :to="profile?.score ?? 0" />
            </template>
          </n-statistic>
        </n-gi>
        <n-gi>
          <n-statistic label="等级">
            <template #default>
              <n-tag v-if="profile?.level" :type="levelTagType(profile.level)" size="large" style="font-size: 16px; font-weight: bold">
                {{ profile.level }}
              </n-tag>
              <span v-else>—</span>
            </template>
          </n-statistic>
        </n-gi>
        <n-gi>
          <n-statistic label="已提交 Alpha" :value="profile?.submittedAlphas ?? 0" />
        </n-gi>
        <n-gi>
          <n-statistic label="排名" :value="profile?.rank ?? '—'" />
        </n-gi>
        <n-gi>
          <n-statistic label="用户 ID" :value="profile?.id ?? '—'" />
        </n-gi>
      </n-grid>
    </n-card>

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

    <n-grid :cols="2" x-gap="16" y-gap="16" style="margin-top: 16px">
      <n-gi>
        <n-card title="Alpha Color 分布">
          <div ref="chartRef" style="height: 340px"></div>
          <n-empty v-if="noAlphaData" description="暂无 Alpha 数据" style="padding: 60px 0" />
        </n-card>
      </n-gi>
      <n-gi>
        <n-card title="Alpha 阻塞原因">
          <div ref="blockingChartRef" style="height: 340px"></div>
          <n-empty v-if="noAlphaData" description="暂无 Alpha 数据" style="padding: 60px 0" />
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from "vue";
import { useMessage } from "naive-ui";
import * as echarts from "echarts";
import {
  getCacheStats,
  syncOperators,
  syncDatasets,
  syncFields,
  syncAlphas,
  getCachedAlphas,
} from "@/api/cache";
import { getUserProfile, getSimulationQuota } from "@/api/auth";

const message = useMessage();
const loading = ref(false);
const profile = ref<any>(null);
const simQuota = ref<any>(null);

const levelColors: Record<string, string> = {
  BRONZE: "warning",
  SILVER: "info",
  GOLD: "success",
  PLATINUM: "primary",
};
function levelTagType(level: string) {
  return levelColors[level] || "default";
}

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

const chartRef = ref<HTMLDivElement | null>(null);
const blockingChartRef = ref<HTMLDivElement | null>(null);
const noAlphaData = ref(false);
let chartInstance: echarts.ECharts | null = null;
let blockingChartInstance: echarts.ECharts | null = null;

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
    if (key === "alphas") await loadColorChart(); // 刷新两个图表
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

const colorNameMap: Record<string, string> = {
  red: "红",
  green: "绿",
  blue: "蓝",
  yellow: "黄",
  orange: "橙",
  purple: "紫",
  cyan: "青",
  pink: "粉",
  brown: "棕",
  grey: "灰",
  gray: "灰",
  white: "白",
  black: "黑",
};

const colorColors: Record<string, string> = {
  red: "#ef4444",
  green: "#22c55e",
  blue: "#3b82f6",
  yellow: "#eab308",
  orange: "#f97316",
  purple: "#a855f7",
  cyan: "#06b6d4",
  pink: "#ec4899",
  brown: "#78716c",
  grey: "#6b7280",
  gray: "#6b7280",
};

function renderColorChart(alphaList: any[]) {
  noAlphaData.value = !alphaList || alphaList.length === 0;
  if (noAlphaData.value) return;

  const counts: Record<string, number> = {};
  for (const alpha of alphaList) {
    const c = (alpha.color || "unknown").toLowerCase();
    counts[c] = (counts[c] || 0) + 1;
  }

  const entries = Object.entries(counts)
    .filter(([, count]) => count > 0)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 4);

  const data = entries.map(([color, count]) => ({
    name: colorNameMap[color] || color,
    value: count,
    itemStyle: { color: colorColors[color] || "#6b7280" },
  }));

  if (data.length === 0) {
    noAlphaData.value = true;
    return;
  }

  nextTick(() => {
    if (!chartRef.value) return;
    if (!chartInstance) {
      chartInstance = echarts.init(chartRef.value);
    }
    chartInstance.setOption({
      tooltip: { trigger: "item", formatter: "{b}: {c}" },
      legend: {
        bottom: 0,
        type: "scroll",
        selector: [
          { type: "all", title: "全选" },
          { type: "inverse", title: "反选" },
        ],
      },
      series: [
        {
          type: "pie",
          radius: ["0%", "55%"],
          minAngle: 3,
          center: ["50%", "40%"],
          padAngle: 3,
          itemStyle: { borderRadius: 4 },
          label: {
            show: true,
            fontSize: 15,
            fontWeight: "bold",
            formatter: "{b}: {c}",
            lineHeight: 30,
          },
          labelLine: {
            length: 25,
            length2: 40,
            smooth: true,
          },
          emphasis: {
            label: { show: true, fontSize: 18, fontWeight: "bold" },
          },
          data,
        },
      ],
    });
  });
}

async function loadColorChart() {
  try {
    const res = await getCachedAlphas();
    const list = res.data.results ?? [];
    renderColorChart(list);
    renderBlockingChart(list);
  } catch {
    noAlphaData.value = true;
  }
}

const blockingLabels = ["Sharpe 不足", "Fitness 不足", "Turnover 不合适", "Self Corr 过高", "Checks 失败"];
const blockingColors = ["#ef4444", "#f97316", "#eab308", "#a855f7", "#6b7280"];

function renderBlockingChart(alphaList: any[]) {
  if (!alphaList || alphaList.length === 0) return;

  const counts: Record<string, number> = {
    sharpe: 0, fitness: 0, turnover: 0, self_corr: 0, checks: 0,
  };

  for (const alpha of alphaList) {
    let isData: any = null;
    if (typeof alpha.is_data === "string") {
      try { isData = JSON.parse(alpha.is_data); } catch {}
    } else if (typeof alpha.is === "object") {
      isData = alpha.is;
    }
    if (!isData) continue;

    const checks: any[] = isData.checks || [];
    const failedMap: Record<string, boolean> = {};
    for (const c of checks) {
      if (c.result === "FAIL") failedMap[c.name] = true;
    }

    const turnover = isData.turnover;
    const fitness = isData.fitness;
    const sharpe = isData.sharpe;

    // Self Corr 过高
    if (failedMap["SELF_CORRELATION"]) counts.self_corr++;

    // Turnover 不合适: 不在 [0.01, 0.70] 范围
    if (turnover != null && (turnover < 0.01 || turnover > 0.70)) counts.turnover++;

    // Fitness 不足: < 1.0
    if (fitness != null && fitness < 1.0) counts.fitness++;

    // Sharpe 不足: < 1.25
    if (sharpe != null && sharpe < 1.25) counts.sharpe++;

    // Checks 失败: LOW_SHARPE、LOW_FITNESS、LOW_SUB_UNIVERSE_SHARPE 都 FAIL
    if (failedMap["LOW_SHARPE"] && failedMap["LOW_FITNESS"] && failedMap["LOW_SUB_UNIVERSE_SHARPE"]) counts.checks++;
  }

  const keys = Object.keys(counts);
  const labels = keys.map((k) => blockingLabels[keys.indexOf(k)] || k);
  const values = keys.map((k) => counts[k]);
  const colors = keys.map((k) => blockingColors[keys.indexOf(k)] || "#6b7280");

  nextTick(() => {
    if (!blockingChartRef.value) return;
    if (!blockingChartInstance) {
      blockingChartInstance = echarts.init(blockingChartRef.value);
    }
    blockingChartInstance.setOption({
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: "{b}: {c}" },
      grid: { left: 110, right: 40, top: 10, bottom: 20 },
      xAxis: { type: "value", minInterval: 1 },
      yAxis: {
        type: "category",
        data: labels,
        axisLabel: { fontSize: 13, fontWeight: "bold" },
      },
      series: [
        {
          type: "bar",
          data: values.map((v, i) => ({
            value: v,
            itemStyle: { color: colors[i], borderRadius: [0, 4, 4, 0] },
          })),
          barMaxWidth: 36,
          label: {
            show: true,
            position: "right",
            fontSize: 14,
            fontWeight: "bold",
          },
        },
      ],
    });
  });
}

async function loadProfile() {
  try {
    const res = await getUserProfile();
    profile.value = res.data;
  } catch { /* 未登录 */ }
}

async function loadQuota() {
  try {
    const res = await getSimulationQuota();
    simQuota.value = res.data;
  } catch { /* 未登录 */ }
}

onMounted(() => {
  refreshStats();
  loadProfile();
  loadQuota();
  loadColorChart();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  chartInstance?.dispose();
  chartInstance = null;
  blockingChartInstance?.dispose();
  blockingChartInstance = null;
});

function handleResize() {
  chartInstance?.resize();
  blockingChartInstance?.resize();
}
</script>
