<template>
  <n-layout class="layout" has-sider position="absolute">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :collapsed="collapsed"
      :native-scrollbar="false"
      class="sider"
    >
      <div class="sider-header" @click="collapsed = !collapsed">
        <n-icon size="28" style="color: #2d8cf0">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </n-icon>
        <span v-show="!collapsed" class="sider-title">WB Web</span>
      </div>
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="onMenuSelect"
      />
      <template #footer>
        <div class="sider-footer">
          <n-ellipsis v-if="!collapsed && auth.email" style="max-width: 160px">
            {{ auth.email }}
          </n-ellipsis>
          <n-button
            quaternary
            circle
            size="small"
            @click="handleLogout"
            :title="'Logout'"
          >
            <n-icon><svg viewBox="0 0 24 24" fill="currentColor"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg></n-icon>
          </n-button>
        </div>
      </template>
    </n-layout-sider>
    <n-layout>
      <n-layout-content class="content" :native-scrollbar="false">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { h, ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import type { MenuOption } from "naive-ui";
import { NIcon } from "naive-ui";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const collapsed = ref(false);

function renderSvg(path: string, viewBox = "0 0 24 24") {
  return () =>
    h(NIcon, null, {
      default: () =>
        h("svg", { viewBox, fill: "currentColor" }, [h("path", { d: path })]),
    });
}

const menuOptions: MenuOption[] = [
  {
    label: "仪表盘",
    key: "dashboard",
    icon: renderSvg("M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"),
  },
  {
    label: "数据集",
    key: "datasets",
    icon: renderSvg("M4 8h4V4H4v4zm6 12h4v-4h-4v4zm-6 0h4v-4H4v4zm0-6h4v-4H4v4zm6 0h4v-4h-4v4zm6-10v4h4V4h-4zm-6 4h4V4h-4v4zm6 6h4v-4h-4v4zm0 6h4v-4h-4v4z"),
  },
  {
    label: "算子",
    key: "operators",
    icon: renderSvg("M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"),
  },
  {
    label: "Alpha",
    key: "alphas",
    icon: renderSvg("M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm7 13H5v-.23c0-.62.28-1.2.76-1.58C7.47 15.82 9.64 15 12 15s4.53.82 6.24 2.19c.48.38.76.97.76 1.58V19z"),
  },
  {
    label: "模拟",
    key: "simulate",
    icon: renderSvg("M8 5v14l11-7z"),
  },
];

const activeKey = computed(() => {
  const segments = route.path.split("/");
  return segments[1] || "dashboard";
});

function onMenuSelect(key: string) {
  router.push({ name: capitalize(key) });
}

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

async function handleLogout() {
  await auth.logout();
  router.push("/login");
}

onMounted(() => {
  auth.checkStatus();
});
</script>

<style scoped>
.layout {
  height: 100%;
}
.sider {
  background-color: #fafafa;
}
.sider-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  cursor: pointer;
  user-select: none;
}
.sider-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}
.sider-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  color: #888;
  font-size: 12px;
}
.content {
  padding: 24px;
  background-color: #fff;
  min-height: 100%;
}
</style>
