import { createRouter, createWebHashHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/LoginView.vue"),
  },
  {
    path: "/",
    component: () => import("@/components/AppLayout.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/views/DashboardView.vue"),
      },
      {
        path: "datasets",
        name: "Datasets",
        component: () => import("@/views/DatasetsView.vue"),
      },
      {
        path: "datasets/:id",
        name: "DatasetDetail",
        component: () => import("@/views/DatasetDetailView.vue"),
      },
      {
        path: "operators",
        name: "Operators",
        component: () => import("@/views/OperatorsView.vue"),
      },
      {
        path: "alphas",
        name: "Alphas",
        component: () => import("@/views/AlphasView.vue"),
      },
      {
        path: "alphas/:id",
        name: "AlphaDetail",
        component: () => import("@/views/AlphaDetailView.vue"),
      },
      {
        path: "alphas/:id/edit",
        name: "AlphaEdit",
        component: () => import("@/views/AlphaEditView.vue"),
      },
      {
        path: "simulate",
        name: "Simulate",
        component: () => import("@/views/SimulateView.vue"),
      },
      {
        path: "alpha-gen",
        name: "AlphaGen",
        component: () => import("@/views/AlphaGenView.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach(async (to, _from) => {
  if (to.path === "/login") return true;
  const { useAuthStore } = await import("@/stores/auth");
  const auth = useAuthStore();
  await auth.checkStatus();
  if (!auth.authenticated) {
    return { name: "Login" };
  }
  return true;
});

export default router;
