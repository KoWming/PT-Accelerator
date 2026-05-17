<template>
  <SettingsPageShell
    page-title="关于"
    context-title="关于"
    description=""
    :loaded="true"
    :refreshing="false"
    :overview-cards="[]"
    :feedback="statusBanner"
    kicker=""
    :hide-context-panel="true"
    :hide-status-banner="true"
  >
    <div class="about-wrap">

      <!-- Hero -->
      <section class="about-hero">
        <div class="about-hero-brand">
          <div class="about-hero-logo" aria-hidden="true">
            <svg width="44" height="44" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="32" cy="32" r="28" stroke="currentColor" stroke-width="4" />
              <path d="M20 32L28 40L44 24" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
          <div class="about-hero-identity">
            <div class="about-hero-name-row">
              <h1 class="about-hero-title">PT-Accelerator</h1>
            </div>
            <p class="about-hero-desc">
              面向 PT 场景的连接优化与同步管理平台，把测速、Tracker、Hosts、远程同步、备份与调度统一收口到一个稳定的工作台中。
            </p>
            <p class="about-hero-stack">FastAPI · Vue 3 · TypeScript</p>
          </div>
        </div>

        <div class="about-hero-divider"></div>

        <div class="about-hero-pillars">
          <div class="about-pillar">
            <i class="bx bx-rocket"></i>
            <span>CFST 测速优选</span>
          </div>
          <div class="about-pillar">
            <i class="bx bx-radar"></i>
            <span>Tracker 管理</span>
          </div>
          <div class="about-pillar">
            <i class="bx bx-globe"></i>
            <span>Hosts 工作流</span>
          </div>
          <div class="about-pillar">
            <i class="bx bx-sync"></i>
            <span>爱快 / 小米路由同步</span>
          </div>
          <div class="about-pillar">
            <i class="bx bx-data"></i>
            <span>调度与结果回看</span>
          </div>
          <div class="about-pillar">
            <i class="bx bx-cloud-upload"></i>
            <span>本地 / WebDAV 备份</span>
          </div>
        </div>
      </section>

      <!-- Body: 双列信息 -->
      <div class="about-body">

        <!-- 左：核心能力 -->
        <section class="about-section about-section-main">
          <div class="about-section-head">
            <h2>核心能力</h2>
          </div>

          <div class="about-feat-grid">
            <div class="about-feat-item">
              <div class="about-feat-icon"><i class="bx bx-rocket"></i></div>
              <div class="about-feat-copy">
                <h3>CFST 测速优选</h3>
                <p>集成 CloudflareSpeedTest，批量探测并筛选出最适合当前网络环境的节点。</p>
              </div>
            </div>
            <div class="about-feat-item">
              <div class="about-feat-icon"><i class="bx bx-radar"></i></div>
              <div class="about-feat-copy">
                <h3>Tracker 管理</h3>
                <p>批量维护 PT Tracker，配合优选链路与域名解析进行统一管理。</p>
              </div>
            </div>
            <div class="about-feat-item">
              <div class="about-feat-icon"><i class="bx bx-globe"></i></div>
              <div class="about-feat-copy">
                <h3>Hosts 工作流</h3>
                <p>覆盖刷新、重建、编辑与保存等常见链路，稳定维护本地 Hosts 内容。</p>
              </div>
            </div>
            <div class="about-feat-item">
              <div class="about-feat-icon"><i class="bx bx-sync"></i></div>
              <div class="about-feat-copy">
                <h3>远程同步</h3>
                <p>将优选结果分发到爱快 DNS 与小米路由器 Hosts，减少重复配置。</p>
              </div>
            </div>
            <div class="about-feat-item">
              <div class="about-feat-icon"><i class="bx bx-data"></i></div>
              <div class="about-feat-copy">
                <h3>调度与结果回看</h3>
                <p>围绕执行状态、最近结果与计划任务，提供稳定清晰的运行反馈。</p>
              </div>
            </div>
            <div class="about-feat-item">
              <div class="about-feat-icon"><i class="bx bx-cloud-upload"></i></div>
              <div class="about-feat-copy">
                <h3>备份恢复</h3>
                <p>支持本地与 WebDAV 备份链路，方便迁移配置与长期留档。</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 右：技术信息 -->
        <section class="about-section about-section-side">
          <div class="about-section-head">
            <h2>技术架构 · 项目链接</h2>
          </div>

          <div class="about-info-group">
            <div class="about-info-group-label">技术栈：</div>
            <div class="about-info-rows">
              <div class="about-info-row">
                <span class="about-info-key">后端</span>
                <div class="about-info-val">
                  <strong>Python · FastAPI · APScheduler</strong>
                </div>
              </div>
              <div class="about-info-row">
                <span class="about-info-key">前端</span>
                <div class="about-info-val">
                  <strong>Vue 3 · TypeScript · Vite</strong>
                </div>
              </div>
              <div class="about-info-row">
                <span class="about-info-key">样式</span>
                <div class="about-info-val">
                  <strong>CSS Variables · Boxicons</strong>
                </div>
              </div>
            </div>
          </div>

          <div class="about-info-group">
            <div class="about-info-group-label">项目链接：</div>
            <div class="about-info-rows about-link-rows">
              <div class="about-info-row about-info-row-link">
                <span class="about-info-key">原始项目</span>
                <a href="https://github.com/eternalcurse/PT-Accelerator" target="_blank" rel="noopener noreferrer" class="about-info-link-main">
                  <i class="bx bxl-github about-link-icon" aria-hidden="true"></i>
                  <strong>eternalcurse / PT-Accelerator</strong>
                  <i class="bx bx-up-right-arrow-alt"></i>
                </a>
              </div>
              <div class="about-info-row about-info-row-link">
                <span class="about-info-key">当前项目</span>
                <a href="https://github.com/KoWming/PT-Accelerator" target="_blank" rel="noopener noreferrer" class="about-info-link-main">
                  <i class="bx bxl-github about-link-icon" aria-hidden="true"></i>
                  <strong>KoWming / PT-Accelerator</strong>
                  <i class="bx bx-up-right-arrow-alt"></i>
                </a>
              </div>
              <div class="about-info-row about-info-row-link">
                <span class="about-info-key">CFST项目</span>
                <a href="https://github.com/XIU2/CloudflareSpeedTest" target="_blank" rel="noopener noreferrer" class="about-info-link-main">
                  <i class="bx bxl-github about-link-icon" aria-hidden="true"></i>
                  <strong>XIU2 / CloudflareSpeedTest</strong>
                  <i class="bx bx-up-right-arrow-alt"></i>
                </a>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </SettingsPageShell>
</template>

<script setup lang="ts">
import '@/assets/styles/settings.css';
import { ref } from 'vue';
import SettingsPageShell from '@/components/settings/shared/SettingsPageShell.vue';
import type { PageFeedback } from '@/types/settings';

const statusBanner = ref<PageFeedback>({
  title: '',
  message: '',
  status: 'success',
});
</script>

<style scoped>
/* ─── 页面容器 ─── */
.about-wrap {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 0.4rem;
}

/* ─── Hero ─── */
.about-hero {
  padding: 1.4rem 1.5rem 1.3rem;
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  background: var(--bg-surface);
}

.about-hero-brand {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 1.25rem;
  align-items: start;
}

.about-hero-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 1rem;
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.08);
  border: 1px solid rgba(var(--primary-rgb), 0.14);
}

.about-hero-identity {
  min-width: 0;
  padding-top: 0.1rem;
}

.about-hero-name-row {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.6rem;
}

.about-hero-title {
  margin: 0;
  color: var(--text-heading);
  font-size: 1.55rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1;
}

.about-hero-desc {
  margin: 0 0 0.55rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.72;
}

.about-hero-stack {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.about-hero-divider {
  height: 1px;
  background: var(--border-color);
  margin: 1.1rem 0;
}

.about-hero-pillars {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0;
}

.about-pillar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: calc(33.33% - 0.1rem);
  color: var(--text-secondary);
  font-size: 0.84rem;
  padding: 0.28rem 0;
}

.about-pillar i {
  color: var(--primary-color);
  font-size: 0.95rem;
  flex-shrink: 0;
}

/* ─── 双列主体 ─── */
.about-body {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 1.25rem;
  align-items: stretch;
}

.about-section {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  background: var(--bg-surface);
}

.about-section-main {
  justify-content: flex-start;
}

.about-section-side {
  justify-content: flex-start;
}

/* ─── 区块头 ─── */
.about-section-head {
  display: flex;
  flex-direction: column;
  gap: 0.28rem;
  margin-bottom: 1.1rem;
  padding-bottom: 0.95rem;
  border-bottom: 1px solid var(--border-color);
}

.about-section-eyebrow {
  color: var(--primary-color);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.about-section-head h2 {
  margin: 0;
  color: var(--text-heading);
  font-size: 1rem;
  font-weight: 650;
}

/* ─── 能力网格 ─── */
.about-feat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-content: start;
}

.about-feat-item {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
}

.about-feat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 2.45rem;
  height: 2.45rem;
  border-radius: 0.78rem;
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.08);
  font-size: 1.05rem;
}

.about-feat-copy h3 {
  margin: 0 0 0.28rem;
  color: var(--text-heading);
  font-size: 0.88rem;
  font-weight: 600;
}

.about-feat-copy p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.65;
}

/* ─── 信息组 ─── */
.about-info-group {
  margin-bottom: 1.1rem;
}

.about-info-group:last-child {
  margin-top: auto;
  margin-bottom: 0;
}

.about-info-group-label {
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.65rem;
}

.about-info-rows {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.about-link-rows {
  gap: 0.5rem;
}

.about-info-row {
  display: grid;
  grid-template-columns: 4rem minmax(0, 1fr);
  gap: 0.75rem;
  align-items: start;
}

.about-info-row-link {
  align-items: center;
  min-height: 2.75rem;
  padding: 0.2rem 0;
}

.about-info-row-link .about-info-key {
  padding-top: 0;
}

.about-info-key {
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.about-info-val strong {
  display: block;
  margin-bottom: 0.18rem;
  color: var(--text-heading);
  font-size: 0.88rem;
}

.about-info-link-main {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  min-width: 0;
  width: fit-content;
  max-width: 100%;
  padding: 0;
  margin: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  outline: none;
  color: inherit;
  text-decoration: none;
}

.about-link-icon {
  flex-shrink: 0;
  color: var(--primary-color);
  font-size: 1.05rem;
}

.about-info-link-main strong {
  margin: 0;
  color: var(--primary-color);
}

.about-info-link-main > .bx-up-right-arrow-alt {
  color: var(--primary-color);
  font-size: 1rem;
  flex-shrink: 0;
  transition: transform 0.18s ease, color 0.18s ease, opacity 0.18s ease;
  opacity: 0.8;
}

.about-info-val p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.6;
}

.about-info-link-main:hover strong,
.about-info-link-main:hover .about-link-icon,
.about-info-link-main:hover > .bx-up-right-arrow-alt {
  color: var(--primary-hover);
}

.about-info-link-main:hover > .bx-up-right-arrow-alt {
  transform: translateX(2px);
  opacity: 1;
}

/* ─── 响应式 ─── */
@media (max-width: 1080px) {
  .about-body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 860px) {
  .about-hero-brand {
    grid-template-columns: 1fr;
  }

  .about-hero-logo {
    display: none;
  }

  .about-pillar {
    width: 50%;
  }

  .about-feat-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .about-wrap {
    gap: 1rem;
    padding: 0.2rem;
  }

  .about-hero,
  .about-section {
    padding: 1rem;
    border-radius: 0.85rem;
  }

  .about-info-row {
    grid-template-columns: 1fr;
    gap: 0.3rem;
  }

  .about-pillar {
    width: 100%;
  }
}
</style>
