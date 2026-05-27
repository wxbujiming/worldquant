<template>
  <div v-if="loading">
    <n-spin size="large" />
  </div>
  <div v-else-if="dataset">
    <n-button quaternary @click="$router.back()" style="margin-bottom: 16px">
      ← 返回
    </n-button>
    <n-h2>{{ dataset.name }}</n-h2>
    <n-text depth="3">{{ dataset.description }}</n-text>

    <n-grid :cols="4" x-gap="16" y-gap="16" style="margin: 16px 0">
      <n-gi>
        <n-statistic label="类型" :value="dataset.category?.name ?? dataset.category ?? '—'" />
      </n-gi>
      <n-gi>
        <n-statistic label="子类" :value="dataset.subcategory?.name ?? dataset.subcategory ?? '—'" />
      </n-gi>
      <n-gi>
        <n-statistic label="数据集 ID" :value="dataset.id" />
      </n-gi>
      <n-gi>
        <n-statistic label="研究论文" :value="dataset.researchPapers ?? 0" />
      </n-gi>
    </n-grid>

    <n-card title="各配置覆盖情况" style="margin-top: 16px">
      <n-data-table
        :columns="dataColumns"
        :data="dataset.data ?? []"
        :bordered="false"
        :single-line="false"
        size="small"
        :max-height="300"
      />
    </n-card>

    <n-card title="数据字段" style="margin-top: 16px">
      <n-empty description="WorldQuant Brain 的字段查询接口 (data-fields) 已不可用，暂无法获取字段列表" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { getDataset } from "@/api/datasets";

const route = useRoute();
const message = useMessage();

const loading = ref(true);
const dataset = ref<any>(null);

const dataColumns: DataTableColumn[] = [
  { title: "区域", key: "region", width: 80 },
  { title: "延迟", key: "delay", width: 70 },
  { title: "股票池", key: "universe", width: 100 },
  {
    title: "覆盖度",
    key: "coverage",
    width: 90,
    render: (row: any) =>
      row.coverage != null ? `${(row.coverage * 100).toFixed(1)}%` : "—",
  },
  {
    title: "价值评分",
    key: "valueScore",
    width: 100,
    render: (row: any) => row.valueScore?.toFixed(2) ?? "—",
  },
  { title: "Alpha 数", key: "alphaCount", width: 90 },
  { title: "用户数", key: "userCount", width: 80 },
  { title: "字段数", key: "fieldCount", width: 80 },
  { title: "日期覆盖", key: "dateCoverage", width: 90 },
];

async function loadData() {
  const id = route.params.id as string;
  loading.value = true;
  try {
    const res = await getDataset(id);
    dataset.value = res.data;
  } catch (err: any) {
    message.error("加载数据集失败");
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>
