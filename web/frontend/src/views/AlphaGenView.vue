<template>
  <div>
    <n-h2>Alpha 公式生成器</n-h2>
    <n-p depth="3">三阶段递进生成：基础表达式 → 组合表达式 → 最终归一化</n-p>

    <n-tabs v-model:value="tabValue" type="line" animated style="margin-bottom: 16px">
      <!-- ===== Tab 0: 基础配置 ===== -->
      <n-tab-pane name="config" tab="基础配置">
        <n-card>
          <n-grid :cols="4" x-gap="12" y-gap="12">
            <n-gi>
              <n-form-item label="区域 (Region)">
                <n-select v-model:value="config.region" :options="regionOptions" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="延迟 (Delay)">
                <n-select v-model:value="config.delay" :options="delayOptions" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="股票池 (Universe)">
                <n-select v-model:value="config.universe" :options="universeOptions" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="资产类型 (Instrument Type)">
                <n-select v-model:value="config.instrument_type" :options="instTypeOptions" />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="中性化 (Neutralization)">
                <n-select v-model:value="config.neutralization" :options="neutralOptions" clearable />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="截断 (Truncation)">
                <n-input-number v-model:value="config.truncation" :min="0" :max="1" :step="0.01" clearable />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="衰减平滑 (Decay)">
                <n-input-number v-model:value="config.decay" :min="0" :max="10" clearable />
              </n-form-item>
            </n-gi>
            <n-gi>
              <n-form-item label="正交化 (Pasteurization)">
                <n-select v-model:value="config.pasteurization" :options="pasteurOptions" clearable />
              </n-form-item>
            </n-gi>
          </n-grid>
          <n-form-item label="选择数据集 (Datasets)">
            <n-select
              v-model:value="selectedDatasetIds"
              multiple
              filterable
              :options="datasetOptions"
              placeholder="选择一个或多个数据集"
            />
          </n-form-item>
        </n-card>

        <n-card title="参数与指标说明" style="margin-top: 16px" size="small">
          <n-h5 prefix="bar">表达式示例说明</n-h5>
          <n-table size="small" :bordered="false" :single-line="false">
            <thead>
              <tr><th>表达式</th><th>说明</th></tr>
            </thead>
            <tbody>
              <tr><td><n-code>returns</n-code></td><td>代表收益信号，如股票每日的回报率</td></tr>
              <tr><td><n-code>-returns</n-code></td><td>将收益信号取反的量化操作，用于寻找可能被市场过度低估或高估的股票</td></tr>
              <tr><td><n-code>rank(-returns)</n-code></td><td>反转策略信号，通过先取负再排名的方式，使最近跌幅最大的股票获得最高的排名，从而在策略中倾向于做多这些股票</td></tr>
            </tbody>
          </n-table>

          <n-h5 prefix="bar" style="margin-top: 16px">回测指标说明</n-h5>
          <n-table size="small" :bordered="false" :single-line="false">
            <thead>
              <tr><th>指标</th><th>说明</th></tr>
            </thead>
            <tbody>
              <tr><td>PnL Graph</td><td>回测收益图，Alpha 策略最直观核心的工具。根据曲线的形状、趋势、波动和平滑度，综合判断策略的质量、健壮性和未来表现潜力</td></tr>
              <tr><td>Sharpe</td><td>风险调整后回报的衡量标准，越高越好。Sharpe = 平均年化收益 / 年化标准收益偏差。一般 &gt;1.5，优秀 &gt;2</td></tr>
              <tr><td>Turnover</td><td>换手率，指回测中股票买卖的频繁程度。理想范围 5% ~ 20%，警戒线超过 70%</td></tr>
              <tr><td>Returns</td><td>回测期间所赚取的金额，通常以百分比表达。负值表示亏损，越大越好</td></tr>
              <tr><td>Drawdown</td><td>回撤率，PnL 最高点到最低点的最大跌幅，百分比表示，越小越好</td></tr>
              <tr><td>Margin</td><td>衡量交易效率和盈利能力的核心指标，通常以万分数表示。地区门槛：USA&gt;10 EUR&gt;10 GLB&gt;15 ASI&gt;15 IND&gt;15</td></tr>
              <tr><td>Fitness</td><td>适应度 = Sharpe × √(Abs(Returns) / Max(Turnover, 0.125))。评估标准：1.0~1.5 Average（达标）；1.5~2.0 Good（良好）；2.0~2.5 Excellent（优秀）；2.5~∞ Spectacular（顶级）</td></tr>
            </tbody>
          </n-table>

          <n-h5 prefix="bar" style="margin-top: 16px">参数配置建议</n-h5>
          <n-table size="small" :bordered="false" :single-line="false">
            <thead>
              <tr><th>参数</th><th>说明与建议</th></tr>
            </thead>
            <tbody>
              <tr><td>截断 (Truncation)</td><td>限制单只股票的最大权重占比。一般推荐 0.05 ~ 0.1（5%~10%）。对 TOP3000 宇宙，常用 0.008 ~ 0.01（0.8%~1%）</td></tr>
              <tr><td>正交化 (Pasteurization)</td><td>清除计算过程中的无穷大/无用值。推荐配置：开启 (ON)</td></tr>
            </tbody>
          </n-table>

          <n-h5 prefix="bar" style="margin-top: 16px">Alpha 质量评估总结</n-h5>
          <n-text>Sharpe 越大、Drawdown 越小、Turnover 越小、Returns 越大、Margin 越大、Fitness 越大，Alpha 质量越高。</n-text>
        </n-card>
      </n-tab-pane>

      <!-- ===== Tab 1: Stage 1 ===== -->
      <n-tab-pane name="stage1" tab="Stage 1 基础表达式">
        <n-card>
          <n-space vertical>
            <n-space align="center">
              <n-text>生成数量：</n-text>
              <n-input-number v-model:value="stage1Count" :min="1" :max="100" style="width: 120px" />
              <n-button type="primary" @click="runStage1" :loading="loadingStage1">
                生成 Stage 1
              </n-button>
            </n-space>
            <n-text v-if="stage1Error" type="error">{{ stage1Error }}</n-text>
          </n-space>
          <n-data-table
            v-if="stage1Results.length > 0"
            :columns="stage1Columns"
            :data="stage1Results"
            :loading="loadingStage1"
            size="small"
            :bordered="false"
            :single-line="false"
            :row-key="(row: any) => row.id"
            :scroll-x="900"
            style="margin-top: 12px"
          />
        </n-card>
      </n-tab-pane>

      <!-- ===== Tab 2: Stage 2 ===== -->
      <n-tab-pane name="stage2" tab="Stage 2 组合表达式">
        <n-card>
          <n-space vertical>
            <n-space align="center">
              <n-text>生成数量：</n-text>
              <n-input-number v-model:value="stage2Count" :min="1" :max="100" style="width: 120px" />
              <n-button type="primary" @click="runStage2" :loading="loadingStage2">
                生成 Stage 2
              </n-button>
            </n-space>
            <n-text v-if="stage2Error" type="error">{{ stage2Error }}</n-text>
          </n-space>
          <n-data-table
            v-if="stage2Results.length > 0"
            :columns="stage2Columns"
            :data="stage2Results"
            :loading="loadingStage2"
            size="small"
            :bordered="false"
            :single-line="false"
            :row-key="(row: any) => row.id"
            :scroll-x="900"
            style="margin-top: 12px"
          />
        </n-card>
      </n-tab-pane>

      <!-- ===== Tab 3: Stage 3 ===== -->
      <n-tab-pane name="stage3" tab="Stage 3 最终归一化">
        <n-card style="margin-bottom: 16px">
          <n-space vertical>
            <n-space align="center">
              <n-text>生成数量：</n-text>
              <n-input-number v-model:value="stage3Count" :min="1" :max="50" style="width: 120px" />
              <n-button type="primary" @click="runStage3" :loading="loadingStage3">
                生成 Stage 3
              </n-button>
            </n-space>
            <n-text v-if="stage3Error" type="error">{{ stage3Error }}</n-text>
          </n-space>
          <n-data-table
            v-if="stage3Results.length > 0"
            :columns="stage3Columns"
            :data="stage3Results"
            :loading="loadingStage3"
            size="small"
            :bordered="false"
            :single-line="false"
            :row-key="(row: any) => row.id"
            :scroll-x="900"
            style="margin-top: 12px"
          />
        </n-card>

        <n-card v-if="stage3Results.length > 0" title="最终 Alpha 公式">
          <n-list>
            <n-list-item v-for="(expr, idx) in stage3Results" :key="expr.id">
              <n-thing :title="`#${idx + 1}  ${expr.operator}`">
                <template #description>
                  <n-code :code="expr.formula" language="text" />
                </template>
                <template #extra>
                  <n-space>
                    <n-tag size="small">{{ expr.category }}</n-tag>
                    <n-button size="tiny" @click="copyFormula(expr.formula)">复制</n-button>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
        </n-card>
      </n-tab-pane>
    </n-tabs>

    <!-- 模拟结果抽屉 -->
    <n-drawer v-model:show="showDrawer" :width="600" placement="right">
      <n-drawer-content title="模拟结果" closable>
        <n-spin :show="simulatingLoading">
          <template v-if="simulateResult">
            <n-h5 prefix="bar">模拟 Alpha: {{ simulateFormulaText }}</n-h5>
            <n-code :code="JSON.stringify(simulateResult, null, 2)" language="json" />
          </template>
          <n-text v-else depth="3">暂无结果</n-text>
        </n-spin>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from "vue";
import { useMessage } from "naive-ui";
import type { DataTableColumn } from "naive-ui";
import { NTag, NButton, NSpace } from "naive-ui";
import { getCachedDatasets } from "@/api/cache";
import {
  generateStage1,
  generateStage2,
  generateStage3,
  simulateFormula,
  type Stage1Expression,
  type Stage2Expression,
  type Stage3Expression,
  type GenConfig,
} from "@/api/generator";

const message = useMessage();

// ── Tab 控制 ──
const tabValue = ref("config");

// ── 基础配置 ──
const config = reactive<GenConfig>({
  region: "USA",
  delay: 1,
  universe: "TOP3000",
  instrument_type: "EQUITY",
  neutralization: "SUBINDUSTRY",
  truncation: 0.08,
  decay: 5,
  pasteurization: "ON",
});

const selectedDatasetIds = ref<string[]>([]);
const datasetOptions = ref<{ label: string; value: string }[]>([]);

const regionOptions = [
  { label: "美国 (USA)", value: "USA" },
  { label: "欧洲 (EUR)", value: "EUR" },
  { label: "亚洲 (ASIA)", value: "ASIA" },
  { label: "全球 (GLOBAL)", value: "GLOBAL" },
];
const delayOptions = [0, 1, 2, 3, 4].map((v) => ({ label: `${v}`, value: v }));
const universeOptions = [
  { label: "TOP3000", value: "TOP3000" },
  { label: "TOP2000", value: "TOP2000" },
  { label: "TOP1000", value: "TOP1000" },
  { label: "TOP500", value: "TOP500" },
  { label: "TOP200", value: "TOP200" },
  { label: "TOPSP500", value: "TOPSP500" },
];
const instTypeOptions = [{ label: "EQUITY", value: "EQUITY" }];
const neutralOptions = [
  { label: "无", value: "none" },
  { label: "Industry", value: "industry" },
  { label: "Sector", value: "sector" },
  { label: "Sub Industry", value: "subindustry" },
];
const pasteurOptions = [
  { label: "开 (ON)", value: "ON" },
  { label: "关 (OFF)", value: "OFF" },
];

// ── Stage 1 ──
const stage1Count = ref(20);
const loadingStage1 = ref(false);
const stage1Error = ref("");
const stage1Results = ref<Stage1Expression[]>([]);

// ── Stage 2 ──
const stage2Count = ref(15);
const loadingStage2 = ref(false);
const stage2Error = ref("");
const stage2Results = ref<Stage2Expression[]>([]);

// ── Stage 3 ──
const stage3Count = ref(10);
const loadingStage3 = ref(false);
const stage3Error = ref("");
const stage3Results = ref<Stage3Expression[]>([]);

// ── 模拟 ──
const simulatingId = ref<string | null>(null);
const showDrawer = ref(false);
const simulateResult = ref<any>(null);
const simulateFormulaText = ref("");
const simulatingLoading = ref(false);

const stage1Columns: DataTableColumn[] = [
  { title: "#", key: "id", width: 80 },
  { title: "公式", key: "formula", minWidth: 260, ellipsis: { tooltip: true },
    render: (row: any) => h("code", { style: "font-size:12px" }, row.formula) },
  { title: "算子", key: "operator", width: 100 },
  { title: "字段", key: "field", width: 110 },
  { title: "分类", key: "category", width: 100,
    render: (row: any) => h(NTag, { size: "tiny" }, { default: () => row.category }) },
  {
    title: "操作", key: "actions", width: 70, fixed: "right",
    render: (row: any) => h(NButton, {
      size: "tiny", ghost: true, type: "primary",
      loading: simulatingId.value === row.id,
      disabled: !!simulatingId.value,
      onClick: () => handleSimulate(row.formula, row.id),
    }, { default: () => "模拟" }),
  },
];

const stage2Columns: DataTableColumn[] = [
  { title: "#", key: "id", width: 80 },
  { title: "公式", key: "formula", minWidth: 300, ellipsis: { tooltip: true },
    render: (row: any) => h("code", { style: "font-size:12px" }, row.formula) },
  { title: "算子", key: "operator", width: 110 },
  { title: "分类", key: "category", width: 100,
    render: (row: any) => h(NTag, { size: "tiny" }, { default: () => row.category }) },
  { title: "来源", key: "composed_from", width: 110,
    render: (row: any) => (row.composed_from as string[]).join(", ") },
  {
    title: "操作", key: "actions", width: 70, fixed: "right",
    render: (row: any) => h(NButton, {
      size: "tiny", ghost: true, type: "primary",
      loading: simulatingId.value === row.id,
      disabled: !!simulatingId.value,
      onClick: () => handleSimulate(row.formula, row.id),
    }, { default: () => "模拟" }),
  },
];

const stage3Columns: DataTableColumn[] = [
  { title: "#", key: "id", width: 80 },
  { title: "最终公式", key: "formula", minWidth: 340, ellipsis: { tooltip: true },
    render: (row: any) => h("code", { style: "font-size:12px" }, row.formula) },
  { title: "算子", key: "operator", width: 120 },
  { title: "分类", key: "category", width: 100,
    render: (row: any) => h(NTag, { size: "tiny" }, { default: () => row.category }) },
  {
    title: "操作", key: "actions", width: 100, fixed: "right",
    render: (row: any) => h(NSpace, null, [
      h(NButton, {
        size: "tiny", ghost: true, type: "primary",
        loading: simulatingId.value === row.id,
        disabled: !!simulatingId.value,
        onClick: () => handleSimulate(row.formula, row.id),
      }, { default: () => "模拟" }),
      h(NButton, {
        size: "tiny", ghost: true, type: "default",
        onClick: () => copyFormula(row.formula),
      }, { default: () => "复制" }),
    ]),
  },
];

// ── 方法 ──

async function runStage1() {
  if (selectedDatasetIds.value.length === 0) {
    message.warning("请先在「基础配置」中选择数据集");
    return;
  }
  loadingStage1.value = true;
  stage1Error.value = "";
  try {
    const res = await generateStage1({
      config: { ...config },
      dataset_ids: selectedDatasetIds.value,
      count: stage1Count.value,
    });
    stage1Results.value = res.data.expressions ?? [];
    message.success(`Stage 1 生成完成：${stage1Results.value.length} 个表达式`);
  } catch (err: any) {
    stage1Error.value = err?.response?.data?.detail || "生成失败";
    message.error(stage1Error.value);
  } finally {
    loadingStage1.value = false;
  }
}

async function runStage2() {
  if (stage1Results.value.length === 0) {
    message.warning("请先生成 Stage 1");
    return;
  }
  loadingStage2.value = true;
  stage2Error.value = "";
  try {
    const res = await generateStage2({
      input_expressions: stage1Results.value,
      count: stage2Count.value,
    });
    stage2Results.value = res.data.expressions ?? [];
    message.success(`Stage 2 生成完成：${stage2Results.value.length} 个表达式`);
  } catch (err: any) {
    stage2Error.value = err?.response?.data?.detail || "生成失败";
    message.error(stage2Error.value);
  } finally {
    loadingStage2.value = false;
  }
}

async function runStage3() {
  if (stage2Results.value.length === 0) {
    message.warning("请先生成 Stage 2");
    return;
  }
  loadingStage3.value = true;
  stage3Error.value = "";
  try {
    const res = await generateStage3({
      input_expressions: stage2Results.value,
      count: stage3Count.value,
    });
    stage3Results.value = res.data.expressions ?? [];
    message.success(`Stage 3 生成完成：${stage3Results.value.length} 个公式`);
  } catch (err: any) {
    stage3Error.value = err?.response?.data?.detail || "生成失败";
    message.error(stage3Error.value);
  } finally {
    loadingStage3.value = false;
  }
}

async function handleSimulate(formula: string, id: string) {
  simulatingId.value = id;
  simulateResult.value = null;
  simulateFormulaText.value = formula;
  showDrawer.value = true;
  simulatingLoading.value = true;
  try {
    const res = await simulateFormula(formula, config);
    simulateResult.value = res.data;
    message.success("模拟完成");
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "模拟失败");
  } finally {
    simulatingId.value = null;
    simulatingLoading.value = false;
  }
}

async function copyFormula(formula: string) {
  try {
    await navigator.clipboard.writeText(formula);
    message.success("已复制到剪贴板");
  } catch {
    message.error("复制失败");
  }
}

// ── 初始化 ──
onMounted(async () => {
  try {
    const res = await getCachedDatasets();
    const items: any[] = res.data.results ?? [];
    const seen = new Set<string>();
    for (const ds of items) {
      const name = ds.name || ds.id;
      if (name && !seen.has(name)) {
        seen.add(name);
        datasetOptions.value.push({ label: `${name} (${ds.region})`, value: ds.id });
      }
    }
  } catch {
    message.error("加载数据集列表失败");
  }
});
</script>
