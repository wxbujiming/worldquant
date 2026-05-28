<template>
  <div>
    <n-h2>Alpha 列表</n-h2>

    <n-tabs v-model:value="tabValue" type="line" animated style="margin-bottom: 4px">
      <n-tab-pane name="all" tab="全部" />
      <n-tab-pane name="qualified" tab="达标" />
      <n-tab-pane name="unqualified" tab="未达标" />
      <n-tab-pane name="submitted" tab="已提交" />
    </n-tabs>

    <n-card style="margin-bottom: 16px">
      <n-grid :cols="24" x-gap="8" y-gap="8">
        <n-gi :span="6">
          <n-input
            v-model:value="filters.keyword"
            placeholder="关键词搜索 (ID/名称/标签/表达式)"
            clearable
          />
        </n-gi>
        <n-gi :span="3">
          <n-input-number
            v-model:value="filters.sharpe_min"
            placeholder="Sharpe min"
            clearable
            :precision="2"
            :step="0.1"
          />
        </n-gi>
        <n-gi :span="3">
          <n-input-number
            v-model:value="filters.sharpe_max"
            placeholder="Sharpe max"
            clearable
            :precision="2"
            :step="0.1"
          />
        </n-gi>
        <n-gi :span="3">
          <n-input-number
            v-model:value="filters.fitness_min"
            placeholder="Fitness min"
            clearable
            :precision="2"
            :step="0.1"
          />
        </n-gi>
        <n-gi :span="3">
          <n-input-number
            v-model:value="filters.fitness_max"
            placeholder="Fitness max"
            clearable
            :precision="2"
            :step="0.1"
          />
        </n-gi>
        <n-gi :span="3">
          <n-select
            v-model:value="filters.self_corr"
            :options="selfCorrOptions"
            placeholder="自相关"
            clearable
          />
        </n-gi>
        <n-gi :span="3">
          <n-button type="primary" @click="handleSearch" :loading="loading" block>
            搜索
          </n-button>
        </n-gi>
      </n-grid>
      <n-grid :cols="24" x-gap="8" y-gap="8" style="margin-top: 8px">
        <n-gi :span="4">
          <n-date-picker
            v-model:value="filters.date_from"
            type="date"
            placeholder="创建日期起"
            clearable
            style="width: 100%"
          />
        </n-gi>
        <n-gi :span="4">
          <n-date-picker
            v-model:value="filters.date_to"
            type="date"
            placeholder="创建日期止"
            clearable
            style="width: 100%"
          />
        </n-gi>
        <n-gi :span="4">
          <n-select
            v-model:value="filters.dataset"
            :options="datasetOptions"
            placeholder="数据集"
            filterable
            clearable
          />
        </n-gi>
        <n-gi :span="3">
          <n-select
            v-model:value="filters.region"
            :options="regionOptions"
            placeholder="地区"
            clearable
          />
        </n-gi>
        <n-gi :span="3">
          <n-select
            v-model:value="filters.stage"
            :options="stageOptions"
            placeholder="阶段"
            clearable
          />
        </n-gi>
        <n-gi :span="3">
          <n-select
            v-model:value="filters.grade"
            :options="gradeOptions"
            placeholder="Grade"
            clearable
          />
        </n-gi>
        <n-gi :span="3">
          <n-select
            v-model:value="filters.color"
            :options="colorOptions"
            placeholder="颜色"
            clearable
          />
        </n-gi>
      </n-grid>
      <n-grid :cols="24" x-gap="8" y-gap="8" style="margin-top: 8px">
        <n-gi :span="2" :offset="20">
          <n-button @click="handleSync" :loading="syncing" block>
            同步
          </n-button>
        </n-gi>
      </n-grid>
    </n-card>

    <n-text depth="3" style="font-size: 12px; padding: 0 0 8px 4px; display: block">
      共 {{ totalCount }} 条，当前页 {{ currentPageCount }} 条
    </n-text>

    <n-data-table
      :columns="columns"
      :data="alphas"
      :loading="loading"
      :bordered="false"
      :single-line="false"
      size="small"
      :pagination="pagination"
      :scroll-x="2200"
    />
  </div>
</template>

<script setup lang="ts">
import { h, ref, reactive, computed, watch, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { NTag, NButton } from "naive-ui";
import { getCachedAlphas, syncAlphas } from "@/api/cache";

const router = useRouter();
const message = useMessage();

const loading = ref(true);
const syncing = ref(false);
const alphas = ref<any[]>([]);
const tabValue = ref("qualified");

const filters = reactive({
  keyword: "",
  sharpe_min: null as number | null,
  sharpe_max: null as number | null,
  fitness_min: null as number | null,
  fitness_max: null as number | null,
  self_corr: null as string | null,
  date_from: null as number | null,
  date_to: null as number | null,
  dataset: null as string | null,
  region: null as string | null,
  stage: null as string | null,
  grade: null as string | null,
  color: null as string | null,
});

const regionOptions = [
  { label: "USA", value: "usa" },
  { label: "Europe", value: "eur" },
  { label: "Asia", value: "asia" },
  { label: "Global", value: "global" },
];

const stageOptions = [
  { label: "IS", value: "IS" },
  { label: "OS", value: "OS" },
];

const gradeOptions = [
  { label: "SPECTACULAR", value: "SPECTACULAR" },
  { label: "EXCELLENT", value: "EXCELLENT" },
  { label: "GOOD", value: "GOOD" },
  { label: "AVERAGE", value: "AVERAGE" },
  { label: "INFERIOR", value: "INFERIOR" },
  { label: "UNKNOWN", value: "UNKNOWN" },
];

const colorOptions = [
  { label: "RED", value: "RED" },
  { label: "GREEN", value: "GREEN" },
  { label: "BLUE", value: "BLUE" },
];

const selfCorrOptions = [
  { label: "PASS", value: "PASS" },
  { label: "FAIL", value: "FAIL" },
  { label: "PENDING", value: "PENDING" },
  { label: "WARNING", value: "WARNING" },
];

const datasetOptions = [
  { label: "analyst4_USA_step1", value: "analyst4_USA_step1" },
  { label: "analyst4_USA_step2", value: "analyst4_USA_step2" },
  { label: "analyst4_USA_step3", value: "analyst4_USA_step3" },
  { label: "fundamental2_USA_step1", value: "fundamental2_USA_step1" },
  { label: "fundamental2_USA_step2", value: "fundamental2_USA_step2" },
  { label: "news12_USA_step1", value: "news12_USA_step1" },
];

const statusColorMap: Record<string, string> = {
  UNSUBMITTED: "default",
  ACTIVE: "success",
};

const gradeColorMap: Record<string, string> = {
  SPECTACULAR: "success",
  EXCELLENT: "info",
  GOOD: "primary",
  AVERAGE: "warning",
  INFERIOR: "error",
  UNKNOWN: "default",
};

const colorTagMap: Record<string, string> = {
  RED: "error",
  GREEN: "success",
  BLUE: "info",
};

function getSelfCorr(row: any): string {
  const checks = row.is?.checks ?? [];
  for (const c of checks) {
    if (c.name === "SELF_CORRELATION") return c.result ?? "—";
  }
  return "—";
}

const columns: DataTableColumn[] = [
  { title: "Alpha ID", key: "id", width: 100, ellipsis: { tooltip: true } },
  {
    title: "表达式",
    key: "regular.code",
    minWidth: 200,
    ellipsis: { tooltip: true },
    render: (row: any) => row.regular?.code ?? "—",
  },
  { title: "名称", key: "name", width: 180, ellipsis: { tooltip: true } },
  {
    title: "Tag",
    key: "tags",
    width: 140,
    render: (row: any) => {
      const tags = row.tags ?? [];
      if (tags.length === 0) return "—";
      return h("div", { style: "display:flex;flex-wrap:wrap;gap:2px" }, tags.slice(0, 2).map((t: string) =>
        h(NTag, { size: "tiny" }, { default: () => t })
      ));
    },
  },
  { title: "地区", key: "settings.region", width: 70, render: (row: any) => row.settings?.region ?? "—" },
  { title: "股票池", key: "settings.universe", width: 90, render: (row: any) => row.settings?.universe ?? "—" },
  { title: "中性化", key: "settings.neutralization", width: 100, render: (row: any) => row.settings?.neutralization ?? "—" },
  {
    title: "Grade",
    key: "grade",
    width: 100,
    render: (row: any) =>
      row.grade
        ? h(NTag, { type: (gradeColorMap[row.grade] as any) ?? "default", size: "small" }, { default: () => row.grade })
        : "—",
  },
  {
    title: "颜色",
    key: "color",
    width: 70,
    render: (row: any) =>
      row.color
        ? h(NTag, { type: (colorTagMap[row.color] as any) ?? "default", size: "small" }, { default: () => row.color })
        : "—",
  },
  { title: "Sharpe", key: "is.sharpe", width: 80, render: (row: any) => row.is?.sharpe?.toFixed(2) ?? "—" },
  { title: "Fitness", key: "is.fitness", width: 80, render: (row: any) => row.is?.fitness?.toFixed(2) ?? "—" },
  { title: "Returns", key: "is.returns", width: 80, render: (row: any) => row.is?.returns?.toFixed(2) ?? "—" },
  { title: "Turnover", key: "is.turnover", width: 80, render: (row: any) => row.is?.turnover?.toFixed(2) ?? "—" },
  {
    title: "Self Corr",
    key: "self_corr",
    width: 90,
    render: (row: any) => {
      const r = getSelfCorr(row);
      const typeMap: Record<string, string> = { PASS: "success", FAIL: "error", PENDING: "warning", WARNING: "info" };
      return r !== "—"
        ? h(NTag, { type: (typeMap[r] as any) ?? "default", size: "small" }, { default: () => r })
        : "—";
    },
  },
  {
    title: "状态",
    key: "status",
    width: 100,
    render: (row: any) =>
      h(NTag, { type: (statusColorMap[row.status] as any) ?? "default", size: "small" }, { default: () => row.status }),
  },
  {
    title: "创建时间",
    key: "dateCreated",
    width: 160,
    render: (row: any) => row.dateCreated ? new Date(row.dateCreated).toLocaleString("zh-CN") : "—",
  },
  {
    title: "提交时间",
    key: "dateSubmitted",
    width: 160,
    render: (row: any) => row.dateSubmitted ? new Date(row.dateSubmitted).toLocaleString("zh-CN") : "—",
  },
  {
    title: "操作",
    key: "actions",
    width: 70,
    render: (row: any) =>
      h(NButton, { size: "small", ghost: true, type: "primary", onClick: () => router.push(`/alphas/${row.id}`) }, { default: () => "详情" }),
  },
];

const pagination = reactive({
  page: 1,
  pageSize: 20,
  pageSizes: [20, 50, 100],
  showSizePicker: true,
  onChange: (page: number) => {
    pagination.page = page;
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize;
    pagination.page = 1;
  },
});

const totalCount = computed(() => alphas.value.length);
const currentPageCount = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize;
  return Math.min(pagination.pageSize, Math.max(0, totalCount.value - start));
});

async function handleSearch() {
  loading.value = true;
  try {
    const res = await getCachedAlphas();
    let items = res.data.results ?? [];

    for (const a of items) {
      (a as any).self_corr = getSelfCorr(a);
    }

    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase();
      items = items.filter(
        (a: any) =>
          (a.id && a.id.toLowerCase().includes(kw)) ||
          (a.name && a.name.toLowerCase().includes(kw)) ||
          (a.regular?.code && a.regular.code.toLowerCase().includes(kw)) ||
          (a.tags && a.tags.some((t: string) => t.toLowerCase().includes(kw)))
      );
    }
    if (filters.sharpe_min != null) {
      items = items.filter((a: any) => (a.is?.sharpe ?? -Infinity) >= filters.sharpe_min!);
    }
    if (filters.sharpe_max != null) {
      items = items.filter((a: any) => (a.is?.sharpe ?? Infinity) <= filters.sharpe_max!);
    }
    if (filters.fitness_min != null) {
      items = items.filter((a: any) => (a.is?.fitness ?? -Infinity) >= filters.fitness_min!);
    }
    if (filters.fitness_max != null) {
      items = items.filter((a: any) => (a.is?.fitness ?? Infinity) <= filters.fitness_max!);
    }
    if (filters.self_corr) {
      items = items.filter((a: any) => (a as any).self_corr === filters.self_corr);
    }
    if (filters.date_from) {
      const from = new Date(filters.date_from).toISOString().slice(0, 10);
      items = items.filter((a: any) => a.dateCreated && a.dateCreated.slice(0, 10) >= from);
    }
    if (filters.date_to) {
      const to = new Date(filters.date_to).toISOString().slice(0, 10);
      items = items.filter((a: any) => a.dateCreated && a.dateCreated.slice(0, 10) <= to);
    }
    if (filters.dataset) {
      items = items.filter((a: any) => a.tags && a.tags.includes(filters.dataset));
    }
    if (filters.region) {
      items = items.filter((a: any) => a.settings?.region === filters.region.toUpperCase());
    }
    if (filters.stage) {
      items = items.filter((a: any) => a.stage === filters.stage);
    }
    if (filters.grade) {
      items = items.filter((a: any) => a.grade === filters.grade);
    }
    if (filters.color) {
      items = items.filter((a: any) => a.color === filters.color);
    }

    // Tab 筛选
    if (tabValue.value === "qualified") {
      items = items.filter((a: any) => a.grade && a.grade !== "INFERIOR" && a.color !== "RED");
    } else if (tabValue.value === "unqualified") {
      items = items.filter((a: any) => a.grade === "INFERIOR" || a.color === "RED");
    } else if (tabValue.value === "submitted") {
      items = items.filter((a: any) => a.status === "ACTIVE");
    }

    alphas.value = items;
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "查询失败");
  } finally {
    loading.value = false;
  }
}

async function handleSync() {
  syncing.value = true;
  try {
    const res = await syncAlphas();
    message.success(res.data.message);
    await handleSearch();
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "同步失败");
  } finally {
    syncing.value = false;
  }
}

watch(tabValue, () => {
  pagination.page = 1;
  handleSearch();
});

onMounted(handleSearch);
</script>
