<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AppHeader from "@/components/AppHeader.vue";
import "@/assets/base.css";
</script>

<template>
  <AppHeader />

  <main>
    <RouterView />
  </main>

</template>