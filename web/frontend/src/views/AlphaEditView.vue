<template>
  <div v-if="loading">
    <n-spin size="large" />
  </div>
  <div v-else>
    <n-button quaternary @click="$router.back()" style="margin-bottom: 16px">
      ← 返回
    </n-button>
    <n-h2>编辑 Alpha</n-h2>

    <n-card title="属性">
      <n-form label-placement="left" label-width="120">
        <n-form-item label="名称">
          <n-input v-model:value="form.name" placeholder="Alpha name" />
        </n-form-item>
        <n-form-item label="标签">
          <n-dynamic-tags v-model:value="form.tags" />
        </n-form-item>
        <n-form-item label="颜色">
          <n-color-picker v-model:value="form.color" />
        </n-form-item>
        <n-form-item label="收藏">
          <n-switch v-model:value="form.favorite" />
        </n-form-item>
        <n-form-item label="隐藏">
          <n-switch v-model:value="form.hidden" />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" @click="handleSave" :loading="saving">
            保存
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import { getAlpha, patchAlpha } from "@/api/alphas";

const route = useRoute();
const router = useRouter();
const message = useMessage();

const loading = ref(true);
const saving = ref(false);
const form = reactive({
  name: "",
  tags: [] as string[],
  color: null as string | null,
  favorite: false,
  hidden: false,
});

async function loadAlpha() {
  try {
    const res = await getAlpha(route.params.id as string);
    const a = res.data;
    form.name = a.name || "";
    form.tags = a.tags || [];
    form.color = a.color || null;
    form.favorite = !!a.favorite;
    form.hidden = !!a.hidden;
  } catch (err: any) {
    message.error("加载失败");
  } finally {
    loading.value = false;
  }
}

async function handleSave() {
  saving.value = true;
  try {
    await patchAlpha(route.params.id as string, {
      name: form.name || undefined,
      tags: form.tags.length ? form.tags : undefined,
      color: form.color || undefined,
      favorite: form.favorite || undefined,
      hidden: form.hidden || undefined,
    });
    message.success("保存成功");
    router.back();
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "保存失败");
  } finally {
    saving.value = false;
  }
}

onMounted(loadAlpha);
</script>
