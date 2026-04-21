# Vue 数字动效（@number-flow/vue）

> 来源：通过 lizard 从 Claude 会话蒸馏 · 2026-04-20

## 核心概念

`@number-flow/vue` 是一个 Vue 3 组件库，提供平滑的数字滚动动效（digit roll animation）。适合 KPI 卡片、实时数据面板等场景，数字变化时会有流畅的上下翻滚过渡效果。

官网：https://number-flow.barvian.me/

## 安装

```bash
npm install @number-flow/vue
```

## 基本用法

```vue
<script setup>
import NumberFlow from '@number-flow/vue'
</script>

<template>
  <NumberFlow :value="windSpeed" />
</template>
```

## 关键细节

### 拆分数值与单位后缀

数字组件只管数字部分，单位/后缀保持静态：

```vue
<!-- 风速：数字滚动，单位静态 -->
<NumberFlow :value="windSpeed" /> kt

<!-- 气温：正负号 + 数字 -->
<span>{{ temp >= 0 ? '' : '-' }}</span><NumberFlow :value="Math.abs(temp)" />°C

<!-- 气压（两位小数） -->
<NumberFlow :value="altimeter" :format="{ minimumFractionDigits: 2, maximumFractionDigits: 2 }" /> inHg
```

### 在 KPICell 组件中集成

父组件通过默认 slot 传入 `NumberFlow`，KPICell 只负责布局：

```vue
<!-- KPICell.vue：提供 slot -->
<template>
  <div class="kpi-cell">
    <slot>{{ value }}</slot>
    <span class="unit">{{ unit }}</span>
  </div>
</template>

<!-- AirportScreen.vue：使用 NumberFlow 填充 slot -->
<KPICell label="Wind">
  <NumberFlow :value="wind.speed" />
</KPICell>
```

### 格式化选项

`:format` 属性接受 `Intl.NumberFormat` 选项对象：

```vue
<NumberFlow
  :value="price"
  :format="{ style: 'currency', currency: 'USD' }"
/>
```

## 适用场景

- 实时气象数据（METAR: 风速、能见度、温度、气压）
- 仪表盘 KPI 指标
- 分数、进度数值变化

## 相关链接

- [[map-dead-reckoning-raf]] — 配套的地图平滑动画方案
