<template>
  <div>
    <n-h2>数据集</n-h2>
    <n-p depth="3">共 {{ kinds.length }} 种数据集（含 {{ totalVariants }} 个配置变体）</n-p>

    <n-card style="margin-bottom: 16px">
      <n-grid :cols="24" x-gap="12" y-gap="12">
        <n-gi :span="8">
          <n-input
            v-model:value="searchText"
            placeholder="搜索数据集名称..."
            clearable
            @input="handleSearch"
          />
        </n-gi>
        <n-gi :span="3" :offset="13">
          <n-button @click="handleSync" :loading="syncing" block>
            同步
          </n-button>
        </n-gi>
      </n-grid>
    </n-card>

    <n-data-table
      :columns="columns"
      :data="filteredKinds"
      :loading="loading"
      :pagination="pagination"
      :bordered="false"
      :single-line="false"
      size="small"
      striped
    />

    <n-card v-if="!loading && filteredKinds.length === 0" style="margin-top: 16px">
      <n-empty description="无数据" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { NTag, NButton } from "naive-ui";
import { getCachedDatasetKinds } from "@/api/cache";

const router = useRouter();
const message = useMessage();

const loading = ref(true);
const syncing = ref(false);
const kinds = ref<any[]>([]);
const searchText = ref("");

const filteredKinds = computed(() => {
  if (!searchText.value) return kinds.value;
  const q = searchText.value.toLowerCase();
  return kinds.value.filter((k: any) =>
    (k.name || "").toLowerCase().includes(q) ||
    (k.id || "").toLowerCase().includes(q)
  );
});

const totalVariants = computed(() =>
  kinds.value.reduce((sum: number, k: any) => sum + (k.variant_count || 0), 0)
);

const columns: DataTableColumn[] = [
  { title: "ID", key: "id", width: 100 },
  { title: "名称", key: "name", ellipsis: { tooltip: true } },
  {
    title: "分类",
    key: "category",
    width: 120,
    render: (row: any) => {
      const cat = row.category;
      const label = typeof cat === "object" ? cat?.name || cat?.id : cat;
      return label ? h(NTag, { size: "small" }, { default: () => label }) : "—";
    },
  },
  {
    title: "子类",
    key: "subcategory",
    width: 140,
    ellipsis: { tooltip: true },
    render: (row: any) => {
      const sub = row.subcategory;
      const label = typeof sub === "object" ? sub?.name || sub?.id : sub;
      return label ?? "—";
    },
  },
  {
    title: "描述",
    key: "description",
    ellipsis: { tooltip: true },
    minWidth: 200,
  },
  {
    title: "变体数",
    key: "variant_count",
    width: 80,
    sorter: (a: any, b: any) => (a.variant_count ?? 0) - (b.variant_count ?? 0),
    render: (row: any) =>
      h(NTag, { size: "small", type: "primary" }, { default: () => String(row.variant_count ?? 0) }),
  },
  {
    title: "字段数",
    key: "field_count",
    width: 80,
    sorter: (a: any, b: any) => (a.field_count ?? 0) - (b.field_count ?? 0),
    render: (row: any) =>
      h(NTag, { size: "small", type: "info" }, { default: () => String(row.field_count ?? 0) }),
  },
  {
    title: "操作",
    key: "actions",
    width: 100,
    fixed: "right",
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
  onChange: (page: number) => {
    pagination.page = page;
  },
});

function handleSearch() {
  pagination.page = 1;
}

async function loadKinds() {
  loading.value = true;
  try {
    const res = await getCachedDatasetKinds();
    kinds.value = res.data.results ?? [];
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "查询失败");
  } finally {
    loading.value = false;
  }
}

async function handleSync() {
  syncing.value = true;
  try {
    const { syncDatasets } = await import("@/api/cache");
    const res = await syncDatasets();
    message.success(res.data.message);
    await loadKinds();
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "同步失败");
  } finally {
    syncing.value = false;
  }
}

onMounted(loadKinds);
</script>
