import { defineStore } from "pinia";
import { ref } from "vue";
import { login as apiLogin, logout as apiLogout, getStatus } from "@/api/auth";
import type { LoginRequest } from "@/api/auth";

export const useAuthStore = defineStore("auth", () => {
  const authenticated = ref(false);
  const email = ref("");
  const loading = ref(false);

  async function checkStatus() {
    try {
      const res = await getStatus();
      authenticated.value = res.data.authenticated;
      email.value = res.data.email ?? "";
    } catch {
      authenticated.value = false;
      email.value = "";
    }
  }

  async function login(data: LoginRequest) {
    loading.value = true;
    try {
      const res = await apiLogin(data);
      authenticated.value = true;
      email.value = res.data.email;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      await apiLogout();
    } finally {
      authenticated.value = false;
      email.value = "";
    }
  }

  return { authenticated, email, loading, checkStatus, login, logout };
});
