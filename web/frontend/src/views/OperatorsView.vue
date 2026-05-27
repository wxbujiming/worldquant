<template>
  <div>
    <n-h2>算子浏览器</n-h2>
    <n-card style="margin-bottom: 16px">
      <n-input
        v-model:value="searchText"
        placeholder="搜索算子..."
        clearable
        @input="filterOperators"
      />
    </n-card>

    <n-data-table
      :columns="columns"
      :data="filtered"
      :loading="loading"
      :bordered="false"
      :single-line="false"
      size="small"
      :pagination="{
        pageSize: 50,
      }"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { searchOperators } from "@/api/operators";

const message = useMessage();
const loading = ref(true);
const operators = ref<any[]>([]);
const filtered = ref<any[]>([]);
const searchText = ref("");

const columns: DataTableColumn[] = [
  { title: "名称", key: "name", width: 200 },
  { title: "说明", key: "description", ellipsis: { tooltip: true } },
  { title: "类型", key: "type", width: 100 },
  { title: "分类", key: "category", width: 100 },
];

function filterOperators() {
  const t = searchText.value.toLowerCase();
  if (!t) {
    filtered.value = operators.value;
  } else {
    filtered.value = operators.value.filter(
      (o) =>
        (o.name && o.name.toLowerCase().includes(t)) ||
        (o.description && o.description.toLowerCase().includes(t)) ||
        (o.category && o.category.toLowerCase().includes(t))
    );
  }
}

onMounted(async () => {
  try {
    const res = await searchOperators();
    const data = res.data;
    operators.value = data.results ?? data.operators ?? data;
    filtered.value = operators.value;
  } catch (err: any) {
    message.error("加载算子失败");
  } finally {
    loading.value = false;
  }
});
</script>
