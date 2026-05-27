<template>
  <div>
    <n-h2>仪表盘</n-h2>
    <n-p depth="3">欢迎使用 WorldQuant Brain Web 界面</n-p>
    <n-grid :cols="3" x-gap="16" y-gap="16" style="margin-top: 16px">
      <n-gi>
        <n-card title="Alpha" hoverable>
          <n-statistic :value="'—'">
            <template #suffix> 个 </template>
          </n-statistic>
          <template #footer> 进入 Alpha 页面管理策略 </template>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card title="数据集" hoverable>
          <n-statistic :value="'—'">
            <template #suffix> 个 </template>
          </n-statistic>
          <template #footer> 浏览数据字段和算子 </template>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card title="模拟状态" hoverable>
          <n-statistic :value="'—'">
            <template #suffix> 次 </template>
          </n-statistic>
          <template #footer> 在模拟页面提交运行 </template>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>
