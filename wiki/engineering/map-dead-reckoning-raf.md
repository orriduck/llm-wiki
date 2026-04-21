# 地图标记死推算动画（requestAnimationFrame）

> 来源：通过 lizard 从 Claude 会话蒸馏 · 2026-04-20

## 核心概念

**死推算（Dead Reckoning）**：已知物体上一时刻的位置、速度、方向，利用匀速运动公式推算当前位置。用于在低频数据更新（如每 3 秒一次的 ADS-B 轮询）之间，以 60fps 的帧率平滑插值地图标记的位置。

## 问题场景

地图标记数据来源是 3 秒轮询一次的 API，若每次更新直接 `setLatLng()`，标记会"跳动"。CSS `transition` 可缓解，但对高速目标（飞机）仍不够平滑，且 transition 不感知球面坐标。

## 实现方案

### 数据结构

每个标记存储上次轮询时的基准状态：

```js
const markers = new Map() // icao24 → { marker, baseLat, baseLon, baseTime, velocity, track }
```

- `velocity`：地速（节，knots）
- `track`：航向（度，0=北，顺时针）
- `baseTime`：上次 ADS-B 数据时间戳（`Date.now()`）

### 每次轮询更新基准

```js
function updateAircraft(ac) {
  const entry = markers.get(ac.icao24)
  if (entry) {
    // 更新基准，不直接移动标记
    entry.baseLat = ac.lat
    entry.baseLon = ac.lon
    entry.velocity = ac.gs   // ground speed in knots
    entry.track = ac.track
    entry.baseTime = Date.now()
  } else {
    // 首次创建标记
    const marker = L.marker([ac.lat, ac.lon], { icon: makeAcIcon(ac) })
    markers.set(ac.icao24, { marker, baseLat: ac.lat, baseLon: ac.lon,
                              baseTime: Date.now(), velocity: ac.gs, track: ac.track })
  }
}
```

### RAF 推算循环

```js
function animateLoop() {
  const now = Date.now()
  for (const [, entry] of markers) {
    const { marker, baseLat, baseLon, baseTime, velocity, track } = entry
    if (!velocity || velocity < 30) continue  // 低速目标不推算

    const dt = (now - baseTime) / 1000  // 秒
    const distKm = (velocity * 1.852) * (dt / 3600)  // 节 → km/h → km

    // 球面坐标推算（近似平面）
    const dLat = distKm / 111.32 * Math.cos(track * Math.PI / 180)
    const dLon = distKm / (111.32 * Math.cos(baseLat * Math.PI / 180)) * Math.sin(track * Math.PI / 180)

    marker.setLatLng([baseLat + dLat, baseLon + dLon])
  }
  rafId = requestAnimationFrame(animateLoop)
}

// 启动/停止
let rafId = requestAnimationFrame(animateLoop)
onUnmounted(() => cancelAnimationFrame(rafId))
```

## 关键细节

### 速度阈值：30 节（kt）

- **≥ 30 kt**：启用死推算（巡航飞机），图标显示为方向箭头
- **< 30 kt**：仅在轮询时更新（地面/滑行），图标显示为圆点

此阈值也用于区分图标样式，保持逻辑一致。

### 误差累积控制

每次 ADS-B 轮询到达，`baseLat/baseLon/baseTime` 重置为权威数据，推算误差归零，不会累积漂移。

### CSS transition vs RAF 死推算

| 方案 | 优点 | 缺点 |
|------|------|------|
| CSS transition | 简单、无 JS 开销 | 不感知球面、过渡时间固定 |
| RAF 死推算 | 物理准确、60fps 平滑 | 需要速度/方向数据 |

## 根据速度切换图标

```js
function makeAcIcon(ac) {
  const showArrow = ac.gs >= 30 && !ac.onGround
  if (!showArrow) {
    // 低速：橙色圆点
    return L.divIcon({ html: `<svg width="10" height="10">
      <circle cx="5" cy="5" r="3.5" fill="#ffb347"/>
    </svg>` })
  }
  // 高速：方向箭头（根据 track 旋转）
  return L.divIcon({ html: `<svg ...transform="rotate(${ac.track})"...>...</svg>` })
}
```

## 相关链接

- [[vue-number-flow]] — 配套的数字动效方案
