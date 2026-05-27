<template>
  <div>
    <n-h2>数据集</n-h2>
    <n-card style="margin-bottom: 16px">
      <n-grid :cols="24" x-gap="12" y-gap="12">
        <n-gi :span="6">
          <n-select
            v-model:value="filters.region"
            :options="regionOptions"
            placeholder="Region"
            filterable
          />
        </n-gi>
        <n-gi :span="6">
          <n-select
            v-model:value="filters.delay"
            :options="delayOptions"
            placeholder="Delay"
          />
        </n-gi>
        <n-gi :span="6">
          <n-select
            v-model:value="filters.universe"
            :options="universeOptions"
            placeholder="Universe"
            filterable
          />
        </n-gi>
        <n-gi :span="6">
          <n-button type="primary" @click="handleSearch" :loading="loading">
            搜索
          </n-button>
        </n-gi>
      </n-grid>
    </n-card>

    <n-data-table
      :columns="columns"
      :data="datasets"
      :loading="loading"
      :pagination="pagination"
      :bordered="false"
      :single-line="false"
      size="small"
    />

    <n-card v-if="!loading && datasets.length === 0" style="margin-top: 16px">
      <n-empty description="选择筛选条件后点击搜索" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { NTag, NButton } from "naive-ui";
import { searchDatasets } from "@/api/datasets";
import type { SearchDatasetsParams } from "@/api/datasets";

const router = useRouter();
const message = useMessage();

const loading = ref(false);
const datasets = ref<any[]>([]);

const filters = reactive({
  region: "usa",
  delay: 1,
  universe: "top3000",
});

const regionOptions = [
  { label: "USA", value: "usa" },
  { label: "Europe", value: "eur" },
  { label: "Asia", value: "asia" },
  { label: "Global", value: "global" },
];

const delayOptions = [1, 2, 3, 4].map((v) => ({ label: `${v}`, value: v }));

const universeOptions = [
  { label: "TOP3000", value: "top3000" },
  { label: "TOP2000", value: "top2000" },
  { label: "TOP1000", value: "top1000" },
  { label: "TOP500", value: "top500" },
];

const columns: DataTableColumn[] = [
  {
    title: "ID",
    key: "id",
    width: 80,
  },
  { title: "名称", key: "name", ellipsis: { tooltip: true } },
  {
    title: "区域",
    key: "region",
    width: 80,
    render: (row: any) =>
      h(NTag, { size: "small" }, { default: () => row.region }),
  },
  {
    title: "分类",
    key: "category",
    width: 100,
    render: (row: any) =>
      row.category ? h(NTag, { size: "small" }, { default: () => row.category }) : "",
  },
  {
    title: "覆盖",
    key: "coverage",
    width: 80,
    render: (row: any) => (row.coverage != null ? `${(row.coverage * 100).toFixed(1)}%` : ""),
  },
  {
    title: "评分",
    key: "valueScore",
    width: 80,
    render: (row: any) => row.valueScore?.toFixed(2) ?? "",
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
          onClick: () => router.push(`/datasets/${row.id}`),
        },
        { default: () => "详情" }
      ),
  },
];

const pagination = reactive({
  page: 1,
  pageSize: 50,
  showSizePicker: false,
  onChange: (page: number) => {
    pagination.page = page;
    handleSearch();
  },
});

async function handleSearch() {
  loading.value = true;
  try {
    const params: SearchDatasetsParams = {
      region: filters.region,
      delay: filters.delay,
      universe: filters.universe,
      limit: pagination.pageSize,
      offset: (pagination.page - 1) * pagination.pageSize,
    };
    const res = await searchDatasets(params);
    datasets.value = res.data.results ?? res.data.datasets ?? [];
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "查询失败");
  } finally {
    loading.value = false;
  }
}
</script>
