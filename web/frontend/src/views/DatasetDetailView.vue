<template>
  <div v-if="loading">
    <n-spin size="large" />
  </div>
  <div v-else-if="dataset">
    <n-button quaternary @click="$router.back()" style="margin-bottom: 16px">
      ← 返回
    </n-button>
    <n-h2>{{ dataset.name }}</n-h2>
    <n-description :title="`ID: ${dataset.id}`" />

    <n-grid :cols="4" x-gap="16" y-gap="16" style="margin: 16px 0">
      <n-gi>
        <n-statistic label="Region" :value="dataset.region" />
      </n-gi>
      <n-gi>
        <n-statistic
          label="Coverage"
          :value="dataset.coverage != null ? (dataset.coverage * 100).toFixed(1) + '%' : '—'"
        />
      </n-gi>
      <n-gi>
        <n-statistic label="Value Score" :value="dataset.valueScore?.toFixed(2) ?? '—'" />
      </n-gi>
      <n-gi>
        <n-statistic label="Dataset Type" :value="dataset.type ?? '—'" />
      </n-gi>
    </n-grid>

    <n-card title="数据字段" style="margin-top: 16px">
      <template #header-extra>
        <n-select
          v-model:value="fieldFilters.type"
          :options="fieldTypeOptions"
          placeholder="字段类型"
          clearable
          style="width: 140px"
          @update:value="loadFields"
        />
      </template>
      <n-data-table
        :columns="fieldColumns"
        :data="fields"
        :loading="fieldsLoading"
        :bordered="false"
        :single-line="false"
        size="small"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { NTag } from "naive-ui";
import { getDataset } from "@/api/datasets";
import { searchFields as searchApiFields } from "@/api/fields";

const route = useRoute();
const router = useRouter();
const message = useMessage();

const loading = ref(true);
const dataset = ref<any>(null);
const fields = ref<any[]>([]);
const fieldsLoading = ref(false);

const fieldFilters = ref<{ type: string | null }>({ type: null });

const fieldTypeOptions = [
  { label: "全部", value: null },
  { label: "因子 (factor)", value: "factor" },
  { label: "原始数据 (raw)", value: "raw" },
];

const fieldColumns: DataTableColumn[] = [
  { title: "ID", key: "id", width: 80 },
  { title: "Name", key: "name", ellipsis: { tooltip: true } },
  { title: "Type", key: "type", width: 100 },
  {
    title: "Category",
    key: "category",
    width: 100,
    render: (row: any) =>
      row.category ? h(NTag, { size: "small" }, { default: () => row.category }) : "",
  },
  {
    title: "Coverage",
    key: "coverage",
    width: 80,
    render: (row: any) =>
      row.coverage != null ? `${(row.coverage * 100).toFixed(1)}%` : "",
  },
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
  await loadFields();
}

async function loadFields() {
  if (!dataset.value) return;
  fieldsLoading.value = true;
  try {
    const res = await searchApiFields({
      region: dataset.value.region,
      delay: 1,
      universe: "top3000",
      dataset_id: dataset.value.id,
      type: fieldFilters.value.type ?? undefined,
    });
    fields.value = res.data.results ?? res.data.fields ?? [];
  } catch {
    fields.value = [];
  } finally {
    fieldsLoading.value = false;
  }
}

onMounted(loadData);
</script>
