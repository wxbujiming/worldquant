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
      <template #header-extra>
        <n-button size="small" @click="handleSyncFields" :loading="fieldsLoading">
          同步字段
        </n-button>
      </template>
      <n-alert v-if="fieldsMsg" type="info" closable style="margin-bottom: 12px">
        {{ fieldsMsg }}
      </n-alert>
      <n-text depth="3" style="font-size: 12px; padding: 0 0 8px 4px; display: block">
        共 {{ fieldsTotal }} 条，当前页 {{ fieldsPageCount }} 条
      </n-text>
      <n-data-table
        :columns="fieldColumns"
        :data="fields"
        :loading="fieldsLoading"
        :bordered="false"
        :single-line="false"
        size="small"
        :pagination="fieldsPagination"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, h, reactive, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { NTag } from "naive-ui";
import { getDataset } from "@/api/datasets";
import { getCachedFields, syncFields } from "@/api/cache";

const route = useRoute();
const message = useMessage();

const loading = ref(true);
const dataset = ref<any>(null);
const fields = ref<any[]>([]);
const fieldsLoading = ref(false);
const fieldsMsg = ref("");

const fieldsPagination = reactive({
  page: 1,
  pageSize: 20,
  pageSizes: [20, 50, 100],
  showSizePicker: true,
  onChange: (page: number) => { fieldsPagination.page = page; },
  onUpdatePageSize: (pageSize: number) => {
    fieldsPagination.pageSize = pageSize;
    fieldsPagination.page = 1;
  },
});

const fieldsTotal = computed(() => fields.value.length);
const fieldsPageCount = computed(() => {
  const start = (fieldsPagination.page - 1) * fieldsPagination.pageSize;
  return Math.min(fieldsPagination.pageSize, Math.max(0, fieldsTotal.value - start));
});

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

const fieldColumns: DataTableColumn[] = [
  { title: "ID", key: "id", width: 120, ellipsis: { tooltip: true } },
  { title: "Name", key: "name", ellipsis: { tooltip: true } },
  { title: "描述", key: "description", ellipsis: { tooltip: true } },
  {
    title: "类别",
    key: "category",
    width: 100,
    render: (row: any) => {
      const cat = row.category;
      let label = "";
      if (typeof cat === "object") label = cat?.name || cat?.id || "";
      else try { const p = JSON.parse(cat); label = p?.name || p?.id || cat; } catch { label = cat; }
      return label ? h(NTag, { size: "small" }, { default: () => label }) : "—";
    },
  },
  { title: "类型", key: "type", width: 80 },
  {
    title: "覆盖度",
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
  const dsId = dataset.value.id;
  fieldsLoading.value = true;
  fieldsMsg.value = "";
  try {
    const res = await getCachedFields(dsId);
    const items = res.data.results ?? [];
    if (items.length > 0) {
      fields.value = items;
      fieldsMsg.value = `共 ${items.length} 个字段`;
    } else {
      fieldsMsg.value = '该数据集暂未同步字段，点击「同步字段」按钮从 WB 拉取';
    }
  } catch {
    fieldsMsg.value = "加载字段失败";
  } finally {
    fieldsLoading.value = false;
  }
}

async function handleSyncFields() {
  if (!dataset.value) return;
  fieldsLoading.value = true;
  fieldsMsg.value = "正在同步字段...";
  try {
    const res = await syncFields(dataset.value.id);
    message.success(res.data.message);
    await loadFields();
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "同步字段失败");
    fieldsMsg.value = "";
  } finally {
    fieldsLoading.value = false;
  }
}

onMounted(loadData);
</script>
