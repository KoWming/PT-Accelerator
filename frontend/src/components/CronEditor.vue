<template>
  <div class="cron-editor h-100">
    <div class="card h-100 border-0 shadow-none bg-transparent">
      <div class="card-body px-0 pt-0 pb-0 d-flex flex-column overflow-hidden">
        <!-- Sentence Style Navigation -->
        <div class="d-flex flex-nowrap align-items-center justify-content-center gap-1 p-2 rounded border mb-3 overflow-auto flex-shrink-0 nav-container" style="scrollbar-width: none; -ms-overflow-style: none;">
          <span class="text-muted small text-nowrap">每</span>
          
          <!-- Month -->
          <div class="btn-group">
            <button 
              type="button"
              class="badge-btn btn btn-xs rounded-pill px-2"
              :class="activeTab === 'month' ? 'btn-primary' : 'btn-primary-soft'"
              @click.stop="toggleTab('month')"
            >
              {{ getBadgeText('month') }}
              <i v-if="state.month.type !== 'every'" class="bi bi-x ms-1" @click.stop="resetField('month')"></i>
            </button>
          </div>

          <span class="text-muted small text-nowrap">的</span>

          <!-- Day -->
          <div class="btn-group">
            <button 
              type="button"
              class="badge-btn btn btn-xs rounded-pill px-2"
              :class="activeTab === 'day' ? 'btn-primary' : 'btn-primary-soft'"
              @click.stop="toggleTab('day')"
            >
              {{ getBadgeText('day') }}
              <i v-if="state.day.type !== 'every'" class="bi bi-x ms-1" @click.stop="resetField('day')"></i>
            </button>
          </div>

          <span class="text-muted small text-nowrap">和</span>

          <!-- Week -->
          <div class="btn-group">
            <button 
              type="button"
              class="badge-btn btn btn-xs rounded-pill px-2"
              :class="activeTab === 'week' ? 'btn-primary' : 'btn-primary-soft'"
              @click.stop="toggleTab('week')"
            >
              {{ getBadgeText('week') }}
              <i v-if="state.week.type !== 'every'" class="bi bi-x ms-1" @click.stop="resetField('week')"></i>
            </button>
          </div>

          <span class="text-muted small text-nowrap">的</span>

          <!-- Hour -->
          <div class="btn-group">
            <button 
              type="button"
              class="badge-btn btn btn-xs rounded-pill px-2"
              :class="activeTab === 'hour' ? 'btn-primary' : 'btn-primary-soft'"
              @click.stop="toggleTab('hour')"
            >
              {{ getBadgeText('hour') }}
              <i v-if="state.hour.type !== 'every'" class="bi bi-x ms-1" @click.stop="resetField('hour')"></i>
            </button>
          </div>

          <span class="text-muted small text-nowrap">:</span>

          <!-- Minute -->
          <div class="btn-group">
            <button 
              type="button"
              class="badge-btn btn btn-xs rounded-pill px-2"
              :class="activeTab === 'minute' ? 'btn-primary' : 'btn-primary-soft'"
              @click.stop="toggleTab('minute')"
            >
              {{ getBadgeText('minute') }}
              <i v-if="state.minute.type !== 'every'" class="bi bi-x ms-1" @click.stop="resetField('minute')"></i>
            </button>
          </div>
        </div>

        <!-- Expandable Editor Panel -->
        <div v-if="activeTab" class="tab-content border p-3 rounded shadow-sm flex-grow-1 overflow-auto editor-panel">
          <div class="tab-pane fade show active">
            <!-- Type Selection -->
            <div class="d-flex flex-column gap-2">
              
              <!-- Type: Every -->
              <div class="form-check">
                <input class="form-check-input" type="radio" :name="activeTab + '-type'" :id="activeTab + '-every'" value="every" v-model="currentVal.type">
                <label class="form-check-label" :for="activeTab + '-every'">
                  每{{ tabLabel }}
                </label>
              </div>

              <!-- Type: Range -->
              <div class="form-check d-flex align-items-center gap-2 flex-wrap">
                <input class="form-check-input" type="radio" :name="activeTab + '-type'" :id="activeTab + '-range'" value="range" v-model="currentVal.type">
                <label class="form-check-label text-nowrap" :for="activeTab + '-range'">
                  周期
                </label>
                <span class="text-muted small">从</span>
                <input type="number" class="form-control form-control-sm w-auto py-0 px-1" v-model.number="currentVal.range.start" :min="minVal" :max="maxVal" :disabled="currentVal.type !== 'range'">
                <span class="text-muted small">-</span>
                <input type="number" class="form-control form-control-sm w-auto py-0 px-1" v-model.number="currentVal.range.end" :min="minVal" :max="maxVal" :disabled="currentVal.type !== 'range'">
                <span class="text-muted small">{{ tabLabel }}</span>
              </div>

              <!-- Type: Loop (Step) -->
              <div class="form-check d-flex align-items-center gap-2 flex-wrap">
                <input class="form-check-input" type="radio" :name="activeTab + '-type'" :id="activeTab + '-loop'" value="loop" v-model="currentVal.type">
                <label class="form-check-label text-nowrap" :for="activeTab + '-loop'">
                  循环
                </label>
                <span class="text-muted small">从</span>
                <input type="number" class="form-control form-control-sm w-auto py-0 px-1" v-model.number="currentVal.loop.start" :min="minVal" :max="maxVal" :disabled="currentVal.type !== 'loop'">
                <span class="text-muted small">{{ tabLabel }}开始，每</span>
                <input type="number" class="form-control form-control-sm w-auto py-0 px-1" v-model.number="currentVal.loop.step" :min="1" :max="maxVal" :disabled="currentVal.type !== 'loop'">
                <span class="text-muted small">{{ tabLabel }}执行一次</span>
              </div>

              <!-- Type: Specific -->
              <div class="form-check">
                <input class="form-check-input" type="radio" :name="activeTab + '-type'" :id="activeTab + '-specific'" value="specific" v-model="currentVal.type">
                <label class="form-check-label" :for="activeTab + '-specific'">
                  指定
                </label>
              </div>
              
              <div class="ms-4 d-flex flex-wrap gap-1" v-if="currentVal.type === 'specific'">
                <div class="form-check form-check-inline m-0" style="width: 3.5rem;" v-for="i in (maxVal - minVal + 1)" :key="i">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    :value="i - 1 + minVal" 
                    v-model="currentVal.specific"
                    :id="activeTab + '-spec-' + (i - 1 + minVal)"
                  >
                  <label class="form-check-label small font-monospace" :for="activeTab + '-spec-' + (i - 1 + minVal)">
                    {{ (i - 1 + minVal).toString().padStart(2, '0') }}
                  </label>
                </div>
              </div>

            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-5 text-muted rounded border border-dashed flex-grow-1 d-flex flex-column justify-content-center empty-state">
          <i class="bi bi-hand-index-thumb fs-1 d-block mb-2 opacity-50"></i>
          <small>点击上方标签进行编辑</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue';

const props = defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'close'): void;
}>();

// Define state keys type
type StateKey = 'minute' | 'hour' | 'day' | 'month' | 'week';
const activeTab = ref<StateKey | null>(null);

const tabItems: { key: StateKey; label: string; min: number; max: number }[] = [
  { key: 'minute', label: '分钟', min: 0, max: 59 },
  { key: 'hour', label: '小时', min: 0, max: 23 },
  { key: 'day', label: '日', min: 1, max: 31 },
  { key: 'month', label: '月', min: 1, max: 12 },
  { key: 'week', label: '星期', min: 0, max: 6 }, // 0=Sun, 6=Sat
];

interface CronStateItem {
  type: string;
  range: { start: number; end: number };
  loop: { start: number; step: number };
  specific: number[];
}

// Internal state for each tab
const state = reactive<Record<StateKey, CronStateItem>>({
  minute: { type: 'every', range: { start: 0, end: 59 }, loop: { start: 0, step: 1 }, specific: [] as number[] },
  hour: { type: 'every', range: { start: 0, end: 23 }, loop: { start: 0, step: 1 }, specific: [] as number[] },
  day: { type: 'every', range: { start: 1, end: 31 }, loop: { start: 1, step: 1 }, specific: [] as number[] },
  month: { type: 'every', range: { start: 1, end: 12 }, loop: { start: 1, step: 1 }, specific: [] as number[] },
  week: { type: 'every', range: { start: 0, end: 6 }, loop: { start: 0, step: 1 }, specific: [] as number[] },
});

const currentTabItem = computed(() => {
  const key = activeTab.value;
  if (key) {
    return tabItems.find(t => t.key === key) || tabItems[0]!;
  }
  return tabItems[0]!;
});

const tabLabel = computed(() => currentTabItem.value.label);
const minVal = computed(() => currentTabItem.value.min);
const maxVal = computed(() => currentTabItem.value.max);

const currentVal = computed<CronStateItem>(() => {
  const key = activeTab.value;
  if (key) {
    return state[key];
  }
  return state['minute']; // Default fallback
});

// Helper to get badge text
const getBadgeText = (key: StateKey) => {
  const s = state[key];
  const label = tabItems.find(t => t.key === key)?.label;
  
  switch (s.type) {
    case 'every':
      if (key === 'month') return '月';
      if (key === 'day') return '天';
      if (key === 'week') return '星期';
      return `每${label}`;
    case 'range':
      return `${s.range.start}-${s.range.end}${label}`;
    case 'loop':
      return `${s.loop.start}/${s.loop.step}${label}`;
    case 'specific':
      return s.specific.length > 0 ? s.specific.join(',') : `每${label}`;
    default:
      return `每${label}`;
  }
};

// Reset field to 'every'
const resetField = (key: StateKey) => {
  state[key].type = 'every';
  state[key].specific = [];
};

const toggleTab = (key: string) => {
  // Cast key to StateKey if valid
  if (activeTab.value === key) {
    activeTab.value = null;
  } else {
    activeTab.value = key as StateKey;
  }
};

// Parse CRON string to state
const parseCron = (cron: string) => {
  const parts = cron.split(' ');
  // Handle 5 parts
  if (parts.length < 5) return;

  const keys: StateKey[] = ['minute', 'hour', 'day', 'month', 'week'];
  
  keys.forEach((key, index) => {
    const part = parts[index];
    // If part is missing, default to 'every' (*)
    if (!part) {
      state[key].type = 'every';
      return;
    }

    const s = state[key];
    const tabItem = tabItems.find(t => t.key === key);
    const min = tabItem?.min ?? 0;
    const max = tabItem?.max ?? 59;
    
    if (part === '*' || part === '?') {
      s.type = 'every';
    } else if (part.includes('-')) {
      s.type = 'range';
      const [start, end] = part.split('-').map(Number);
      s.range.start = start ?? min;
      s.range.end = end ?? max;
    } else if (part.includes('/')) {
      s.type = 'loop';
      const [start, step] = part.split('/').map(Number);
      s.loop.start = start ?? min;
      s.loop.step = step ?? 1;
    } else {
      s.type = 'specific';
      s.specific = part.split(',').map(Number).sort((a, b) => a - b);
    }
  });
};

// Generate CRON string from state
const generateCron = () => {
  const keys: StateKey[] = ['minute', 'hour', 'day', 'month', 'week'];
  const parts = keys.map(key => {
    const s = state[key];
    switch (s.type) {
      case 'every':
        return '*';
      case 'range':
        return `${s.range.start}-${s.range.end}`;
      case 'loop':
        return `${s.loop.start}/${s.loop.step}`;
      case 'specific':
        return s.specific.length > 0 ? s.specific.join(',') : '*';
      default:
        return '*';
    }
  });
  
  return parts.join(' ');
};

// Watch for external model changes
watch(() => props.modelValue, (newVal) => {
  if (newVal !== generateCron()) {
    parseCron(newVal);
  }
}, { immediate: true });

// Watch for internal state changes
watch(state, () => {
  emit('update:modelValue', generateCron());
}, { deep: true });
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
.badge-btn {
  border: 1px solid transparent;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}
.btn-xs {
  padding: 0.1rem 0.4rem;
  font-size: 0.75rem;
  line-height: 1.5;
  border-radius: 0.2rem;
}
.btn-primary-soft {
  background-color: rgba(163, 112, 247, 0.1);
  color: var(--primary-color);
  border-color: transparent;
}
.btn-primary-soft:hover {
  background-color: rgba(163, 112, 247, 0.2);
  color: var(--primary-hover);
}
.form-check-input:checked {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}
.btn-group {
  display: inline-flex;
  align-items: center;
}
/* Hide scrollbar for Chrome, Safari and Opera */
.overflow-auto::-webkit-scrollbar {
  display: none;
}
/* Hide scrollbar for IE, Edge and Firefox */
.overflow-auto {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
.nav-container {
  background-color: var(--bg-surface);
  border-color: var(--glass-border) !important;
}
.editor-panel {
  background-color: var(--bg-surface);
  border-color: var(--glass-border) !important;
}
.empty-state {
  background-color: var(--bg-surface) !important;
  border-color: var(--glass-border) !important;
}
</style>
