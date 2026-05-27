<template>
  <div class="login-container">
    <n-card class="login-card" title="WorldQuant Brain" size="large">
      <template #header-extra>
        <n-icon size="28" color="#2d8cf0">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </n-icon>
      </template>
      <n-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-placement="top"
        label-width="auto"
        @submit.prevent="handleLogin"
      >
        <n-form-item label="Email" path="email">
          <n-input
            v-model:value="form.email"
            placeholder="your@email.com"
            :disabled="loading"
          />
        </n-form-item>
        <n-form-item label="Password" path="password">
          <n-input
            v-model:value="form.password"
            type="password"
            show-password-on="click"
            placeholder="******"
            :disabled="loading"
          />
        </n-form-item>
        <n-button
          attr-type="submit"
          type="primary"
          block
          :loading="loading"
          :disabled="loading"
        >
          登录
        </n-button>
        <n-button
          v-if="hasCredentials"
          block
          dashed
          style="margin-top: 8px"
          :loading="loading"
          @click="handleAutoLogin"
        >
          使用配置文件中的账号登录
        </n-button>
      </n-form>
      <template #footer>
        <n-text depth="3" style="font-size: 12px">
          登录后即可访问 WorldQuant Brain 平台数据
        </n-text>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useMessage } from "naive-ui";
import type { FormInst, FormRules } from "naive-ui";
import { useAuthStore } from "@/stores/auth";
import { getStatus } from "@/api/auth";

const router = useRouter();
const message = useMessage();
const auth = useAuthStore();
const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const hasCredentials = ref(false);

const form = reactive({
  email: "",
  password: "",
});

const rules: FormRules = {
  email: [{ required: true, message: "请输入邮箱", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

async function handleLogin() {
  loading.value = true;
  try {
    await auth.login({ email: form.email, password: form.password });
    message.success("登录成功");
    router.push("/");
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "登录失败");
  } finally {
    loading.value = false;
  }
}

async function handleAutoLogin() {
  loading.value = true;
  try {
    const { loginWithEnv } = await import("@/api/auth");
    const res = await loginWithEnv();
    auth.authenticated = true;
    auth.email = res.data.email;
    message.success("登录成功");
    router.push("/");
  } catch (err: any) {
    message.error(err?.response?.data?.detail || "登录失败");
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  try {
    const res = await getStatus();
    if (res.data.authenticated) {
      auth.authenticated = true;
      auth.email = res.data.email || "";
      router.push("/");
    }
    hasCredentials.value = !!res.data.has_credentials;
  } catch {
    // ignore
  }
});
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: linear-gradient(135deg, #e8edf5 0%, #f5f7fa 100%);
}
.login-card {
  width: 400px;
}
</style>
