<template>
  <el-card>
    <h3 style="margin-top:0">{{ title }}</h3>
    <p style="color:#374151">{{ desc }}</p>
    <el-tag type="info">路线图阶段 {{ stage }} 实现</el-tag>
    <el-tag style="margin-left:8px">阶段1 骨架占位页</el-tag>
  </el-card>
</template>
<script setup lang="ts">
defineProps<{ title: string; desc: string; stage: number }>()
</script>
