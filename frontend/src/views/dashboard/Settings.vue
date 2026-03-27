<template>
  <div class="dashboard-redesign settings-redesign">
    <div class="page-header">
      <h2 class="page-title">系统设置</h2>
    </div>

    <!-- Routed Content -->
    <div class="tab-content">
      <transition name="fade" mode="out-in">
        <div v-if="currentSection === 'system'" key="system" class="settings-section-shell">
          <article class="workspace-card settings-auth-card">
            <header class="workspace-card-header settings-auth-header">
              <div class="settings-card-heading">
                <div class="settings-card-title-row">
                  <h3>
                    安全与认证
                  </h3>
                </div>
                <p>统一管理控制台登录认证、管理员账号与密码更新策略，提升后台访问安全性。</p>
              </div>
            </header>

            <div class="settings-auth-body">
              <form @submit.prevent="saveAuthSettings">
                <div class="settings-inline-note" role="alert">
                  <i class="bx bx-info-circle"></i>
                  <div>
                    <span class="settings-inline-note-title">启用登录认证后，所有访问此控制面板的操作都需要验证身份。</span>
                    <div class="settings-inline-note-text">
                        <strong>注意:</strong> 如果管理员密码尚未设置，启用认证时请自行输入新密码。若留空，系统将自动生成一个初始密码并打印在应用日志中。
                    </div>
                  </div>
                </div>

                <section class="settings-auth-toggle-card">
                  <div class="settings-auth-toggle-copy">
                    <span class="settings-field-label">认证状态</span>
                    <strong>启用登录认证</strong>
                    <p>开启后，进入后台前需要使用管理员身份进行验证。</p>
                  </div>
                  <label class="switch settings-auth-switch" for="auth-enable">
                    <input type="checkbox" id="auth-enable" v-model="authForm.enable_auth">
                    <div class="slider">
                      <div class="circle">
                        <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                          <g>
                            <path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path>
                          </g>
                        </svg>
                        <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg">
                          <g>
                            <path class="" data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path>
                          </g>
                        </svg>
                      </div>
                    </div>
                  </label>
                </section>

                <transition name="fade">
                  <div v-if="authForm.enable_auth" class="settings-auth-form-grid">
                    <section class="settings-form-block settings-form-block-single">
                      <div class="settings-block-heading">
                        <h4>账号信息</h4>
                        <p>建议使用便于识别的管理员用户名，避免与其他服务账号混淆。</p>
                      </div>

                      <div class="settings-field-grid settings-field-grid-single">
                        <div class="settings-field-card">
                          <label class="form-label settings-form-label">用户名</label>
                          <div class="input-group settings-input-group">
                            <span class="input-group-text"><i class="bx bx-user"></i></span>
                            <input type="text" class="form-control" v-model="authForm.username" placeholder="请输入管理员用户名">
                          </div>
                        </div>
                      </div>
                    </section>

                    <section class="settings-form-block">
                      <div class="settings-block-heading settings-block-heading-inline">
                        <h4>密码更新</h4>
                        <span class="settings-mini-note">建议定期轮换密码</span>
                      </div>

                      <div class="settings-password-divider">
                        <span>修改密码</span>
                      </div>

                      <div class="settings-field-grid">
                        <div class="settings-field-card settings-field-card-full">
                          <label class="form-label settings-form-label">当前密码</label>
                          <div class="input-group settings-input-group">
                            <span class="input-group-text"><i class="bx bx-key"></i></span>
                            <input type="password" class="form-control" v-model="authForm.current_password" placeholder="留空则不修改">
                          </div>
                          <div class="settings-field-hint">如果首次设置密码或认证被禁用时更改密码，则无需当前密码。</div>
                        </div>
                        <div class="settings-field-card">
                          <label class="form-label settings-form-label">新密码</label>
                          <input type="password" class="form-control settings-standalone-input" v-model="authForm.new_password" placeholder="请输入新密码">
                          <div class="settings-field-hint">密码要求：至少8位字符，建议包含大小写字母、数字和特殊字符。</div>
                        </div>
                        <div class="settings-field-card">
                          <label class="form-label settings-form-label">确认新密码</label>
                          <input type="password" class="form-control settings-standalone-input" v-model="authForm.confirm_password" placeholder="请再次输入新密码">
                        </div>
                      </div>
                    </section>
                  </div>
                </transition>
                
                <div class="settings-auth-actions">
                  <button type="submit" class="settings-save-btn" :disabled="savingAuth">
                    <span v-if="savingAuth" class="spinner-border spinner-border-sm me-2"></span>
                    <span v-else><i class="bx bx-check me-2"></i>保存设置</span>
                  </button>
                </div>
              </form>
            </div>
          </article>
        </div>

        <div v-else-if="currentSection === 'notification'" key="notification" class="settings-section-shell">
          <article class="workspace-card settings-notify-card">
            <header class="workspace-card-header settings-section-header">
              <div class="settings-card-heading">
                <div class="settings-card-title-row">
                  <h3>
                    通知渠道
                    <span class="settings-title-count">({{ Object.keys(notifyChannels).length }}个)</span>
                  </h3>
                  <button class="settings-toolbar-btn settings-toolbar-btn-primary" @click="openAddModal">
                    <i class="bx bx-plus"></i>
                    <span>添加渠道</span>
                  </button>
                </div>
                <p>统一管理通知推送渠道、启用状态、测试发送与编辑维护操作。</p>
              </div>
            </header>

            <div class="settings-section-body">
              <div v-if="Object.keys(notifyChannels).length === 0" class="workspace-empty settings-empty-state">
                <i class="bx bx-bell-off fs-1 d-block mb-3 opacity-50"></i>
                暂无通知渠道
              </div>

              <div v-else class="settings-channel-list">
                <div v-for="(channel, key) in notifyChannels" :key="key" class="settings-channel-item transition-hover">
                  <div class="d-flex flex-column flex-md-row gap-3">
                    <div class="d-flex align-items-center flex-grow-1 min-width-0">
                      <div class="settings-channel-icon">
                        <i class="bx" :class="getChannelIcon(String(channel.type))"></i>
                      </div>
                      <div class="flex-grow-1 min-width-0">
                        <div class="d-flex justify-content-between align-items-center mb-1 gap-2">
                          <h6 class="mb-0 fw-semibold text-break me-2">{{ channel.name || key }}</h6>
                          <div class="flex-shrink-0 ps-2 d-md-none">
                            <label class="switch">
                              <input type="checkbox" :checked="channel.enable" @change="toggleChannel(String(key))">
                              <div class="slider">
                                <div class="circle">
                                  <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                                  <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                                </div>
                              </div>
                            </label>
                          </div>
                        </div>

                        <div class="d-flex align-items-center flex-wrap gap-2 small text-muted">
                          <div class="d-flex gap-2 align-items-center">
                            <span class="settings-chip" :class="getChannelChipClass(String(channel.type))">{{ getChannelTypeLabel(String(channel.type)) }}</span>
                            <span v-if="channel.HITOKOTO" class="settings-chip settings-chip-primary">一言</span>
                          </div>
                          <span class="text-truncate d-inline-block" style="max-width: 100%;">{{ getChannelSummary(channel) }}</span>
                        </div>
                      </div>
                    </div>

                    <div class="settings-channel-actions d-flex align-items-center justify-content-end gap-2 ps-md-3 w-100 w-md-auto mt-2 mt-md-0">
                      <div class="d-none d-md-block me-2">
                        <label class="switch">
                          <input type="checkbox" :checked="channel.enable" @change="toggleChannel(String(key))">
                          <div class="slider">
                            <div class="circle">
                              <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                              <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                            </div>
                          </div>
                        </label>
                      </div>
                      <button class="settings-action-btn settings-action-success flex-grow-1 flex-md-grow-0 justify-content-center" @click="testChannel(String(key))" :disabled="testingChannel === String(key)">
                        <span v-if="testingChannel === String(key)" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bx bx-send me-1"></i> 测试
                      </button>
                      <button class="settings-action-btn settings-action-primary flex-grow-1 flex-md-grow-0 justify-content-center" @click="editChannel(String(key))">
                        <i class="bx bx-pencil me-1"></i> 编辑
                      </button>
                      <button class="settings-action-btn settings-action-danger flex-grow-1 flex-md-grow-0 justify-content-center" @click="deleteChannel(String(key))">
                        <i class="bx bx-trash me-1"></i> 删除
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <NotificationForm
                v-if="showModal"
                :initialData="currentChannel"
                :isEdit="!!currentChannelId"
                @close="closeModal"
                @save="saveChannel"
              />

              <div class="settings-guide-panel">
                <div class="settings-guide-header">
                  <h6><i class="bx bx-info-circle"></i>通知渠道说明</h6>
                </div>
                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="settings-guide-item h-100">
                      <div class="d-flex mb-2"><span class="settings-chip settings-chip-success">企业微信机器人</span></div>
                      <p class="small text-muted mb-0">适合企业微信群通知，配置机器人 Key 即可。</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="settings-guide-item h-100">
                      <div class="d-flex mb-2"><span class="settings-chip settings-chip-success">企业微信App</span></div>
                      <p class="small text-muted mb-0">通过企业自建应用推送，需 corpid/corpsecret/touser/agentid，可选 media_id。</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="settings-guide-item h-100">
                      <div class="d-flex mb-2"><span class="settings-chip settings-chip-primary">Telegram</span></div>
                      <p class="small text-muted mb-0">使用 Bot Token 与用户ID，支持可选代理。</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="settings-guide-item h-100">
                      <div class="d-flex mb-2"><span class="settings-chip settings-chip-warning">邮件 (SMTP)</span></div>
                      <p class="small text-muted mb-0">配置服务器、邮箱与密码，支持 SSL 与端口。</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="settings-guide-item h-100">
                      <div class="d-flex mb-2"><span class="settings-chip settings-chip-info">iGot / Server酱 / 飞书 / 钉钉</span></div>
                      <p class="small text-muted mb-0">常用聚合与办公通知渠道，分别填写对应的 Key 或 Token 即可。</p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="settings-guide-item h-100">
                      <div class="d-flex mb-2"><span class="settings-chip settings-chip-neutral">自定义 Webhook</span></div>
                      <p class="small text-muted mb-0">支持 POST/GET，自定义 Header 与 Body（含占位符 $title/$content）。</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-else-if="currentSection === 'backup'" key="backup" class="settings-section-shell">
          <article class="workspace-card settings-backup-card">
            <header class="workspace-card-header settings-section-header">
              <div class="settings-card-heading">
                <div class="settings-card-title-row">
                  <h3>
                    备份设置
                  </h3>
                </div>
                <p>配置 WebDAV 远程存储、自动备份周期、保留份数与恢复流程，确保配置可快速回滚。</p>
              </div>
            </header>

            <div class="settings-section-body">
              <form @submit.prevent="saveBackupSettings">
                <div class="settings-inline-note settings-inline-note-info" role="alert">
                  <i class="bx bx-info-circle"></i>
                  <div style="min-width: 0;">
                    <span class="settings-inline-note-title">配置 WebDav 以备份系统配置。</span>
                    <div class="settings-inline-note-text text-break">
                      支持定时自动备份和手动立即备份。备份文件将保存为 config_YYYYMMDD_HHMMSS.yaml。
                    </div>
                  </div>
                </div>

                <section class="settings-auth-toggle-card settings-backup-toggle-card">
                  <div class="settings-auth-toggle-copy">
                    <span class="settings-field-label">备份状态</span>
                    <strong>启用配置备份</strong>
                    <p>开启后可配置自动备份任务，并支持手动测试、立即备份与恢复历史版本。</p>
                  </div>
                  <label class="switch settings-auth-switch" for="backup-enable">
                    <input type="checkbox" id="backup-enable" v-model="backupForm.enable">
                    <div class="slider">
                      <div class="circle">
                        <svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg>
                        <svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg>
                      </div>
                    </div>
                  </label>
                </section>

                <transition name="fade">
                  <div v-if="backupForm.enable" class="settings-auth-form-grid">
                    <section class="settings-form-block">
                      <div class="settings-block-heading">
                        <h4>远程存储连接</h4>
                        <p>填写 WebDAV 地址与认证信息，用于保存和读取备份文件。</p>
                      </div>

                      <div class="settings-field-grid settings-field-grid-single">
                        <div class="settings-field-card settings-field-card-full">
                          <label class="form-label settings-form-label">WebDav URL</label>
                          <input type="text" class="form-control settings-standalone-input" v-model="backupForm.webdav_url" placeholder="https://example.com/dav/">
                        </div>
                      </div>

                      <div class="settings-field-grid">
                        <div class="settings-field-card">
                          <label class="form-label settings-form-label">用户名</label>
                          <input type="text" class="form-control settings-standalone-input" v-model="backupForm.webdav_username" placeholder="请输入 WebDAV 用户名">
                        </div>
                        <div class="settings-field-card">
                          <label class="form-label settings-form-label">密码</label>
                          <input type="password" class="form-control settings-standalone-input" v-model="backupForm.webdav_password" placeholder="请输入 WebDAV 密码">
                        </div>
                      </div>
                    </section>

                    <section class="settings-form-block">
                      <div class="settings-block-heading settings-block-heading-inline">
                        <h4>备份策略</h4>
                      </div>

                      <div class="settings-field-grid">
                        <div class="settings-field-card">
                          <label class="form-label settings-form-label">备份保留份数</label>
                          <input type="number" class="form-control settings-standalone-input" v-model.number="backupForm.backup_count" min="1" placeholder="5">
                          <div class="settings-field-hint">当备份数量超过此限制时，将自动删除最旧的备份。默认保留 5 份。</div>
                        </div>
                        <div class="settings-field-card">
                          <label class="form-label settings-form-label">Cron 表达式 (自动备份时间)</label>
                          <CronInput v-model="backupForm.cron" />
                          <div class="settings-field-hint">默认为每天凌晨 2:00（0 2 * * *）。</div>
                        </div>
                      </div>
                    </section>
                  </div>
                </transition>

                <div class="settings-backup-actions">
                  <div class="settings-backup-tools">
                    <button type="button" class="settings-action-btn settings-action-neutral justify-content-center" @click="testBackupConnection" :disabled="testingConnection || !backupForm.webdav_url">
                      <span v-if="testingConnection" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bx bx-plug me-2"></i>测试连接
                    </button>
                    <button type="button" class="settings-action-btn settings-action-success justify-content-center" @click="runBackupNow" :disabled="runningBackup || !backupForm.enable">
                      <span v-if="runningBackup" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bx bx-play-circle me-2"></i>立即备份
                    </button>
                    <button type="button" class="settings-action-btn settings-action-warning justify-content-center" @click="openBackupModal" :disabled="loadingBackups || !backupForm.webdav_url">
                      <span v-if="loadingBackups" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bx bx-reset me-2"></i>备份恢复
                    </button>
                  </div>
                  <button type="submit" class="settings-save-btn" :disabled="savingBackup">
                    <span v-if="savingBackup" class="spinner-border spinner-border-sm me-2"></span>
                    <span v-else><i class="bx bx-check me-2"></i>保存设置</span>
                  </button>
                </div>
              </form>
            </div>
          </article>
        </div>
      </transition>
    </div>

    <!-- Backup Restore Modal -->
    <!-- Backup Restore Modal -->
    <Teleport to="body">
      <div v-if="showBackupModal" class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" tabindex="-1" @click.self="showBackupModal = false">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">恢复备份</h5>
              <button type="button" class="btn-close" @click="showBackupModal = false"></button>
            </div>
            <div class="modal-body">
              <div v-if="loadingBackups" class="text-center py-4">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 text-muted">正在获取备份列表...</p>
              </div>
              <div v-else-if="backups.length === 0" class="text-center py-4 text-muted">
                未找到备份文件
              </div>
              <div v-else class="list-group list-group-flush">
                <button v-for="backup in backups" :key="backup.filename" 
                        class="list-group-item list-group-item-action d-flex justify-content-between align-items-center bg-transparent text-main border-0 rounded-3 mb-1 backup-item"
                        @click="confirmRestore(backup)">
                  <div>
                    <div class="fw-bold">{{ backup.filename }}</div>
                    <small class="text-muted">{{ backup.last_modified }} ({{ formatSize(backup.size) }})</small>
                  </div>
                  <i class="bx bx-reset"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, reactive, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from '../../api/axios';
import NotificationForm from '../../components/NotificationForm.vue';
import CronInput from '../../components/CronInput.vue';
import { useToast } from 'vue-toastification';
import { useConfirm } from '../../composables/useConfirm';

const route = useRoute();
const showModal = ref(false);
const currentChannelId = ref<string | null>(null);
const currentChannel = ref<any>(null);
const savingAuth = ref(false);
const toast = useToast();
const { confirm } = useConfirm();
const testingChannel = ref<string | null>(null);

const authForm = reactive({
  enable_auth: false,
  username: '',
  current_password: '',
  new_password: '',
  confirm_password: ''
});

const backupForm = reactive({
  enable: false,
  webdav_url: '',
  webdav_username: '',
  webdav_password: '',
  cron: '0 2 * * *',
  backup_count: 5
});

const testingConnection = ref(false);
const runningBackup = ref(false);
const savingBackup = ref(false);
const showBackupModal = ref(false);
const backups = ref<any[]>([]);
const loadingBackups = ref(false);
const restoringBackup = ref(false);

const fullConfig = ref<any>({});
const notifyChannels = ref<Record<string, any>>({});

const currentSection = computed<'system' | 'notification' | 'backup'>(() => {
  if (route.path.includes('/settings/notification')) return 'notification';
  if (route.path.includes('/settings/backup')) return 'backup';
  return 'system';
});

const fetchSettings = async () => {
  try {
    const response = await axios.get('/config');
    fullConfig.value = response.data;
    const auth = response.data.auth || {};
    
    // Load notify channels
    if (response.data.notify && response.data.notify.channels) {
      notifyChannels.value = response.data.notify.channels;
    }
    authForm.enable_auth = auth.enable || false;
    authForm.username = auth.username || '';
    
    // Load backup settings
    const backup = response.data.backup || {};
    backupForm.enable = backup.enable || false;
    backupForm.webdav_url = backup.webdav_url || '';
    backupForm.webdav_username = backup.webdav_username || '';
    backupForm.webdav_password = backup.webdav_password || '';
    backupForm.cron = backup.cron || '0 2 * * *';
    backupForm.backup_count = backup.backup_count || 5;
  } catch (e) {
    console.error('Failed to load config', e);
  }
};

onMounted(async () => {
  await fetchSettings();
});

const saveAuthSettings = async () => {
  if (authForm.new_password && authForm.new_password !== authForm.confirm_password) {
    toast.error('两次输入的密码不一致');
    return;
  }
  
  savingAuth.value = true;
  try {
    const formData = new FormData();
    formData.append('enable_auth', String(authForm.enable_auth));
    
    if (authForm.username) formData.append('username', authForm.username);
    if (authForm.current_password) formData.append('current_password', authForm.current_password);
    if (authForm.new_password) formData.append('new_password', authForm.new_password);
    if (authForm.confirm_password) formData.append('confirm_password', authForm.confirm_password);
    
    const response = await axios.post('/auth/config', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    toast.success(response.data.message || '认证设置已保存');
    authForm.current_password = '';
    authForm.new_password = '';
    authForm.confirm_password = '';
  } catch (e: any) {
    toast.error('保存失败: ' + (e.response?.data?.detail || e.message));
  } finally {
    savingAuth.value = false;
  }
};

const getChannelSummary = (channel: any) => {
  switch (channel.type) {
    case 'bark': return channel.BARK_PUSH ? `Key: ${channel.BARK_PUSH.substring(0, 8)}...` : '';
    case 'telegram': return `Bot: ...${channel.TG_BOT_TOKEN?.substring(0, 5) || ''}`;
    case 'smtp': return `Email: ${channel.SMTP_EMAIL}`;
    default: return '';
  }
};

const openAddModal = () => {
  currentChannelId.value = null;
  currentChannel.value = null;
  showModal.value = true;
};

const editChannel = (key: string) => {
  currentChannelId.value = key;
  // Look up the latest channel data from the reactive state
  const channel = notifyChannels.value[key];
  if (channel) {
    currentChannel.value = { ...channel }; // Clone
    showModal.value = true;
  }
};

const deleteChannel = async (key: string) => {
  if (!await confirm('确定要删除此通知渠道吗？', '删除确认')) return;
  
  try {
    const newChannels = { ...notifyChannels.value };
    delete newChannels[key];
    await saveNotifyConfig(newChannels);
    toast.success('删除成功');
  } catch (e) {
    toast.error('删除失败');
  }
};

const toggleChannel = async (key: string) => {
  try {
    // Look up the latest channel data to ensure we have the correct state
    const currentData = notifyChannels.value[key];
    if (!currentData) return;

    const newChannels = { ...notifyChannels.value };
    // Toggle based on the CURRENT state in the reactive object
    newChannels[key] = { ...currentData, enable: !currentData.enable };
    
    // Optimistic update
    notifyChannels.value = newChannels;

    await saveNotifyConfig(newChannels);
  } catch (e) {
    // Revert on error
    await fetchSettings();
    toast.error('状态更新失败');
  }
};

const testChannel = async (key: string) => {
  testingChannel.value = key;
  try {
    await axios.post(`/notify/test/${key}`);
    toast.success('测试消息已发送');
  } catch (e) {
    toast.error('测试发送失败');
  } finally {
    testingChannel.value = null;
  }
};

const closeModal = () => {
  showModal.value = false;
  currentChannelId.value = null;
  currentChannel.value = null;
};

const saveChannel = async (channelData: any) => {
  const newChannels = { ...notifyChannels.value };
  
  if (currentChannelId.value) {
    // Edit
    newChannels[currentChannelId.value] = channelData;
  } else {
    // Add - generate a simple ID
    const id = 'channel_' + Date.now();
    newChannels[id] = channelData;
  }
  
  await saveNotifyConfig(newChannels);
  closeModal();
};

const saveNotifyConfig = async (channels: any) => {
  try {
    const newConfig = { ...fullConfig.value };
    if (!newConfig.notify) newConfig.notify = {};
    newConfig.notify.channels = channels;
    
    notifyChannels.value = channels;
    fullConfig.value = newConfig;

    await axios.post('/config', newConfig);
    toast.success('通知设置已保存');
  } catch (e: any) {
    toast.error('保存通知设置失败: ' + (e.response?.data?.detail || e.message));
  }
};

const saveBackupSettings = async () => {
  savingBackup.value = true;
  try {
    const newConfig = { ...fullConfig.value };
    newConfig.backup = { ...backupForm };
    
    fullConfig.value = newConfig;
    
    await axios.post('/config', newConfig);
    toast.success('备份设置已保存');
  } catch (e: any) {
    toast.error('保存失败: ' + (e.response?.data?.detail || e.message));
  } finally {
    savingBackup.value = false;
  }
};

const testBackupConnection = async () => {
  testingConnection.value = true;
  try {
    const config = {
      webdav_url: backupForm.webdav_url,
      webdav_username: backupForm.webdav_username,
      webdav_password: backupForm.webdav_password
    };
    const response = await axios.post('/backup/test', config);
    if (response.data.success) {
      toast.success(response.data.message);
    } else {
      toast.error('测试失败: ' + response.data.message);
    }
  } catch (e: any) {
    toast.error('测试出错: ' + (e.response?.data?.detail || e.message));
  } finally {
    testingConnection.value = false;
  }
};



const openBackupModal = async () => {
  showBackupModal.value = true;
  loadingBackups.value = true;
  try {
    const response = await axios.get('/backup/list');
    if (response.data.success) {
      backups.value = response.data.backups;
    } else {
      toast.error(response.data.message);
    }
  } catch (e: any) {
    toast.error('获取备份列表失败: ' + (e.response?.data?.detail || e.message));
  } finally {
    loadingBackups.value = false;
  }
};

const confirmRestore = async (backup: any) => {
  if (!await confirm(`确定要恢复备份 ${backup.filename} 吗？\n当前配置将被覆盖！`, '恢复确认')) return;
  
  restoringBackup.value = true;
  try {
    const response = await axios.post('/backup/restore', { filename: backup.filename });
    if (response.data.success) {
      toast.success(response.data.message);
      showBackupModal.value = false;
      // Refresh settings
      await fetchSettings();
    } else {
      toast.error(response.data.message);
    }
  } catch (e: any) {
    toast.error('恢复失败: ' + (e.response?.data?.detail || e.message));
  } finally {
    restoringBackup.value = false;
  }
};

const formatSize = (bytes: string | number) => {
  const b = parseInt(String(bytes));
  if (isNaN(b)) return bytes;
  if (b < 1024) return b + ' B';
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
  return (b / (1024 * 1024)).toFixed(1) + ' MB';
};

const runBackupNow = async () => {
  if (!await confirm('确定要立即执行备份吗？', '备份确认')) return;
  runningBackup.value = true;
  try {
    const response = await axios.post('/backup/run');
    toast.success(response.data.message);
  } catch (e: any) {
    toast.error('执行失败: ' + (e.response?.data?.detail || e.message));
  } finally {
    runningBackup.value = false;
  }
};

const getChannelIcon = (type: string) => {
  switch (type) {
    case 'bark': return 'bx bx-megaphone';
    case 'telegram': return 'bx bxl-telegram';
    case 'wecom_bot': case 'wecom_app': return 'bx bx-message-dots';
    case 'smtp': return 'bx bx-envelope';
    case 'wxpusher': return 'bx bx-chat';
    case 'gotify': return 'bx bx-broadcast';
    default: return 'bx bx-bell';
  }
};

const getChannelChipClass = (type: string) => {
  switch (type) {
    case 'wecom_bot':
    case 'wecom_app':
      return 'settings-chip-success';
    case 'telegram':
      return 'settings-chip-primary';
    case 'smtp':
      return 'settings-chip-warning';
    case 'serverchan':
    case 'feishu':
    case 'dingtalk':
    case 'igot':
    case 'wxpusher':
    case 'gotify':
      return 'settings-chip-info';
    case 'webhook':
      return 'settings-chip-neutral';
    default:
      return 'settings-chip-neutral';
  }
};

const getChannelTypeLabel = (type: string) => {
  switch (type) {
    case 'wecom_bot':
      return '企业微信机器人';
    case 'wecom_app':
      return '企业微信App';
    case 'telegram':
      return 'Telegram';
    case 'smtp':
      return '邮件 (SMTP)';
    case 'serverchan':
      return 'Server酱';
    case 'feishu':
      return '飞书';
    case 'dingtalk':
      return '钉钉';
    case 'igot':
      return 'iGot';
    case 'wxpusher':
      return 'WxPusher';
    case 'gotify':
      return 'Gotify';
    case 'webhook':
      return '自定义 Webhook';
    case 'bark':
      return 'Bark';
    default:
      return type;
  }
};
</script>

<style scoped>
.settings-redesign {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.12rem;
}

.settings-section-shell {
  display: flex;
}

.settings-auth-card {
  width: 100%;
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  background: var(--bg-surface);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.workspace-card-header.settings-auth-header {
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid var(--divider-color);
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.035), transparent 100%);
}

.workspace-card.settings-notify-card,
.workspace-card.settings-backup-card {
  width: 100%;
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  background: var(--bg-surface);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.workspace-card.settings-backup-card {
  overflow: visible;
}

.workspace-card-header.settings-section-header {
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid var(--divider-color);
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.03), transparent 100%);
}

.settings-section-header-split {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.settings-section-body {
  padding: 1.5rem;
}

.settings-title-badge-warning {
  color: #ffb400;
  background: rgba(255, 180, 0, 0.12);
}

.settings-title-badge-info {
  color: #0dcaf0;
  background: rgba(13, 202, 240, 0.12);
}

.settings-inline-note-info {
  border-color: rgba(13, 202, 240, 0.22);
  background: rgba(13, 202, 240, 0.08);
}

.settings-toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 2.32rem;
  padding: 0.54rem 0.92rem;
  border-radius: 0.78rem;
  border: 1px solid transparent;
  font-weight: 600;
  font-size: 0.92rem;
  line-height: 1;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
}

.settings-toolbar-btn-primary {
  color: #fff;
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.98), rgba(var(--primary-rgb), 0.84));
  box-shadow: 0 0.65rem 1.4rem rgba(var(--primary-rgb), 0.2);
}

.settings-toolbar-btn-primary:hover {
  transform: translateY(-1px);
}

.settings-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 220px;
  border: 1px dashed var(--border-color);
  border-radius: 1rem;
  background: var(--bg-surface-alt);
  color: var(--text-muted);
  font-weight: 500;
}

.settings-channel-list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.settings-channel-item {
  padding: 0.62rem 0.78rem;
  border-radius: 0.95rem;
  border: 1px solid var(--border-color);
  background: var(--bg-surface-alt);
}

.settings-channel-icon {
  width: 2.35rem;
  height: 2.35rem;
  margin-right: 0.72rem;
  border-radius: 0.78rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--primary-rgb), 0.1);
  color: var(--primary-color);
  font-size: 1.05rem;
  flex-shrink: 0;
}

.settings-channel-actions {
  flex-wrap: wrap;
}

.settings-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 1.5rem;
  padding: 0.14rem 0.5rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  border: 1px solid transparent;
  white-space: nowrap;
  line-height: 1;
}

.settings-chip-neutral {
  color: var(--text-muted);
  background: rgba(161, 172, 184, 0.12);
  border-color: rgba(161, 172, 184, 0.18);
}

.settings-chip-primary {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.1);
  border-color: rgba(var(--primary-rgb), 0.18);
}

.settings-chip-success {
  color: #26b36a;
  background: rgba(38, 179, 106, 0.12);
  border-color: rgba(38, 179, 106, 0.18);
}

.settings-chip-warning {
  color: #ffb400;
  background: rgba(255, 180, 0, 0.12);
  border-color: rgba(255, 180, 0, 0.18);
}

.settings-chip-info {
  color: #0dcaf0;
  background: rgba(13, 202, 240, 0.12);
  border-color: rgba(13, 202, 240, 0.18);
}

.settings-guide-panel {
  margin-top: 1.5rem;
  padding-top: 1.35rem;
  border-top: 1px solid var(--divider-color);
}

.settings-guide-header {
  margin-bottom: 0.95rem;
}

.settings-guide-header h6 {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  color: var(--text-heading);
  font-weight: 700;
}

.settings-guide-item {
  height: 100%;
  padding: 1rem;
  border-radius: 0.9rem;
  border: 1px solid var(--border-color);
  background: var(--bg-surface-alt);
}

.settings-action-btn {
  display: inline-flex;
  align-items: center;
  min-height: 2.18rem;
  padding: 0.44rem 0.72rem;
  border-radius: 0.72rem;
  border: 1px solid transparent;
  font-size: 0.84rem;
  font-weight: 600;
  background: transparent;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
}

.settings-action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.settings-action-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.settings-action-primary {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.1);
  border-color: rgba(var(--primary-rgb), 0.18);
}

.settings-action-success {
  color: #26b36a;
  background: rgba(38, 179, 106, 0.12);
  border-color: rgba(38, 179, 106, 0.18);
}

.settings-action-warning {
  color: #ffb400;
  background: rgba(255, 180, 0, 0.12);
  border-color: rgba(255, 180, 0, 0.18);
}

.settings-action-danger {
  color: #ff5b5c;
  background: rgba(255, 91, 92, 0.1);
  border-color: rgba(255, 91, 92, 0.18);
}

.settings-action-neutral {
  color: var(--text-muted);
  background: rgba(161, 172, 184, 0.1);
  border-color: rgba(161, 172, 184, 0.18);
}

.settings-backup-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.35rem;
  flex-wrap: wrap;
}

.settings-backup-tools {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.settings-backup-toggle-card {
  margin-bottom: 1.35rem;
}

.settings-card-heading {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.settings-card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.settings-card-title-row .settings-toolbar-btn {
  margin-left: auto;
  flex: 0 0 auto;
}

.settings-card-title-row h3 {
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  color: var(--text-heading);
  font-size: 1.18rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.settings-card-heading p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.94rem;
  line-height: 1.65;
}

.settings-title-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.36rem 0.7rem;
  border-radius: 999px;
  color: var(--primary-color);
  background: rgba(var(--primary-rgb), 0.1);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.settings-title-count {
  font-size: 0.88rem;
  font-weight: 600;
  color: rgba(105, 122, 141, 0.72);
}

.settings-auth-body {
  padding: 1.5rem;
}

.settings-inline-note {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  margin-bottom: 1.25rem;
  padding: 1rem 1.1rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(13, 202, 240, 0.22);
  background: rgba(13, 202, 240, 0.08);
  color: var(--text-main);
}

.settings-inline-note > i {
  flex: 0 0 auto;
  color: #0dcaf0;
  font-size: 1.15rem;
}

.settings-inline-note-title {
  display: block;
  color: #0dcaf0;
  font-weight: 700;
  line-height: 1.5;
}

.settings-inline-note-text {
  margin-top: 0.25rem;
  color: #0dcaf0;
  font-size: 0.88rem;
  line-height: 1.65;
}

.settings-inline-note-text strong {
  color: #0dcaf0;
}

.settings-auth-toggle-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding: 1.1rem 1.15rem;
  border-radius: 0.95rem;
  background: var(--bg-surface-alt);
  border: 1px solid var(--border-color);
}

.settings-auth-toggle-copy {
  display: flex;
  flex-direction: column;
  gap: 0.22rem;
  min-width: 0;
}

.settings-field-label {
  color: var(--text-muted);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.settings-auth-toggle-copy strong {
  color: var(--text-heading);
  font-size: 1rem;
  font-weight: 700;
}

.settings-auth-toggle-copy p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.6;
}

.settings-auth-switch {
  flex: 0 0 auto;
}

.settings-auth-form-grid {
  display: grid;
  gap: 1.25rem;
}

.settings-form-block {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.2rem;
  border-radius: 0.95rem;
  border: 1px solid var(--border-color);
  background: var(--bg-surface-alt);
}

.settings-form-block-single {
  padding-bottom: 1rem;
}

.settings-block-heading {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.settings-block-heading-inline {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.settings-block-heading h4 {
  margin: 0;
  color: var(--text-heading);
  font-size: 1rem;
  font-weight: 700;
}

.settings-block-heading p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.88rem;
  line-height: 1.6;
}

.settings-mini-note {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.65rem;
  border-radius: 999px;
  background: rgba(var(--primary-rgb), 0.08);
  color: var(--primary-color);
  font-size: 0.76rem;
  font-weight: 600;
  white-space: nowrap;
}

.settings-password-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--primary-color);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.settings-password-divider::before,
.settings-password-divider::after {
  content: '';
  flex: 1;
  border-top: 1px solid var(--divider-color);
}

.settings-password-divider span {
  padding: 0 0.8rem;
}

.settings-field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.settings-field-grid-single {
  grid-template-columns: 1fr;
}

.settings-field-card {
  min-width: 0;
}

.settings-field-card-full {
  grid-column: 1 / -1;
}

.settings-form-label {
  margin-bottom: 0.55rem;
  color: var(--text-heading);
  font-size: 0.88rem;
  font-weight: 600;
}

.settings-input-group :deep(.input-group-text) {
  color: var(--primary-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, rgba(var(--primary-rgb), 0.08));
  border-color: var(--border-color);
  border-top-left-radius: 0.9rem;
  border-bottom-left-radius: 0.9rem;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.settings-input-group :deep(.form-control),
.settings-standalone-input {
  min-height: 2.9rem;
  border-color: var(--border-color);
  background: var(--bg-surface);
  color: color-mix(in srgb, var(--text-heading) 78%, var(--text-muted));
  -webkit-text-fill-color: color-mix(in srgb, var(--text-heading) 78%, var(--text-muted));
  box-shadow: none;
  border-radius: 0.9rem;
}

.settings-input-group :deep(.form-control) {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-top-right-radius: 0.9rem;
  border-bottom-right-radius: 0.9rem;
}

.settings-backup-card .settings-standalone-input,
.settings-backup-card .settings-standalone-input.font-monospace,
.settings-backup-card :deep(input.form-control) {
  color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
  -webkit-text-fill-color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
}

.settings-backup-card :deep(.cron-input-wrapper .form-control),
.settings-backup-card :deep(.cron-input-wrapper .input-group-text) {
  min-height: 2.9rem;
}

.settings-input-group :deep(.form-control::placeholder),
.settings-standalone-input::placeholder {
  color: color-mix(in srgb, var(--text-muted) 88%, transparent);
}

.settings-backup-card .settings-standalone-input::placeholder,
.settings-backup-card :deep(input.form-control::placeholder) {
  color: color-mix(in srgb, var(--text-muted) 76%, transparent);
}

.settings-input-group :deep(.form-control:focus),
.settings-standalone-input:focus {
  border-color: rgba(var(--primary-rgb), 0.34);
  box-shadow: 0 0 0 0.2rem rgba(var(--primary-rgb), 0.12);
}

.settings-field-hint {
  margin-top: 0.45rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.6;
}

.settings-auth-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.25rem;
}

.settings-save-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  min-height: 2.32rem;
  padding: 0.54rem 0.92rem;
  border: none;
  border-radius: 0.8rem;
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.98), rgba(var(--primary-rgb), 0.82));
  color: #fff;
  font-size: 0.92rem;
  line-height: 1;
  font-weight: 600;
  box-shadow: 0 0.75rem 1.6rem rgba(var(--primary-rgb), 0.24);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), opacity var(--transition-fast);
}

.settings-save-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0.95rem 1.8rem rgba(var(--primary-rgb), 0.28);
}

.settings-save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon {
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.transition-hover {
  transition: all var(--transition-fast);
}

.transition-hover:hover {
  background: rgba(var(--primary-rgb), 0.05) !important;
  transform: translateY(-2px);
}

.backup-item:focus {
  outline: none;
  box-shadow: none;
  background-color: rgba(var(--primary-rgb), 0.05);
}

.switch {
  --switch-width: 46px;
  --switch-height: 24px;
  --switch-bg: rgba(161, 172, 184, 0.42);
  --switch-checked-bg: linear-gradient(135deg, color-mix(in srgb, var(--success-color) 86%, #3dd598) 0%, var(--success-color) 100%);
  --switch-offset: calc((var(--switch-height) - var(--circle-diameter)) / 2);
  --switch-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
  --circle-diameter: 18px;
  --circle-bg: #fff;
  --circle-shadow: 0 0.125rem 0.5rem rgba(67, 89, 113, 0.24);
  --circle-checked-shadow: 0 0.125rem 0.75rem rgba(74, 179, 126, 0.3);
  --circle-transition: var(--switch-transition);
  --icon-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
  --icon-cross-color: var(--switch-bg);
  --icon-cross-size: 6px;
  --icon-checkmark-color: var(--success-color);
  --icon-checkmark-size: 10px;
  --effect-width: calc(var(--circle-diameter) / 2);
  --effect-height: calc(var(--effect-width) / 2 - 1px);
  --effect-bg: var(--circle-bg);
  --effect-border-radius: 1px;
  --effect-transition: all .2s ease-in-out;
}

.switch input {
  display: none;
}

.switch {
  display: inline-block;
}

.switch svg {
  -webkit-transition: var(--icon-transition);
  -o-transition: var(--icon-transition);
  transition: var(--icon-transition);
  position: absolute;
  top: 50%;
  left: 50%;
  height: auto;
}

.switch .checkmark {
  width: var(--icon-checkmark-size);
  color: var(--icon-checkmark-color);
  -webkit-transform: translate(-50%, -50%) scale(0);
  -ms-transform: translate(-50%, -50%) scale(0);
  transform: translate(-50%, -50%) scale(0);
}

.switch .cross {
  width: var(--icon-cross-size);
  color: var(--icon-cross-color);
  -webkit-transform: translate(-50%, -50%) scale(1);
  -ms-transform: translate(-50%, -50%) scale(1);
  transform: translate(-50%, -50%) scale(1);
}

.slider {
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
  width: var(--switch-width);
  height: var(--switch-height);
  background: var(--switch-bg);
  border-radius: 999px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  position: relative;
  -webkit-transition: var(--switch-transition);
  -o-transition: var(--switch-transition);
  transition: var(--switch-transition);
  cursor: pointer;
}

.circle {
  width: var(--circle-diameter);
  height: var(--circle-diameter);
  background: var(--circle-bg);
  border-radius: inherit;
  -webkit-box-shadow: var(--circle-shadow);
  box-shadow: var(--circle-shadow);
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  -webkit-box-pack: center;
  -ms-flex-pack: center;
  justify-content: center;
  -webkit-transition: var(--circle-transition);
  -o-transition: var(--circle-transition);
  transition: var(--circle-transition);
  z-index: 1;
  position: absolute;
  top: 50%;
  left: var(--switch-offset);
  -webkit-transform: translateY(-50%);
  -ms-transform: translateY(-50%);
  transform: translateY(-50%);
}

.slider::before {
  content: "";
  position: absolute;
  width: var(--effect-width);
  height: var(--effect-height);
  top: 50%;
  left: calc(var(--switch-offset) + (var(--effect-width) / 2));
  background: var(--effect-bg);
  border-radius: var(--effect-border-radius);
  -webkit-transition: var(--effect-transition);
  -o-transition: var(--effect-transition);
  transition: var(--effect-transition);
  -webkit-transform: translateY(-50%);
  -ms-transform: translateY(-50%);
  transform: translateY(-50%);
}

.switch input:checked+.slider {
  background: var(--switch-checked-bg);
}

.switch input:checked+.slider .checkmark {
  -webkit-transform: translate(-50%, -50%) scale(1);
  -ms-transform: translate(-50%, -50%) scale(1);
  transform: translate(-50%, -50%) scale(1);
}

.switch input:checked+.slider .cross {
  -webkit-transform: translate(-50%, -50%) scale(0);
  -ms-transform: translate(-50%, -50%) scale(0);
  transform: translate(-50%, -50%) scale(0);
}

.switch input:checked+.slider::before {
  left: calc(100% - var(--effect-width) - (var(--effect-width) / 2) - var(--switch-offset));
}

.switch input:checked+.slider .circle {
  left: calc(100% - var(--circle-diameter) - var(--switch-offset));
  -webkit-box-shadow: var(--circle-checked-shadow);
  box-shadow: var(--circle-checked-shadow);
}

.backup-item {
  transition: all var(--transition-fast);
  border: 1px solid transparent !important;
}

.backup-item:hover {
  background-color: rgba(var(--primary-rgb), 0.08) !important;
  border-color: rgba(var(--primary-rgb), 0.28) !important;
  transform: translateY(-2px);
}

.glass-effect {
  background: var(--bg-surface-alt);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
}

@media (max-width: 767.98px) {
  .workspace-card-header.settings-auth-header,
  .workspace-card-header.settings-section-header,
  .settings-auth-body,
  .settings-section-body {
    padding: 1.1rem;
  }

  .settings-inline-note,
  .settings-auth-toggle-card,
  .settings-form-block {
    padding: 1rem;
  }

  .settings-inline-note {
    align-items: flex-start;
  }

  .settings-auth-toggle-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .settings-section-header-split {
    flex-direction: column;
  }

  .settings-toolbar-btn,
  .settings-action-btn,
  .settings-backup-tools,
  .settings-backup-actions {
    width: 100%;
  }

  .settings-card-title-row .settings-toolbar-btn {
    width: auto;
    padding-inline: 0.7rem;
    white-space: nowrap;
  }

  .settings-backup-tools {
    flex-direction: row;
    align-items: stretch;
    flex-wrap: nowrap;
    gap: 0.45rem;
  }

  .settings-backup-tools .settings-action-btn {
    width: auto;
    min-width: 0;
    flex: 1 1 0;
    padding-inline: 0.4rem;
    white-space: nowrap;
  }

  .settings-channel-actions {
    flex-wrap: nowrap;
    justify-content: space-between !important;
    gap: 0.45rem !important;
  }

  .settings-channel-actions .settings-action-btn {
    width: auto;
    min-width: 0;
    flex: 1 1 0;
    padding-inline: 0.4rem;
    white-space: nowrap;
  }

  .settings-channel-actions {
    padding-left: 0 !important;
  }

  .settings-chip {
    min-height: 1.22rem;
    padding: 0.06rem 0.36rem;
    font-size: 0.62rem;
  }

  .settings-auth-switch {
    align-self: flex-end;
  }

  .settings-field-grid {
    grid-template-columns: 1fr;
  }

  .settings-auth-actions {
    justify-content: stretch;
  }

  .settings-save-btn {
    width: 100%;
  }
}
</style>
