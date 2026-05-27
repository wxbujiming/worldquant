<template>
  <div>
    <n-h2>模拟控制台</n-h2>
    <n-p depth="3">在此提交 Alpha 代码进行模拟，或对已存在的 Alpha 运行模拟。</n-p>

    <n-card title="提交新 Alpha 模拟">
      <n-form label-placement="top">
        <n-form-item label="Alpha ID（可选）">
          <n-input
            v-model:value="form.alphaId"
            placeholder="输入已有 Alpha ID，或直接在下框粘贴代码"
          />
        </n-form-item>
        <n-form-item label="Alpha 代码">
          <n-input
            v-model:value="form.code"
            type="textarea"
            :rows="10"
            placeholder="粘贴 Alpha 公式代码..."
            :disabled="!!form.alphaId"
          />
        </n-form-item>
        <n-grid :cols="4" x-gap="12">
          <n-gi>
            <n-form-item label="Region">
              <n-select
                v-model:value="form.region"
                :options="regionOptions"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="Delay">
              <n-select v-model:value="form.delay" :options="delayOptions" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="Universe">
              <n-select
                v-model:value="form.universe"
                :options="universeOptions"
              />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="Neutralization">
              <n-select
                v-model:value="form.neutralization"
                :options="neutralOptions"
                clearable
              />
            </n-form-item>
          </n-gi>
        </n-grid>
        <n-button
          type="primary"
          @click="handleSimulate"
          :loading="simulating"
          :disabled="!form.code && !form.alphaId"
        >
          运行模拟
        </n-button>
      </n-form>
    </n-card>

    <n-card v-if="result" title="模拟结果" style="margin-top: 16px">
      <n-code :code="JSON.stringify(result, null, 2)" language="json" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useMessage } from "naive-ui";
import { simulateAlpha, filterAlphas } from "@/api/alphas";

const message = useMessage();

const simulating = ref(false);
const result = ref<any>(null);

const form = reactive({
  alphaId: "",
  code: "",
  region: "usa",
  delay: 1,
  universe: "top3000",
  neutralization: null as string | null,
});

const regionOptions = [
  { label: "USA", value: "usa" },
  { label: "Europe", value: "eur" },
  { label: "Asia", value: "asia" },
];

const delayOptions = [1, 2, 3, 4].map((v) => ({ label: `${v}`, value: v }));

const universeOptions = [
  { label: "TOP3000", value: "top3000" },
  { label: "TOP2000", value: "top2000" },
  { label: "TOP1000", value: "top1000" },
];

const neutralOptions = [
  { label: "None", value: "none" },
  { label: "Industry", value: "industry" },
  { label: "Sector", value: "sector" },
  { label: "Sub Industry", value: "subindustry" },
];

async function handleSimulate() {
  result.value = null;
  simulating.value = true;
  try {
    if (form.alphaId) {
      const res = await simulateAlpha(form.alphaId);
      result.value = res.data;
      message.success("模拟完成");
    } else {
      message.warning("暂不支持直接通过代码模拟，请先创建 Alpha 或使用已有 Alpha ID");
    }
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "模拟失败");
  } finally {
    simulating.value = false;
  }
}
</script>
