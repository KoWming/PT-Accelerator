<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">系统设置</h2>
    </div>

    <!-- Tabs Navigation -->
    <div class="settings-tabs mb-4 d-flex gap-4 border-bottom border-secondary border-opacity-10" ref="tabsRef">
      <div class="tab-glider" :style="tabGliderStyle"></div>
      <button 
        class="btn btn-link nav-link px-0 pb-3 rounded-0 fw-bold position-relative" 
        :class="{ 'active': activeTab === 'system' }"
        @click="activeTab = 'system'"
      >
        系统设置
      </button>
      <button 
        class="btn btn-link nav-link px-0 pb-3 rounded-0 fw-bold position-relative" 
        :class="{ 'active': activeTab === 'notification' }"
        @click="activeTab = 'notification'"
      >
        通知设置
      </button>
      <button 
        class="btn btn-link nav-link px-0 pb-3 rounded-0 fw-bold position-relative" 
        :class="{ 'active': activeTab === 'backup' }"
        @click="activeTab = 'backup'"
      >
        备份设置
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- System Settings Tab -->
      <transition name="fade" mode="out-in">
        <div v-if="activeTab === 'system'" key="system">
          <div class="card shadow-sm">
            <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0">
              <h5 class="mb-0 fw-bold"><i class="bi bi-shield-lock me-2 text-primary"></i>安全与认证</h5>
            </div>
            <div class="card-body p-4">
              <form @submit.prevent="saveAuthSettings">
                <div class="alert bg-info bg-opacity-10 border border-info border-opacity-25 text-main mb-4" role="alert">
                  <div class="d-flex">
                    <i class="bi bi-info-circle-fill text-info me-3 fs-5"></i>
                    <div>
                      <span class="fw-bold text-info">启用登录认证后，所有访问此控制面板的操作都需要验证身份。</span>
                      <div class="mt-2 small opacity-75">
                        <strong>注意:</strong> 如果管理员密码尚未设置，启用认证时请自行输入新密码。若留空，系统将自动生成一个初始密码并打印在应用日志中。
                      </div>
                    </div>
                  </div>
                </div>
                <div class="form-check form-switch mb-4 p-3 bg-dark-glass rounded-3 border border-secondary border-opacity-10 d-flex align-items-center">
                  <label class="switch me-3">
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
                  <label class="form-check-label fw-medium cursor-pointer" for="auth-enable">启用登录认证</label>
                </div>
                
                <transition name="fade">
                  <div v-if="authForm.enable_auth">
                    <div class="mb-3">
                      <label class="form-label">用户名</label>
                      <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-person"></i></span>
                        <input type="text" class="form-control" v-model="authForm.username">
                      </div>
                    </div>
                    
                    <div class="my-4 d-flex align-items-center">
                      <hr class="flex-grow-1 border-secondary opacity-25 m-0">
                      <span class="px-2 text-primary small fw-bold">修改密码</span>
                      <hr class="flex-grow-1 border-secondary opacity-25 m-0">
                    </div>

                      <div class="mb-3">
                        <label class="form-label">当前密码</label>
                        <div class="input-group">
                          <span class="input-group-text"><i class="bi bi-key"></i></span>
                          <input type="password" class="form-control" v-model="authForm.current_password" placeholder="留空则不修改">
                        </div>
                        <div class="form-text text-muted small mt-1">如果首次设置密码或认证被禁用时更改密码，则无需当前密码。</div>
                      </div>
                    <div class="row g-3 mb-3">
                      <div class="col-md-6">
                        <label class="form-label">新密码</label>
                        <input type="password" class="form-control" v-model="authForm.new_password">
                        <div class="form-text text-muted small mt-1">密码要求：至少8位字符，建议包含大小写字母、数字和特殊字符</div>
                      </div>
                      <div class="col-md-6">
                        <label class="form-label">确认新密码</label>
                        <input type="password" class="form-control" v-model="authForm.confirm_password">
                      </div>
                    </div>
                  </div>
                </transition>
                
                <div class="mt-4 text-end">
                  <button type="submit" class="save-config-btn" :disabled="savingAuth">
                    <span v-if="savingAuth" class="spinner-border spinner-border-sm me-2"></span>
                    <span v-else><i class="bi bi-check-lg me-2"></i>保存设置</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Notification Settings Tab -->
        <div v-else-if="activeTab === 'notification'" key="notification">
          <div class="card shadow-sm">
            <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0 d-flex justify-content-between align-items-center">
              <h5 class="mb-0 fw-bold"><i class="bi bi-bell me-2 text-warning"></i>通知渠道</h5>
              <button class="btn-pill btn-pill-primary btn-sm" @click="openAddModal">
                <i class="bi bi-plus-lg me-1"></i> 添加渠道
              </button>
            </div>
            <div class="card-body p-4">
              <div v-if="Object.keys(notifyChannels).length === 0" class="text-center py-5 text-muted bg-dark-glass rounded-3 border border-dashed border-secondary border-opacity-25">
                <i class="bi bi-bell-slash fs-1 d-block mb-3 opacity-50"></i>
                暂无通知渠道
              </div>

              <div v-else class="list-group list-group-flush gap-2">
                <div v-for="(channel, key) in notifyChannels" :key="key" class="list-group-item bg-dark-glass border border-secondary border-opacity-10 rounded-3 p-3 transition-hover">
                  <div class="d-flex flex-column flex-md-row gap-3">
                    <!-- Left Side: Icon + Info + Switch -->
                    <div class="d-flex align-items-center flex-grow-1 min-width-0">
                      <div class="icon-square bg-secondary bg-opacity-10 text-secondary me-3 rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width: 40px; height: 40px;">
                        <i class="bi" :class="getChannelIcon(String(channel.type))"></i>
                      </div>
                      <div class="flex-grow-1 min-width-0">
                        <!-- Row 1: Name + Switch -->
                        <div class="d-flex justify-content-between align-items-center mb-1">
                          <h6 class="mb-0 fw-semibold text-break me-2">{{ channel.name || key }}</h6>
                          
                          <!-- Enable Switch (Mobile Only) -->
                          <div class="flex-shrink-0 ps-2 d-md-none">
                            <label class="switch">
                                <input type="checkbox" :checked="channel.enable" @change="toggleChannel(String(key))">
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
                          </div>
                        </div>

                        <!-- Row 2: Tags + Summary -->
                        <div class="d-flex align-items-center flex-wrap gap-2 small text-muted">
                          <div class="d-flex gap-2 align-items-center">
                            <span class="badge bg-secondary bg-opacity-10 text-secondary border border-secondary border-opacity-10">{{ channel.type }}</span>
                            <span v-if="channel.HITOKOTO" class="badge rounded-pill bg-primary bg-opacity-10 text-primary border border-primary border-opacity-10">
                              一言
                            </span>
                          </div>
                          <span class="text-truncate d-inline-block" style="max-width: 100%;">{{ getChannelSummary(channel) }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- Right Side (Desktop) / Bottom (Mobile): Action Buttons -->
                    <div class="d-flex align-items-center justify-content-end gap-2 ps-md-3 border-start-md border-secondary border-opacity-10 w-100 w-md-auto mt-2 mt-md-0">
                      <!-- Enable Switch (Desktop Only) -->
                      <div class="d-none d-md-block me-2">
                        <label class="switch">
                            <input type="checkbox" :checked="channel.enable" @change="toggleChannel(String(key))">
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
                      </div>
                      <button class="btn-pill btn-pill-success btn-sm flex-grow-1 flex-md-grow-0 justify-content-center" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" @click="testChannel(String(key))" :disabled="testingChannel === String(key)">
                        <span v-if="testingChannel === String(key)" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-send me-1"></i> 测试
                      </button>
                      <button class="btn-pill btn-pill-primary btn-sm flex-grow-1 flex-md-grow-0 justify-content-center" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" @click="editChannel(String(key))">
                        <i class="bi bi-pencil me-1"></i> 编辑
                      </button>
                      <button class="btn-pill btn-pill-danger btn-sm flex-grow-1 flex-md-grow-0 justify-content-center" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" @click="deleteChannel(String(key))">
                        <i class="bi bi-trash me-1"></i> 删除
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
            </div>
          </div>
        </div>

        <!-- Backup Settings Tab -->
        <div v-else-if="activeTab === 'backup'" key="backup">
          <div class="card shadow-sm">
            <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0">
              <h5 class="mb-0 fw-bold"><i class="bi bi-cloud-arrow-up me-2 text-info"></i>备份设置</h5>
            </div>
            <div class="card-body p-4">
              <form @submit.prevent="saveBackupSettings">
                <div class="alert bg-info bg-opacity-10 border border-info border-opacity-25 text-main mb-4" role="alert">
                  <div class="d-flex">
                    <i class="bi bi-info-circle-fill text-info me-3 fs-5"></i>
                    <div style="min-width: 0;">
                      <span class="fw-bold text-info">配置WebDav以备份系统配置。</span>
                      <div class="mt-2 small opacity-75 text-break">
                        支持定时自动备份和手动立即备份。备份文件将保存为 config_YYYYMMDD_HHMMSS.yaml。
                      </div>
                    </div>
                  </div>
                </div>

                <div class="form-check form-switch mb-4 p-3 bg-dark-glass rounded-3 border border-secondary border-opacity-10 d-flex align-items-center">
                  <label class="switch me-3">
                      <input type="checkbox" id="backup-enable" v-model="backupForm.enable">
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
                  <label class="form-check-label fw-medium cursor-pointer" for="backup-enable">启用配置备份</label>
                </div>

                <transition name="fade">
                  <div v-if="backupForm.enable">
                    <div class="mb-3">
                      <label class="form-label">WebDav URL</label>
                      <input type="text" class="form-control" v-model="backupForm.webdav_url" placeholder="https://example.com/dav/">
                    </div>
                    <div class="row g-3 mb-3">
                      <div class="col-md-6">
                        <label class="form-label">用户名</label>
                        <input type="text" class="form-control" v-model="backupForm.webdav_username">
                      </div>
                      <div class="col-md-6">
                        <label class="form-label">密码</label>
                        <input type="password" class="form-control" v-model="backupForm.webdav_password">
                      </div>
                    </div>
                    <div class="row g-3 mb-4">
                      <div class="col-md-6">
                        <label class="form-label">备份保留份数</label>
                        <input type="number" class="form-control" v-model.number="backupForm.backup_count" min="1" placeholder="5">
                        <div class="form-text text-muted">当备份数量超过此限制时，将自动删除最旧的备份。默认保留 5 份。</div>
                      </div>
                      <div class="col-md-6">
                        <label class="form-label">Cron 表达式 (自动备份时间)</label>
                        <input type="text" class="form-control font-monospace" v-model="backupForm.cron" placeholder="0 2 * * *">
                        <div class="form-text text-muted">默认为每天凌晨 2:00 (0 2 * * *)</div>
                      </div>
                    </div>
                  </div>
                </transition>

                <div class="d-flex flex-column flex-md-row justify-content-between mt-4 gap-3">
                  <div class="d-flex flex-column flex-md-row gap-2">
                     <button type="button" class="btn-pill btn-pill-secondary" style="white-space: nowrap;" @click="testBackupConnection" :disabled="testingConnection || !backupForm.webdav_url">
                      <span v-if="testingConnection" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bi bi-plug me-2"></i>测试连接
                    </button>
                    <button type="button" class="btn-pill btn-pill-success" style="white-space: nowrap;" @click="runBackupNow" :disabled="runningBackup || !backupForm.enable">
                      <span v-if="runningBackup" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bi bi-play-fill me-2"></i>立即备份
                    </button>
                    <button type="button" class="btn-pill btn-pill-warning" style="white-space: nowrap;" @click="openBackupModal" :disabled="loadingBackups || !backupForm.webdav_url">
                      <span v-if="loadingBackups" class="spinner-border spinner-border-sm me-2"></span>
                      <i v-else class="bi bi-arrow-counterclockwise me-2"></i>备份恢复
                    </button>
                  </div>
                  <button type="submit" class="btn-pill btn-pill-primary" style="white-space: nowrap;" :disabled="savingBackup">
                    <span v-if="savingBackup" class="spinner-border spinner-border-sm me-2"></span>
                    <span v-else><i class="bi bi-check-lg me-2"></i>保存设置</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
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
                  <i class="bi bi-arrow-counterclockwise"></i>
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
import { ref, reactive, onMounted, watch, nextTick } from 'vue';
import axios from '../../api/axios';
import NotificationForm from '../../components/NotificationForm.vue';
import { useToast } from 'vue-toastification';
import { useConfirm } from '../../composables/useConfirm';

const activeTab = ref('system');
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

// Tab Glider Logic
const tabGliderStyle = ref({
  width: '0px',
  transform: 'translateX(0px)',
  opacity: 0
});
const tabsRef = ref<HTMLElement | null>(null);

const updateTabGlider = () => {
  if (!tabsRef.value) return;
  
  const activeBtn = tabsRef.value.querySelector('.nav-link.active') as HTMLElement;
  if (activeBtn) {
    const containerRect = tabsRef.value.getBoundingClientRect();
    const btnRect = activeBtn.getBoundingClientRect();
    
    const left = btnRect.left - containerRect.left;
    const width = btnRect.width;
    
    tabGliderStyle.value = {
      width: `${width}px`,
      transform: `translateX(${left}px)`,
      opacity: 1
    };
  }
};

watch(activeTab, () => {
  nextTick(() => {
    updateTabGlider();
  });
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
    
  // Initialize glider
  nextTick(() => {
    updateTabGlider();
  });
  window.addEventListener('resize', updateTabGlider);
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
    case 'bark': return 'bi-megaphone';
    case 'telegram': return 'bi-telegram';
    case 'wecom_bot': case 'wecom_app': return 'bi-chat-dots';
    case 'smtp': return 'bi-envelope';
    case 'wxpusher': return 'bi-chat-square-text';
    case 'gotify': return 'bi-broadcast';
    default: return 'bi-bell';
  }
};
</script>

<style scoped>
.btn-icon {
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.transition-hover {
  transition: all 0.2s ease;
}

.transition-hover:hover {
  background: rgba(var(--text-main), 0.05) !important;
  transform: translateX(2px);
}

.backup-item:focus {
  outline: none;
  box-shadow: none;
  background-color: rgba(var(--text-main), 0.05);
}

/* Custom Switch Styles */
.switch {
  /* switch */
  --switch-width: 46px;
  --switch-height: 24px;
  --switch-bg: rgb(131, 131, 131);
  --switch-checked-bg: rgb(0, 218, 80);
  --switch-offset: calc((var(--switch-height) - var(--circle-diameter)) / 2);
  --switch-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
  /* circle */
  --circle-diameter: 18px;
  --circle-bg: #fff;
  --circle-shadow: 1px 1px 2px rgba(146, 146, 146, 0.45);
  --circle-checked-shadow: -1px 1px 2px rgba(163, 163, 163, 0.45);
  --circle-transition: var(--switch-transition);
  /* icon */
  --icon-transition: all .2s cubic-bezier(0.27, 0.2, 0.25, 1.51);
  --icon-cross-color: var(--switch-bg);
  --icon-cross-size: 6px;
  --icon-checkmark-color: var(--switch-checked-bg);
  --icon-checkmark-size: 10px;
  /* effect line */
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
  height: auto;
}

.switch .checkmark {
  width: var(--icon-checkmark-size);
  color: var(--icon-checkmark-color);
  -webkit-transform: scale(0);
  -ms-transform: scale(0);
  transform: scale(0);
}

.switch .cross {
  width: var(--icon-cross-size);
  color: var(--icon-cross-color);
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
  left: var(--switch-offset);
}

.slider::before {
  content: "";
  position: absolute;
  width: var(--effect-width);
  height: var(--effect-height);
  left: calc(var(--switch-offset) + (var(--effect-width) / 2));
  background: var(--effect-bg);
  border-radius: var(--effect-border-radius);
  -webkit-transition: var(--effect-transition);
  -o-transition: var(--effect-transition);
  transition: var(--effect-transition);
}

.switch input:checked+.slider {
  background: var(--switch-checked-bg);
}

.switch input:checked+.slider .checkmark {
  -webkit-transform: scale(1);
  -ms-transform: scale(1);
  transform: scale(1);
}

.switch input:checked+.slider .cross {
  -webkit-transform: scale(0);
  -ms-transform: scale(0);
  transform: scale(0);
}

.switch input:checked+.slider::before {
  left: calc(100% - var(--effect-width) - (var(--effect-width) / 2) - var(--switch-offset));
}

.switch input:checked+.slider .circle {
  left: calc(100% - var(--circle-diameter) - var(--switch-offset));
  -webkit-box-shadow: var(--circle-checked-shadow);
  box-shadow: var(--circle-checked-shadow);
}

/* Tab Glider Styles */
.settings-tabs {
  position: relative;
}

.tab-glider {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--primary-color);
  border-radius: 3px 3px 0 0;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 -2px 10px rgba(163, 112, 247, 0.5);
  z-index: 10;
}

.nav-link {
  color: var(--text-muted);
  transition: color 0.2s ease;
  border-bottom: 3px solid transparent; /* Reserve space but transparent */
}

.nav-link:hover {
  color: var(--text-main);
}

.nav-link.active {
  color: var(--primary-color) !important;
  /* Border handled by glider */
  border-bottom-color: transparent !important; 
}

.backup-item {
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.backup-item:hover {
  background-color: rgba(var(--primary-color-rgb), 0.1) !important;
  border-color: var(--primary-color);
  transform: translateX(5px);
}

.glass-effect {
  background: var(--bg-surface-glass, rgba(30, 41, 59, 0.9));
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
}
</style>
