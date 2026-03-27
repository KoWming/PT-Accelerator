<template>
  <Teleport to="body">
    <div class="modal fade show d-block notification-modal" tabindex="-1" @click.self="$emit('close')">
      <div class="modal-dialog modal-lg modal-dialog-centered notification-modal-dialog">
        <div class="modal-content notification-modal-content">
          <div class="modal-header notification-modal-header">
            <div class="notification-modal-title-wrap">
              <h5 class="modal-title">{{ isEdit ? '编辑' : '添加' }}通知渠道</h5>
              <p>统一配置通知渠道类型、鉴权信息与启用状态，保存后即可参与消息推送。</p>
            </div>
            <button type="button" class="btn-close notification-modal-close" @click="$emit('close')"></button>
          </div>
          <div class="modal-body notification-modal-body">
            <form @submit.prevent="save" class="notification-modal-form">
              <section class="notification-form-panel notification-form-panel-main">
                <div class="notification-form-panel-head notification-form-panel-head-inline">
                  <h6>基础配置</h6>
                  <div class="form-check form-switch notification-switch-item notification-switch-item-inline notification-switch-item-compact">
                    <input type="checkbox" class="form-check-input" id="enable" v-model="form.enable">
                    <label class="form-check-label" for="enable">启用</label>
                  </div>
                </div>

                <div class="row g-3">
                <div class="col-md-6 mb-3">
                  <label class="form-label">渠道名称 (备注) <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bx bx-purchase-tag-alt"></i></span>
                    <input type="text" class="form-control" v-model="form.name" required placeholder="例如：自定义通知">
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">通知类型 <span class="text-danger">*</span></label>
                  <div ref="typeWrapperRef" class="notification-type-wrapper position-relative">
                    <div class="input-group notification-input-group notification-type-group" :class="{ 'is-disabled': isEdit }">
                      <span class="input-group-text"><i class="bx bx-broadcast"></i></span>
                      <button
                        type="button"
                        class="form-control notification-type-trigger"
                        :disabled="isEdit"
                        @click="toggleTypeDropdown"
                      >
                        <span :class="{ 'is-placeholder': !form.type }">{{ selectedTypeLabel }}</span>
                        <i class="bx bx-chevron-down" :class="{ 'is-open': typeDropdownOpen }"></i>
                      </button>
                    </div>

                    <transition name="cron-dropdown">
                      <div v-if="typeDropdownOpen && !isEdit" class="notification-type-dropdown">
                        <div class="notification-type-dropdown-note">
                          <strong>通知类型</strong>
                          <span>默认选择企业微信机器人，可切换其他渠道类型。</span>
                        </div>
                        <button
                          v-for="type in notificationTypeOptions"
                          :key="type.value"
                          type="button"
                          class="notification-type-option"
                          :class="{ 'is-active': form.type === type.value }"
                          @click="selectNotificationType(type.value)"
                        >
                          <strong>{{ type.label }}</strong>
                          <span>{{ type.value }}</span>
                        </button>
                      </div>
                    </transition>
                  </div>
                </div>
              </div>
              </section>

              <section class="notification-form-panel notification-form-panel-subtle">
                <div class="notification-form-panel-head notification-form-panel-head-inline">
                  <h6>渠道参数</h6>
                  <div class="form-check form-switch notification-switch-item notification-switch-item-inline notification-switch-item-compact">
                    <input type="checkbox" class="form-check-input" id="hitokoto" v-model="form.HITOKOTO">
                    <label class="form-check-label" for="hitokoto">一言</label>
                  </div>
                </div>

              <!-- Bark Fields -->
              <div v-if="form.type === 'bark'">
                <div class="mb-3">
                  <label class="form-label">Bark 推送地址或设备码 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bx bx-mobile-alt"></i></span>
                    <input type="text" class="form-control" v-model="form.BARK_PUSH" required placeholder="https://api.day.app/DxHcxxxxx...">
                  </div>
                  <div class="form-text">填入完整的 URL 或 Key</div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">分组 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-collection"></i></span>
                      <input type="text" class="form-control" v-model="form.BARK_GROUP" placeholder="默认: PT-Accelerator">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">声音 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-volume-full"></i></span>
                      <input type="text" class="form-control" v-model="form.BARK_SOUND">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">图标URL (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-image"></i></span>
                      <input type="text" class="form-control" v-model="form.BARK_ICON" placeholder="https://day.app/assets/images/avatar.jpg">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">时效性 (可选)</label>
                    <div ref="barkLevelWrapperRef" class="notification-type-wrapper position-relative">
                      <div class="input-group notification-input-group notification-type-group">
                      <span class="input-group-text"><i class="bx bx-time-five"></i></span>
                        <button
                          type="button"
                          class="form-control notification-type-trigger"
                          @click="toggleDropdown('barkLevel')"
                        >
                          <span :class="{ 'is-placeholder': !form.BARK_LEVEL }">{{ selectedBarkLevelLabel }}</span>
                          <i class="bx bx-chevron-down" :class="{ 'is-open': dropdownOpen.barkLevel }"></i>
                        </button>
                      </div>

                      <transition name="cron-dropdown">
                        <div v-if="dropdownOpen.barkLevel" class="notification-type-dropdown notification-type-dropdown-compact">
                          <div class="notification-type-dropdown-note">
                            <strong>时效性</strong>
                            <span>选择 Bark 推送展示优先级与亮屏方式。</span>
                          </div>
                          <button
                            v-for="option in barkLevelOptions"
                            :key="option.value || 'default'"
                            type="button"
                            class="notification-type-option"
                            :class="{ 'is-active': form.BARK_LEVEL === option.value }"
                            @click="selectDropdownOption('barkLevel', option.value, 'BARK_LEVEL')"
                          >
                            <strong>{{ option.label }}</strong>
                            <span>{{ option.meta }}</span>
                          </button>
                        </div>
                      </transition>
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">跳转URL (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-link-alt"></i></span>
                      <input type="text" class="form-control" v-model="form.BARK_URL">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3 bark-archive-col">
                    <label class="form-label bark-archive-label-placeholder" aria-hidden="true">存档</label>
                    <div class="form-check d-flex align-items-center bark-archive-check">
                      <input type="checkbox" class="form-check-input notification-checkbox-input" id="bark_archive" v-model="form.BARK_ARCHIVE" true-value="1" false-value="0">
                      <label class="form-check-label" for="bark_archive">存档 (BARK_ARCHIVE)</label>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Telegram Fields -->
              <div v-if="form.type === 'telegram'">
                <div class="mb-3">
                  <label class="form-label">机器人的TOKEN <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bx bx-bot"></i></span>
                    <input type="text" class="form-control" v-model="form.TG_BOT_TOKEN" required>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">机器人的ID <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-id-card"></i></span>
                      <input type="text" class="form-control" v-model="form.TG_USER_ID" required>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">API代理地址 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-globe"></i></span>
                      <input type="text" class="form-control" v-model="form.TG_API_HOST" placeholder="默认: https://api.telegram.org">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">HTTP代理主机 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-network-chart"></i></span>
                      <input type="text" class="form-control" v-model="form.TG_PROXY_HOST" placeholder="代理主机">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">HTTP代理端口 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-plug"></i></span>
                      <input type="text" class="form-control" v-model="form.TG_PROXY_PORT" placeholder="代理端口">
                    </div>
                  </div>
                </div>
                <div class="form-text field-tip">说明：默认使用官方地址 https://api.telegram.org，如需自建代理或使用代理服务器可填写相应配置。</div>
              </div>

              <!-- iGot Fields -->
              <div v-if="form.type === 'igot'">
                <div class="mb-3">
                  <label class="form-label">Push Key <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bx bx-key"></i></span>
                    <input type="text" class="form-control" v-model="form.IGOT_PUSH_KEY" required>
                  </div>
                  <div class="form-text field-tip">在 iGot 平台获取 PUSH_KEY，格式通常为一串字母数字。</div>
                </div>
              </div>

              <!-- DingDing Fields -->
              <div v-if="form.type === 'dingding'">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">DD_BOT_TOKEN <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-bot"></i></span>
                      <input type="text" class="form-control" v-model="form.DD_BOT_TOKEN" required>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">DD_BOT_SECRET <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-key"></i></span>
                      <input type="text" class="form-control" v-model="form.DD_BOT_SECRET" required>
                    </div>
                  </div>
                </div>
                <div class="form-text field-tip">在钉钉群自定义机器人中获取 Token 与加签 Secret。</div>
              </div>

              <!-- Feishu Fields -->
              <div v-if="form.type === 'feishu'">
                <div class="mb-3">
                  <label class="form-label">飞书机器人 FSKEY <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bx bx-bot"></i></span>
                    <input type="text" class="form-control" v-model="form.FSKEY" required>
                  </div>
                  <div class="form-text field-tip">在飞书群机器人的设置中获取 FSKEY。</div>
                </div>
              </div>

              <!-- WeCom Bot Fields -->
              <div v-if="form.type === 'wecom_bot'">
                <div class="mb-3">
                  <label class="form-label">企业微信机器人Key <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bx bx-key"></i></span>
                    <input type="text" class="form-control" v-model="form.QYWX_KEY" required>
                  </div>
                </div>
              </div>

              <!-- WeCom App Fields -->
              <div v-if="form.type === 'wecom_app'">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">企业ID (corpid)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-buildings"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.corpid" placeholder="企业ID">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">应用Secret (corpsecret)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-key"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.corpsecret" placeholder="应用Secret">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">接收者 (touser 或 @all)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-user"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.touser" placeholder="接收者">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">应用AgentID (agentid)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-bot"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.agentid" placeholder="应用AgentID">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">图文素材 media_id (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-image-alt"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.media_id" placeholder="图文素材media_id">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">转发代理地址 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-globe"></i></span>
                      <input type="text" class="form-control" v-model="form.QYWX_ORIGIN" placeholder="https://qyapi.weixin.qq.com">
                    </div>
                  </div>
                </div>
                <div class="form-text field-tip">将以上字段组合为 QYWX_AM: corpid,corpsecret,touser,agentid[,media_id]</div>
                <div class="form-text field-tip">说明：企业微信消息的转发代理地址，2022年6月20日后创建的自建应用才需要，其他情况请保持默认 https://qyapi.weixin.qq.com</div>
              </div>

              <!-- SMTP Fields -->
              <div v-if="form.type === 'smtp'">
                <div class="row">
                  <div class="col-md-6 mb-3">
                      <label class="form-label">SMTP服务器(可加端口) <span class="text-danger">*</span></label>
                      <div class="input-group">
                        <span class="input-group-text"><i class="bx bx-network-chart"></i></span>
                        <input type="text" class="form-control" v-model="form.SMTP_SERVER" required placeholder="smtp.exmail.qq.com:465">
                      </div>
                  </div>
                  <div class="col mb-3 smtp-name-col">
                      <label class="form-label">发件人名称(可选)</label>
                      <div class="input-group">
                        <span class="input-group-text"><i class="bx bx-user"></i></span>
                        <input type="text" class="form-control" v-model="form.SMTP_NAME">
                      </div>
                  </div>
                  <div class="col-auto mb-3 smtp-ssl-col">
                    <label class="form-label bark-archive-label-placeholder" aria-hidden="true">启用SSL</label>
                    <div class="form-check d-flex align-items-center bark-archive-check smtp-ssl-check">
                      <input
                        class="form-check-input notification-checkbox-input"
                        type="checkbox"
                        id="smtp_ssl"
                        v-model="smtpSslEnabled"
                      >
                      <label class="form-check-label" for="smtp_ssl">启用SSL</label>
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">邮箱 <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-envelope"></i></span>
                      <input type="email" class="form-control" v-model="form.SMTP_EMAIL" required>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">密码/授权码 <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-key"></i></span>
                      <input type="password" class="form-control" v-model="form.SMTP_PASSWORD" required>
                    </div>
                  </div>
                </div>
                <div class="form-text field-tip">说明：若服务器地址未包含端口且填写了端口，将自动组合为 host:port。SSL 对应配置项 SMTP_SSL。</div>
              </div>

              <!-- ServerJ Fields -->
              <div v-if="form.type === 'serverj'">
                <div class="mb-3">
                  <label class="form-label">PUSH_KEY <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bx bx-key"></i></span>
                    <input type="text" class="form-control" v-model="form.PUSH_KEY" required>
                  </div>
                  <div class="form-text field-tip">说明：支持旧版与 Turbo 版，填写对应的 PUSH_KEY。</div>
                </div>
              </div>

              <!-- Synology Chat Fields -->
              <div v-if="form.type === 'chat'">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Chat URL <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-link-alt"></i></span>
                      <input type="text" class="form-control" v-model="form.CHAT_URL" required>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Chat Token <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-key"></i></span>
                      <input type="text" class="form-control" v-model="form.CHAT_TOKEN" required>
                    </div>
                  </div>
                </div>
                <div class="form-text field-tip">说明：在群组的整合服务中创建“传入Webhook”，复制Webhook URL；Token按需填写。</div>
              </div>

              <!-- MediaSaber Fields -->
              <div v-if="form.type === 'mediasaber'">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">服务器地址 <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-network-chart"></i></span>
                      <input type="text" class="form-control" v-model="form.MEDIASABER_HOST" required placeholder="https://your-domain.com">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">API密钥 <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bx bx-key"></i></span>
                      <input type="text" class="form-control" v-model="form.MEDIASABER_APIKEY" required>
                    </div>
                  </div>
                </div>
                <div class="form-text field-tip">说明：填写Media Saber服务器的完整地址（如：https://your-domain.com）和对应的apikey。</div>
              </div>
              


              <!-- Webhook Fields -->
              <div v-if="form.type === 'webhook'">
                <div class="mb-3">
                  <label class="form-label">通知URL <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bx bx-link-alt"></i></span>
                    <input type="text" class="form-control" v-model="form.WEBHOOK_URL" required placeholder="Webhook URL">
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">请求方法</label>
                    <div ref="webhookMethodWrapperRef" class="notification-type-wrapper position-relative">
                      <div class="input-group notification-input-group notification-type-group">
                      <span class="input-group-text"><i class="bx bx-transfer-alt"></i></span>
                        <button
                          type="button"
                          class="form-control notification-type-trigger"
                          @click="toggleDropdown('webhookMethod')"
                        >
                          <span>{{ selectedWebhookMethodLabel }}</span>
                          <i class="bx bx-chevron-down" :class="{ 'is-open': dropdownOpen.webhookMethod }"></i>
                        </button>
                      </div>

                      <transition name="cron-dropdown">
                        <div v-if="dropdownOpen.webhookMethod" class="notification-type-dropdown notification-type-dropdown-compact">
                          <div class="notification-type-dropdown-note">
                            <strong>请求方法</strong>
                            <span>选择发送通知时使用的 HTTP 请求方法。</span>
                          </div>
                          <button
                            v-for="option in webhookMethodOptions"
                            :key="option.value"
                            type="button"
                            class="notification-type-option"
                            :class="{ 'is-active': form.WEBHOOK_METHOD === option.value }"
                            @click="selectDropdownOption('webhookMethod', option.value, 'WEBHOOK_METHOD')"
                          >
                            <strong>{{ option.label }}</strong>
                            <span>{{ option.meta }}</span>
                          </button>
                        </div>
                      </transition>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Content-Type</label>
                    <div ref="webhookContentTypeWrapperRef" class="notification-type-wrapper position-relative">
                      <div class="input-group notification-input-group notification-type-group">
                      <span class="input-group-text"><i class="bx bx-code-alt"></i></span>
                        <button
                          type="button"
                          class="form-control notification-type-trigger"
                          @click="toggleDropdown('webhookContentType')"
                        >
                          <span>{{ selectedWebhookContentTypeLabel }}</span>
                          <i class="bx bx-chevron-down" :class="{ 'is-open': dropdownOpen.webhookContentType }"></i>
                        </button>
                      </div>

                      <transition name="cron-dropdown">
                        <div v-if="dropdownOpen.webhookContentType" class="notification-type-dropdown notification-type-dropdown-compact">
                          <div class="notification-type-dropdown-note">
                            <strong>Content-Type</strong>
                            <span>匹配请求体格式，便于接收端正确解析内容。</span>
                          </div>
                          <button
                            v-for="option in webhookContentTypeOptions"
                            :key="option.value"
                            type="button"
                            class="notification-type-option"
                            :class="{ 'is-active': form.WEBHOOK_CONTENT_TYPE === option.value }"
                            @click="selectDropdownOption('webhookContentType', option.value, 'WEBHOOK_CONTENT_TYPE')"
                          >
                            <strong>{{ option.label }}</strong>
                            <span>{{ option.meta }}</span>
                          </button>
                        </div>
                      </transition>
                    </div>
                  </div>
                </div>

                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">请求头 (可选)</label>
                    <textarea class="form-control" v-model="form.WEBHOOK_HEADERS" rows="3" placeholder="Authorization: Bearer token&#10;X-Custom: value"></textarea>
                    <div class="form-text field-tip">请求头，一行一个；例如：X-Requested-With:XMLHttpRequest</div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">请求体</label>
                    <textarea class="form-control" v-model="form.WEBHOOK_BODY" rows="3" placeholder='{"title": "$title", "text": "$content"}'></textarea>
                    <div class="form-text field-tip">JSON: {"title": "$title", "text": "$content"}；表单: title=$title&text=$content</div>
                  </div>
                </div>
              </div>

              </section>
            </form>
          </div>
          <div class="modal-footer notification-modal-footer">
            <div class="notification-modal-footer-note">
              <i class="bx bx-info-circle"></i>
              <span>保存后可在列表中继续测试发送、切换启用状态或再次编辑渠道配置。</span>
            </div>
            <div class="notification-modal-footer-actions">
              <button type="button" class="notification-modal-btn notification-modal-btn-muted" @click="$emit('close')">取消</button>
              <button type="button" class="notification-modal-btn notification-modal-btn-primary" @click="save">
                <i class="bx bx-save"></i>
                <span>保存配置</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, reactive, onMounted, onUnmounted, ref, watch } from 'vue';
import { useToast } from 'vue-toastification';

const props = defineProps<{
  initialData?: any;
  isEdit?: boolean;
}>();

const emit = defineEmits(['close', 'save']);
const toast = useToast();
const typeDropdownOpen = ref(false);
const typeWrapperRef = ref<HTMLElement | null>(null);
const barkLevelWrapperRef = ref<HTMLElement | null>(null);
const webhookMethodWrapperRef = ref<HTMLElement | null>(null);
const webhookContentTypeWrapperRef = ref<HTMLElement | null>(null);

const dropdownOpen = reactive({
  barkLevel: false,
  webhookMethod: false,
  webhookContentType: false
});

const notificationTypeOptions = [
  { value: 'wecom_bot', label: '企业微信机器人' },
  { value: 'wecom_app', label: '企业微信应用' },
  { value: 'telegram', label: 'Telegram Bot' },
  { value: 'igot', label: 'iGot 聚合推送' },
  { value: 'dingding', label: '钉钉机器人' },
  { value: 'feishu', label: '飞书机器人' },
  { value: 'smtp', label: 'SMTP 邮件' },
  { value: 'bark', label: 'Bark' },
  { value: 'serverj', label: 'Server酱' },
  { value: 'chat', label: 'Synology Chat' },
  { value: 'mediasaber', label: 'Media Saber' },
  { value: 'webhook', label: '自定义Webhook' }
] as const;

const barkLevelOptions = [
  { value: '', label: '默认', meta: 'system' },
  { value: 'active', label: 'Active', meta: '立即亮屏' },
  { value: 'timeSensitive', label: 'TimeSensitive', meta: '时效通知' },
  { value: 'passive', label: 'Passive', meta: '仅列表展示' }
] as const;

const webhookMethodOptions = [
  { value: 'POST', label: 'POST', meta: 'body' },
  { value: 'GET', label: 'GET', meta: 'query' }
] as const;

const webhookContentTypeOptions = [
  { value: 'application/json', label: 'application/json', meta: 'json' },
  { value: 'application/x-www-form-urlencoded', label: 'application/x-www-form-urlencoded', meta: 'form' },
  { value: 'text/plain', label: 'text/plain', meta: 'text' }
] as const;

const wecomApp = reactive({
  corpid: '',
  corpsecret: '',
  touser: '',
  agentid: '',
  media_id: ''
});

const form = reactive<any>({
  name: '',
  type: 'wecom_bot',
  enable: true,
  HITOKOTO: false,
  // Common fields initialized to empty to avoid undefined issues
  BARK_PUSH: '', BARK_SOUND: '', BARK_GROUP: '', BARK_ICON: '', BARK_LEVEL: '', BARK_URL: '', BARK_ARCHIVE: '0',
  TG_BOT_TOKEN: '', TG_USER_ID: '', TG_API_HOST: '', TG_PROXY_HOST: '', TG_PROXY_PORT: '',
  QYWX_KEY: '', QYWX_AM: '', QYWX_ORIGIN: '',
  SMTP_SERVER: '', SMTP_SSL: 'false', SMTP_EMAIL: '', SMTP_PASSWORD: '', SMTP_NAME: '',
  WEBHOOK_URL: '', WEBHOOK_METHOD: 'POST', WEBHOOK_CONTENT_TYPE: 'application/json', WEBHOOK_HEADERS: '', WEBHOOK_BODY: '',
  IGOT_PUSH_KEY: '',
  DD_BOT_TOKEN: '', DD_BOT_SECRET: '',
  FSKEY: '',
  PUSH_KEY: '',
  CHAT_URL: '', CHAT_TOKEN: '',
  MEDIASABER_HOST: '', MEDIASABER_APIKEY: ''
});

const selectedTypeLabel = computed(() => {
  const target = notificationTypeOptions.find(type => type.value === form.type);
  return target?.label || '企业微信机器人';
});

const selectedBarkLevelLabel = computed(() => {
  const target = barkLevelOptions.find(option => option.value === form.BARK_LEVEL);
  return target?.label || '默认';
});

const smtpSslEnabled = computed({
  get: () => form.SMTP_SSL === 'true',
  set: (value: boolean) => {
    form.SMTP_SSL = value ? 'true' : 'false';
  }
});

const selectedWebhookMethodLabel = computed(() => {
  const target = webhookMethodOptions.find(option => option.value === form.WEBHOOK_METHOD);
  return target?.label || 'POST';
});

const selectedWebhookContentTypeLabel = computed(() => {
  const target = webhookContentTypeOptions.find(option => option.value === form.WEBHOOK_CONTENT_TYPE);
  return target?.label || 'application/json';
});

const closeAllDropdowns = () => {
  typeDropdownOpen.value = false;
  dropdownOpen.barkLevel = false;
  dropdownOpen.webhookMethod = false;
  dropdownOpen.webhookContentType = false;
};

const toggleTypeDropdown = () => {
  if (props.isEdit) return;
  const nextState = !typeDropdownOpen.value;
  closeAllDropdowns();
  typeDropdownOpen.value = nextState;
};

const selectNotificationType = (type: string) => {
  form.type = type;
  typeDropdownOpen.value = false;
};

const toggleDropdown = (key: keyof typeof dropdownOpen) => {
  const nextState = !dropdownOpen[key];
  closeAllDropdowns();
  dropdownOpen[key] = nextState;
};

const selectDropdownOption = (key: keyof typeof dropdownOpen, value: string, field: string) => {
  form[field] = value;
  dropdownOpen[key] = false;
};

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Node;
  const isInsideKnownDropdown = [
    typeWrapperRef.value,
    barkLevelWrapperRef.value,
    webhookMethodWrapperRef.value,
    webhookContentTypeWrapperRef.value
  ].some(wrapper => wrapper?.contains(target));

  if (!isInsideKnownDropdown) {
    closeAllDropdowns();
  }
};

// Sync wecomApp fields to QYWX_AM
watch(wecomApp, (newVal) => {
  const parts = [newVal.corpid, newVal.corpsecret, newVal.touser, newVal.agentid];
  if (newVal.media_id) {
    parts.push(newVal.media_id);
  }
  // Only update if at least one field is filled to avoid overwriting with commas on init if empty
  if (parts.some(p => p)) {
     form.QYWX_AM = parts.join(',');
  }
});

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  if (props.initialData) {
    Object.assign(form, props.initialData);
    
    // Parse QYWX_AM if exists
    if (form.QYWX_AM) {
      const parts = form.QYWX_AM.split(',');
      if (parts.length >= 4) {
        wecomApp.corpid = parts[0];
        wecomApp.corpsecret = parts[1];
        wecomApp.touser = parts[2];
        wecomApp.agentid = parts[3];
        if (parts.length > 4) {
          wecomApp.media_id = parts[4];
        }
      }
    }
  }
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

const save = () => {
  // Basic validation
  if (!form.name) {
    toast.error('请输入渠道名称');
    return;
  }
  


  emit('save', { ...form });
};
</script>

<style scoped>
.notification-modal {
  background: var(--bg-overlay);
}

.notification-modal-dialog {
  max-width: 52rem;
  padding: 0.9rem;
}

.notification-modal-content {
  border: 1px solid rgba(161, 172, 184, 0.16);
  border-radius: 1.2rem;
  overflow: hidden;
  background: color-mix(in srgb, var(--bg-surface) 94%, white 6%);
  box-shadow: 0 1.1rem 2.4rem rgba(15, 23, 42, 0.16);
}

.notification-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 1rem 1.15rem 0.85rem;
  border-bottom: 1px solid var(--divider-color);
  background: color-mix(in srgb, transparent 28%, rgba(var(--primary-rgb), 0.06));
}

.notification-modal-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.notification-modal-title-wrap .modal-title {
  margin: 0;
  color: var(--text-heading);
  font-size: 1.08rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.notification-modal-title-wrap p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.85rem;
  line-height: 1.55;
}

.notification-modal-close {
  flex-shrink: 0;
  margin: 0;
}

.notification-modal-body {
  padding: 1rem 1.15rem 1.05rem;
}

.notification-modal-form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.notification-form-panel {
  padding: 0.9rem;
  border: 1px solid rgba(161, 172, 184, 0.14);
  border-radius: 0.95rem;
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, transparent);
}

.notification-form-panel-main {
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.04), transparent 100%);
}

.notification-form-panel-subtle {
  background: linear-gradient(180deg, rgba(var(--primary-rgb), 0.04), transparent 100%);
}

.notification-form-panel-head {
  margin-bottom: 0.75rem;
}

.notification-form-panel-head-inline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.notification-form-panel-head h6 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-heading);
}

.notification-form-panel-head span {
  display: block;
  margin-top: 0.3rem;
  color: var(--text-muted);
  font-size: 0.81rem;
  line-height: 1.45;
}

.notification-switch-item-compact {
  flex: 0 0 auto;
  min-width: auto;
}
.notification-switch-item {
  display: flex;
  align-items: center;
  gap: 0.72rem;
  min-height: 2.9rem;
  margin: 0;
}

.notification-switch-item-inline {
  min-height: auto;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  justify-content: flex-end;
}

.smtp-name-col {
  min-width: 0;
}

.smtp-ssl-col {
  padding-left: 0.35rem;
  min-width: 12rem;
}

.notification-checkbox-input {
  width: 1rem !important;
  height: 1rem !important;
  border-radius: 0.28rem !important;
  background-size: 0.72rem;
}

.notification-checkbox-input:checked {
  background-color: rgba(var(--primary-rgb), 0.92) !important;
  border-color: rgba(var(--primary-rgb), 0.92) !important;
}

.notification-checkbox-input:focus {
  box-shadow: 0 0 0 0.18rem rgba(var(--primary-rgb), 0.14) !important;
}

.notification-switch-item :deep(.form-check-label) {
  color: var(--text-heading);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
}

.notification-switch-item :deep(.form-check-input) {
  width: 2.5rem;
  height: 1.35rem;
  margin: 0;
  cursor: pointer;
  float: none;
  flex-shrink: 0;
  background-color: rgba(161, 172, 184, 0.3);
  border-color: rgba(161, 172, 184, 0.3);
  box-shadow: none;
}

.notification-switch-item :deep(.form-check-input:checked) {
  background-color: rgba(var(--primary-rgb), 0.92);
  border-color: rgba(var(--primary-rgb), 0.92);
}

.notification-switch-item :deep(.form-check-input:focus) {
  box-shadow: 0 0 0 0.18rem rgba(var(--primary-rgb), 0.14);
  border-color: rgba(var(--primary-rgb), 0.42);
}

.section-divider {
  margin: 1rem 0 1.5rem;
  border-color: var(--divider-color);
  opacity: 1;
}

.notification-modal-body :deep(.form-label) {
  margin-bottom: 0.48rem;
  color: var(--text-heading);
  font-size: 0.88rem;
  font-weight: 600;
}

.notification-modal-body :deep(.input-group) {
  display: flex;
  align-items: stretch;
  border-radius: 0.9rem;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--border-color);
}

.notification-input-group {
  display: flex;
  align-items: stretch;
  border-radius: 0.9rem;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--border-color);
}

.notification-modal-body :deep(.input-group-text) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.9rem;
  color: var(--primary-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 72%, rgba(var(--primary-rgb), 0.08));
  border: 0;
  border-right: 1px solid var(--border-color);
}

.notification-modal-body :deep(.form-control),
.notification-modal-body :deep(.form-select) {
  min-height: 2.9rem;
  border: 0;
  background: var(--bg-surface) !important;
  color: color-mix(in srgb, var(--text-heading) 78%, var(--text-muted));
  box-shadow: none;
}

.notification-modal-body :deep(.form-control::placeholder) {
  color: color-mix(in srgb, var(--text-muted) 88%, transparent);
}

.notification-type-wrapper {
  width: 100%;
}

.notification-type-group.is-disabled {
  opacity: 0.78;
}

.notification-type-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.68rem 0.92rem;
  text-align: left;
  cursor: pointer;
}

.notification-type-trigger span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-type-trigger span.is-placeholder {
  color: color-mix(in srgb, var(--text-muted) 88%, transparent);
}

.notification-type-trigger i {
  flex: 0 0 auto;
  font-size: 1rem;
  color: var(--text-muted);
  transition: transform 0.2s ease, color 0.2s ease;
}

.notification-type-trigger i.is-open {
  transform: rotate(180deg);
  color: var(--primary-color);
}

.notification-type-trigger:disabled {
  cursor: not-allowed;
}

.notification-type-dropdown {
  position: absolute;
  top: calc(100% + 0.55rem);
  left: 0;
  right: 0;
  z-index: 30;
  isolation: isolate;
  padding: 0.45rem;
  display: grid;
  gap: 0.36rem;
  border-radius: 0.95rem;
  border: 1px solid rgba(var(--primary-rgb), 0.1);
  background: color-mix(in srgb, var(--bg-surface) 92%, white 8%);
  backdrop-filter: blur(14px) saturate(145%);
  -webkit-backdrop-filter: blur(14px) saturate(145%);
  box-shadow: 0 0.85rem 1.7rem rgba(15, 23, 42, 0.1);
  max-height: 15.2rem;
  overflow-y: auto;
  scrollbar-width: none;
}

.notification-type-dropdown-compact {
  max-height: 13.8rem;
}

.notification-type-dropdown::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  border-radius: inherit;
  background: var(--bg-surface);
}

.notification-type-dropdown::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.notification-type-dropdown-note {
  display: grid;
  gap: 0.18rem;
  padding: 0.2rem 0.32rem 0.12rem;
}

.notification-type-dropdown-note strong {
  font-size: 0.79rem;
  color: var(--text-heading);
}

.notification-type-dropdown-note span {
  font-size: 0.72rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.notification-type-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  width: 100%;
  padding: 0.62rem 0.72rem;
  border: 0;
  border-radius: 0.8rem;
  background: transparent;
  color: inherit;
  text-align: left;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.notification-type-option strong {
  font-size: 0.84rem;
  color: var(--text-heading);
  font-weight: 600;
}

.notification-type-option span {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.notification-type-option:hover,
.notification-type-option.is-active {
  background: rgba(var(--primary-rgb), 0.1);
}

.notification-type-option.is-active strong,
.notification-type-option.is-active span {
  color: var(--primary-color);
}

.notification-modal-body :deep(.form-control:focus),
.notification-modal-body :deep(.form-select:focus),
.notification-modal-body :deep(textarea.form-control:focus) {
  box-shadow: inset 0 0 0 1px rgba(var(--primary-rgb), 0.34), 0 0 0 0.2rem rgba(var(--primary-rgb), 0.12);
}

.notification-modal-body :deep(textarea.form-control) {
  min-height: 6.5rem;
  border-radius: 0.95rem !important;
  border: 1px solid var(--border-color);
  background: var(--bg-surface) !important;
  color: var(--text-main);
  box-shadow: none !important;
}

.notification-modal-body :deep(.form-check:not(.notification-switch-item-inline)) {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 2.9rem;
  margin: 0;
  padding: 0.82rem 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 0.9rem;
  background: var(--bg-surface);
}

.notification-modal-body :deep(.form-check:not(.notification-switch-item-inline) .form-check-input) {
  margin-top: 0;
  margin-left: 0;
  float: none;
  flex-shrink: 0;
}

.notification-modal-body :deep(.form-check:not(.notification-switch-item-inline) .form-check-label) {
  color: var(--text-heading);
  font-size: 0.84rem;
  font-weight: 600;
}

.bark-archive-check {
  min-height: 3rem;
  height: 3rem;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

.smtp-ssl-check {
  justify-content: flex-start;
  min-height: 3rem;
  height: 3rem;
}

.bark-archive-check :deep(.form-check-label) {
  color: var(--text-heading);
  font-size: 0.84rem;
  font-weight: 600;
}

.bark-archive-label-placeholder {
  visibility: hidden;
}

.field-tip {
  margin-top: 0.35rem;
  color: var(--text-muted);
  font-size: 0.79rem;
  line-height: 1.55;
}

.notification-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.85rem 1.15rem 1rem;
  border-top: 1px solid var(--divider-color);
  background: color-mix(in srgb, var(--bg-surface-alt) 82%, transparent);
}

.notification-modal-footer-note {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--text-muted);
  font-size: 0.81rem;
  line-height: 1.5;
}

.notification-modal-footer-note i {
  color: rgb(var(--primary-rgb));
  font-size: 1rem;
  line-height: 1;
  flex: 0 0 auto;
}

.notification-modal-footer-note span {
  display: block;
}

.notification-modal-footer-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.notification-modal-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.38rem;
  min-height: 2.35rem;
  padding: 0.52rem 0.88rem;
  border: 1px solid transparent;
  border-radius: 0.78rem;
  font-size: 0.86rem;
  font-weight: 600;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast), border-color var(--transition-fast);
}

.notification-modal-btn:hover:not(:disabled),
.notification-modal-btn:focus-visible:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.notification-modal-btn-primary {
  background: linear-gradient(135deg, rgba(var(--primary-rgb), 0.98), rgba(var(--primary-rgb), 0.82));
  color: #fff;
  box-shadow: 0 0.75rem 1.6rem rgba(var(--primary-rgb), 0.22);
}

.notification-modal-btn-muted {
  background: color-mix(in srgb, var(--bg-surface-alt) 88%, transparent);
  border-color: rgba(161, 172, 184, 0.16);
  color: color-mix(in srgb, var(--text-heading) 74%, var(--text-muted));
}

/* Mobile Responsiveness Fixes */
@media (max-width: 767.98px) {
  .notification-form-panel-head-inline {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
  }

  .notification-switch-item-compact {
    width: auto;
    min-width: auto;
    margin-left: auto;
  }

  .notification-form-panel-head-inline h6 {
    flex: 0 0 auto;
    margin-left: 0;
  }

  .smtp-name-col,
  .smtp-ssl-col {
    flex: 0 0 50%;
    max-width: 50%;
    margin-bottom: 0.75rem;
  }

  .smtp-name-col {
    padding-right: 0.35rem;
  }

  .smtp-ssl-col {
    min-width: 0;
    padding-left: 0.35rem;
  }

  .smtp-ssl-check {
    width: 100%;
  }

  .bark-archive-col .bark-archive-label-placeholder {
    display: none;
  }

  .notification-modal-dialog {
    margin: 0.5rem auto;
    max-width: calc(100% - 1rem) !important; /* Force max width to be screen width minus margin */
    width: calc(100% - 1rem) !important; /* Explicitly set width */
    height: calc(100% - 1rem); /* Full height minus margins */
    display: flex;
    align-items: center; /* Center vertically */
  }

  .notification-modal-content {
    max-height: 100%; /* Ensure it fits within viewport */
    width: 100%; /* Ensure content fills dialog */
    display: flex;
    flex-direction: column;
    overflow: hidden; /* Prevent overflow */
  }

  .notification-modal-body {
    overflow-y: auto; /* Scrollable body */
    overflow-x: hidden; /* Prevent horizontal scroll */
    padding: 1rem; /* Slightly less padding on mobile */
  }

  .notification-modal-header,
  .notification-modal-footer {
    padding: 1rem; /* Consistent padding */
    flex-shrink: 0; /* Prevent header/footer from shrinking */
  }

  .notification-modal-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .notification-modal-footer-note {
    display: none;
  }

  .notification-modal-footer-actions {
    width: 100%;
    margin: 0 auto;
    justify-content: center;
    align-items: center;
    flex-direction: row;
  }

  .notification-modal-btn,
  .notification-modal-footer-actions .notification-modal-btn {
    width: auto;
    flex: 1 1 0;
    justify-content: center;
  }
}
</style>
