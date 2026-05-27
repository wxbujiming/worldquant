<template>
  <div v-if="loading">
    <n-spin size="large" />
  </div>
  <div v-else-if="alpha">
    <n-button quaternary @click="$router.back()" style="margin-bottom: 16px">
      ← 返回
    </n-button>

    <n-h2>{{ alpha.name || alpha.id }}</n-h2>

    <n-tabs type="line" animated>
      <n-tab-pane name="info" tab="基本信息">
        <n-descriptions label-placement="left" bordered :column="2">
          <n-descriptions-item label="ID">{{ alpha.id }}</n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="statusColor" size="small">{{ alpha.status }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="名称">{{ alpha.name || "—" }}</n-descriptions-item>
          <n-descriptions-item label="区域">{{ alpha.settings?.region || "—" }}</n-descriptions-item>
          <n-descriptions-item label="Universe">{{ alpha.settings?.universe || "—" }}</n-descriptions-item>
          <n-descriptions-item label="Delay">{{ alpha.settings?.delay || "—" }}</n-descriptions-item>
          <n-descriptions-item label="Neutralization">{{ alpha.settings?.neutralization || "—" }}</n-descriptions-item>
          <n-descriptions-item label="Decay">{{ alpha.settings?.decay || "—" }}</n-descriptions-item>
          <n-descriptions-item label="Truncation">{{ alpha.settings?.truncation || "—" }}</n-descriptions-item>
          <n-descriptions-item label="Unit Handling">{{ alpha.settings?.unitHandling || "—" }}</n-descriptions-item>
          <n-descriptions-item label="Nan Handling">{{ alpha.settings?.nanHandling || "—" }}</n-descriptions-item>
          <n-descriptions-item label="Color">
            <n-tag v-if="alpha.color" :color="{ color: alpha.color }" size="small">{{ alpha.color }}</n-tag>
            <span v-else>—</span>
          </n-descriptions-item>
        </n-descriptions>
      </n-tab-pane>

      <n-tab-pane name="code" tab="代码">
        <n-code :code="alpha.regular || alpha.code || 'No code available'" language="python" />
      </n-tab-pane>

      <n-tab-pane name="results" tab="模拟结果">
        <n-grid :cols="4" x-gap="16" y-gap="16">
          <n-gi>
            <n-statistic label="Sharpe" :value="alpha.is?.sharpe?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Returns" :value="alpha.is?.returns?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Fitness" :value="alpha.is?.fitness?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Drawdown" :value="alpha.is?.drawdown?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Turnover" :value="alpha.is?.turnover?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="PnL" :value="alpha.is?.pnl?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Margin" :value="alpha.is?.margin?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Long/Short" :value="alpha.is?.longCount != null ? `${alpha.is.longCount}/${alpha.is.shortCount}` : '—'" />
          </n-gi>
        </n-grid>
        <n-divider />
        <n-h3>Out-of-Sample</n-h3>
        <n-grid :cols="4" x-gap="16" y-gap="16">
          <n-gi>
            <n-statistic label="Sharpe (60)" :value="alpha.os?.sharpe60?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Sharpe (125)" :value="alpha.os?.sharpe125?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Sharpe (250)" :value="alpha.os?.sharpe250?.toFixed(4) ?? '—'" />
          </n-gi>
          <n-gi>
            <n-statistic label="Sharpe (500)" :value="alpha.os?.sharpe500?.toFixed(4) ?? '—'" />
          </n-gi>
        </n-grid>
      </n-tab-pane>
    </n-tabs>

    <n-space style="margin-top: 24px">
      <n-button type="primary" @click="handleSimulate" :loading="simulating">
        模拟
      </n-button>
      <n-button @click="handleCheck" :loading="checking">检查</n-button>
      <n-button type="success" @click="handleSubmit" :loading="submitting">
        提交比赛
      </n-button>
      <n-button @click="handleEdit">编辑</n-button>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import { getAlpha, simulateAlpha, checkAlpha, submitAlpha } from "@/api/alphas";

const route = useRoute();
const router = useRouter();
const message = useMessage();

const loading = ref(true);
const alpha = ref<any>(null);
const simulating = ref(false);
const checking = ref(false);
const submitting = ref(false);

const statusColor = computed(() => {
  const map: Record<string, string> = {
    PASSED: "success",
    FAILED: "error",
    INPROGRESS: "warning",
    SUBMITTED: "info",
  };
  return map[alpha.value?.status] || "default";
});

async function loadAlpha() {
  const id = route.params.id as string;
  try {
    const res = await getAlpha(id);
    alpha.value = res.data;
  } catch (err: any) {
    message.error("加载 Alpha 失败");
  } finally {
    loading.value = false;
  }
}

async function handleSimulate() {
  simulating.value = true;
  try {
    const res = await simulateAlpha(route.params.id as string);
    message.success("模拟完成");
    alpha.value = res.data;
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "模拟失败");
  } finally {
    simulating.value = false;
  }
}

async function handleCheck() {
  checking.value = true;
  try {
    const res = await checkAlpha(route.params.id as string);
    message.success("检查完成");
    alpha.value = res.data;
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "检查失败");
  } finally {
    checking.value = false;
  }
}

async function handleSubmit() {
  submitting.value = true;
  try {
    await submitAlpha(route.params.id as string);
    message.success("提交成功");
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "提交失败");
  } finally {
    submitting.value = false;
  }
}

function handleEdit() {
  router.push(`/alphas/${route.params.id}/edit`);
}

onMounted(loadAlpha);
</script>
