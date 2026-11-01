<template><div ref="el" :style="{ height: height + 'px', width: '100%' }"></div></template>
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts'
const props = defineProps<{ option: any; height?: number }>()
const el = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
function render() { if (chart) chart.setOption(props.option, true) }
onMounted(() => { chart = echarts.init(el.value!); render(); window.addEventListener('resize', onResize) })
function onResize() { chart?.resize() }
watch(() => props.option, render, { deep: true })
onBeforeUnmount(() => { window.removeEventListener('resize', onResize); chart?.dispose() })
</script>
