<template>
  <div>
    <n-h2>Alpha 列表</n-h2>

    <n-card style="margin-bottom: 16px">
      <n-grid :cols="24" x-gap="12" y-gap="12">
        <n-gi :span="6">
          <n-select
            v-model:value="filters.status"
            :options="statusOptions"
            placeholder="状态"
            clearable
          />
        </n-gi>
        <n-gi :span="6">
          <n-select
            v-model:value="filters.region"
            :options="regionOptions"
            placeholder="Region"
            clearable
          />
        </n-gi>
        <n-gi :span="4">
          <n-input-number
            v-model:value="filters.sharpe_min"
            placeholder="Sharpe min"
            clearable
            :precision="2"
            :step="0.1"
          />
        </n-gi>
        <n-gi :span="4">
          <n-input-number
            v-model:value="filters.sharpe_max"
            placeholder="Sharpe max"
            clearable
            :precision="2"
            :step="0.1"
          />
        </n-gi>
        <n-gi :span="4">
          <n-button type="primary" @click="handleSearch" :loading="loading">
            搜索
          </n-button>
        </n-gi>
      </n-grid>
    </n-card>

    <n-data-table
      :columns="columns"
      :data="alphas"
      :loading="loading"
      :bordered="false"
      :single-line="false"
      size="small"
      :pagination="pagination"
    />
  </div>
</template>

<script setup lang="ts">
import { h, ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { NTag, NButton } from "naive-ui";
import { filterAlphas } from "@/api/alphas";
import type { FilterAlphasParams } from "@/api/alphas";

const router = useRouter();
const message = useMessage();

const loading = ref(false);
const alphas = ref<any[]>([]);

const filters = reactive({
  status: null as string | null,
  region: null as string | null,
  sharpe_min: null as number | null,
  sharpe_max: null as number | null,
});

const statusOptions = [
  { label: "通过 (PASSED)", value: "PASSED" },
  { label: "失败 (FAILED)", value: "FAILED" },
  { label: "进行中 (INPROGRESS)", value: "INPROGRESS" },
  { label: "已提交 (SUBMITTED)", value: "SUBMITTED" },
];

const regionOptions = [
  { label: "USA", value: "usa" },
  { label: "Europe", value: "eur" },
  { label: "Asia", value: "asia" },
  { label: "Global", value: "global" },
];

const statusColorMap: Record<string, string> = {
  PASSED: "success",
  FAILED: "error",
  INPROGRESS: "warning",
  SUBMITTED: "info",
};

const columns: DataTableColumn[] = [
  { title: "ID", key: "id", width: 120, ellipsis: { tooltip: true } },
  { title: "名称", key: "name", ellipsis: { tooltip: true } },
  {
    title: "状态",
    key: "status",
    width: 120,
    render: (row: any) =>
      h(
        NTag,
        { type: (statusColorMap[row.status] as any) ?? "default", size: "small" },
        { default: () => row.status }
      ),
  },
  { title: "Sharpe", key: "is.sharpe", width: 90, render: (row: any) => row.is?.sharpe?.toFixed(3) ?? "—" },
  {
    title: "收益率",
    key: "is.returns",
    width: 90,
    render: (row: any) => row.is?.returns?.toFixed(3) ?? "—",
  },
  {
    title: "Fitness",
    key: "is.fitness",
    width: 90,
    render: (row: any) => row.is?.fitness?.toFixed(3) ?? "—",
  },
  {
    title: "Region",
    key: "settings.region",
    width: 80,
    render: (row: any) => row.settings?.region ?? "—",
  },
  {
    title: "操作",
    key: "actions",
    width: 100,
    render: (row: any) =>
      h(
        NButton,
        {
          size: "small",
          ghost: true,
          type: "primary",
          onClick: () => router.push(`/alphas/${row.id}`),
        },
        { default: () => "详情" }
      ),
  },
];

const pagination = reactive({
  page: 1,
  pageSize: 100,
  onChange: (page: number) => {
    pagination.page = page;
    handleSearch();
  },
});

async function handleSearch() {
  loading.value = true;
  try {
    const params: FilterAlphasParams = {
      limit: pagination.pageSize,
      offset: (pagination.page - 1) * pagination.pageSize,
    };
    if (filters.status) params.status = filters.status;
    if (filters.region) params.region = filters.region;
    if (filters.sharpe_min != null) params.sharpe_min = filters.sharpe_min;
    if (filters.sharpe_max != null) params.sharpe_max = filters.sharpe_max;

    const res = await filterAlphas(params);
    const data = res.data;
    alphas.value = data.results ?? data.alphas ?? [];
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "查询失败");
  } finally {
    loading.value = false;
  }
}
</script>
