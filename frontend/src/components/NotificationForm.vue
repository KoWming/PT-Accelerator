<template>
  <Teleport to="body">
    <div class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEdit ? '编辑' : '添加' }}通知渠道</h5>
            <button type="button" class="btn-close" @click="$emit('close')"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="save">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">渠道名称 (备注) <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-tag"></i></span>
                    <input type="text" class="form-control" v-model="form.name" required placeholder="例如：自定义通知">
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">通知类型 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-broadcast"></i></span>
                    <select class="form-select" v-model="form.type" :disabled="isEdit" required>
                      <option value="" disabled>选择类型</option>
                      <option value="wecom_bot">企业微信机器人</option>
                      <option value="wecom_app">企业微信应用</option>
                      <option value="telegram">Telegram Bot</option>
                      <option value="igot">iGot 聚合推送</option>
                      <option value="dingding">钉钉机器人</option>
                      <option value="feishu">飞书机器人</option>
                      <option value="smtp">SMTP 邮件</option>
                      <option value="bark">Bark</option>
                      <option value="serverj">Server酱</option>
                      <option value="chat">Synology Chat</option>
                      <option value="mediasaber">Media Saber</option>
                      <option value="webhook">自定义Webhook</option>
                    </select>
                  </div>
                </div>
              </div>

              <hr>

              <!-- Bark Fields -->
              <div v-if="form.type === 'bark'">
                <div class="mb-3">
                  <label class="form-label">Bark 推送地址或设备码 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-phone"></i></span>
                    <input type="text" class="form-control" v-model="form.BARK_PUSH" required placeholder="https://api.day.app/DxHcxxxxx...">
                  </div>
                  <div class="form-text">填入完整的 URL 或 Key</div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">分组 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-collection"></i></span>
                      <input type="text" class="form-control" v-model="form.BARK_GROUP" placeholder="默认: PT-Accelerator">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">声音 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-volume-up"></i></span>
                      <input type="text" class="form-control" v-model="form.BARK_SOUND">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">图标URL (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-image"></i></span>
                      <input type="text" class="form-control" v-model="form.BARK_ICON" placeholder="https://day.app/assets/images/avatar.jpg">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">时效性 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-clock-history"></i></span>
                      <select class="form-select" v-model="form.BARK_LEVEL">
                        <option value="">默认</option>
                        <option value="active">Active (立即亮屏)</option>
                        <option value="timeSensitive">TimeSensitive (时效性)</option>
                        <option value="passive">Passive (仅列表)</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">跳转URL (可选)</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-link-45deg"></i></span>
                    <input type="text" class="form-control" v-model="form.BARK_URL">
                  </div>
                </div>
                <div class="mb-3 form-check">
                  <input type="checkbox" class="form-check-input" id="bark_archive" v-model="form.BARK_ARCHIVE" true-value="1" false-value="0">
                  <label class="form-check-label" for="bark_archive">存档 (BARK_ARCHIVE)</label>
                </div>
              </div>

              <!-- Telegram Fields -->
              <div v-if="form.type === 'telegram'">
                <div class="mb-3">
                  <label class="form-label">机器人的TOKEN <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-robot"></i></span>
                    <input type="text" class="form-control" v-model="form.TG_BOT_TOKEN" required>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">机器人的ID <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-person-badge"></i></span>
                      <input type="text" class="form-control" v-model="form.TG_USER_ID" required>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">API代理地址 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-globe"></i></span>
                      <input type="text" class="form-control" v-model="form.TG_API_HOST" placeholder="默认: https://api.telegram.org">
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">HTTP 代理 (可选)</label>
                  <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-hdd-network"></i></span>
                      <input type="text" class="form-control" v-model="form.TG_PROXY_HOST" placeholder="代理主机">
                      <span class="input-group-text">:</span>
                      <input type="text" class="form-control" v-model="form.TG_PROXY_PORT" placeholder="代理端口">
                  </div>
                </div>
                <div class="form-text">说明：默认使用官方地址 https://api.telegram.org，如需自建代理或使用代理服务器可填写相应配置。</div>
              </div>

              <!-- iGot Fields -->
              <div v-if="form.type === 'igot'">
                <div class="mb-3">
                  <label class="form-label">Push Key <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-key"></i></span>
                    <input type="text" class="form-control" v-model="form.IGOT_PUSH_KEY" required>
                  </div>
                  <div class="form-text">在 iGot 平台获取 PUSH_KEY，格式通常为一串字母数字。</div>
                </div>
              </div>

              <!-- DingDing Fields -->
              <div v-if="form.type === 'dingding'">
                <div class="mb-3">
                  <label class="form-label">DD_BOT_TOKEN <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-robot"></i></span>
                    <input type="text" class="form-control" v-model="form.DD_BOT_TOKEN" required>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">DD_BOT_SECRET <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-key"></i></span>
                    <input type="text" class="form-control" v-model="form.DD_BOT_SECRET" required>
                  </div>
                </div>
                <div class="form-text">在钉钉群自定义机器人中获取 Token 与加签 Secret。</div>
              </div>

              <!-- Feishu Fields -->
              <div v-if="form.type === 'feishu'">
                <div class="mb-3">
                  <label class="form-label">飞书机器人 FSKEY <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-robot"></i></span>
                    <input type="text" class="form-control" v-model="form.FSKEY" required>
                  </div>
                  <div class="form-text">在飞书群机器人的设置中获取 FSKEY。</div>
                </div>
              </div>

              <!-- WeCom Bot Fields -->
              <div v-if="form.type === 'wecom_bot'">
                <div class="mb-3">
                  <label class="form-label">企业微信机器人Key <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-key"></i></span>
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
                      <span class="input-group-text"><i class="bi bi-building"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.corpid" placeholder="企业ID">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">应用Secret (corpsecret)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-key"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.corpsecret" placeholder="应用Secret">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">接收者 (touser 或 @all)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-person"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.touser" placeholder="接收者">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">应用AgentID (agentid)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-robot"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.agentid" placeholder="应用AgentID">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">图文素材 media_id (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-file-image"></i></span>
                      <input type="text" class="form-control" v-model="wecomApp.media_id" placeholder="图文素材media_id">
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">转发代理地址 (可选)</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-globe"></i></span>
                      <input type="text" class="form-control" v-model="form.QYWX_ORIGIN" placeholder="https://qyapi.weixin.qq.com">
                    </div>
                  </div>
                </div>
                <div class="form-text">将以上字段组合为 QYWX_AM: corpid,corpsecret,touser,agentid[,media_id]</div>
                <div class="form-text">说明：企业微信消息的转发代理地址，2022年6月20日后创建的自建应用才需要，其他情况请保持默认 https://qyapi.weixin.qq.com</div>
              </div>

              <!-- SMTP Fields -->
              <div v-if="form.type === 'smtp'">
                <div class="row">
                  <div class="col-md-8 mb-3">
                      <label class="form-label">SMTP服务器(host 或 host:port) <span class="text-danger">*</span></label>
                      <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-hdd-network"></i></span>
                        <input type="text" class="form-control" v-model="form.SMTP_SERVER" required placeholder="smtp.exmail.qq.com:465">
                      </div>
                  </div>
                  <div class="col-md-4 mb-3">
                      <label class="form-label">启用SSL</label>
                      <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-shield-lock"></i></span>
                        <select class="form-select" v-model="form.SMTP_SSL">
                            <option value="true">是</option>
                            <option value="false">否</option>
                        </select>
                      </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">邮箱 <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                      <input type="email" class="form-control" v-model="form.SMTP_EMAIL" required>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">密码/授权码 <span class="text-danger">*</span></label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-key"></i></span>
                      <input type="password" class="form-control" v-model="form.SMTP_PASSWORD" required>
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">发件人名称(可选)</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input type="text" class="form-control" v-model="form.SMTP_NAME">
                  </div>
                </div>
                <div class="form-text">说明：若服务器地址未包含端口且填写了端口，将自动组合为 host:port。SSL 对应配置项 SMTP_SSL。</div>
              </div>

              <!-- ServerJ Fields -->
              <div v-if="form.type === 'serverj'">
                <div class="mb-3">
                  <label class="form-label">PUSH_KEY <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-key"></i></span>
                    <input type="text" class="form-control" v-model="form.PUSH_KEY" required>
                  </div>
                  <div class="form-text">说明：支持旧版与 Turbo 版，填写对应的 PUSH_KEY。</div>
                </div>
              </div>

              <!-- Synology Chat Fields -->
              <div v-if="form.type === 'chat'">
                <div class="mb-3">
                  <label class="form-label">Chat URL <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-link-45deg"></i></span>
                    <input type="text" class="form-control" v-model="form.CHAT_URL" required>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">Chat Token <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-key"></i></span>
                    <input type="text" class="form-control" v-model="form.CHAT_TOKEN" required>
                  </div>
                </div>
                <div class="form-text">说明：在群组的整合服务中创建“传入Webhook”，复制Webhook URL；Token按需填写。</div>
              </div>

              <!-- MediaSaber Fields -->
              <div v-if="form.type === 'mediasaber'">
                <div class="mb-3">
                  <label class="form-label">服务器地址 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-hdd-network"></i></span>
                    <input type="text" class="form-control" v-model="form.MEDIASABER_HOST" required placeholder="https://your-domain.com">
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">API密钥 <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-key"></i></span>
                    <input type="text" class="form-control" v-model="form.MEDIASABER_APIKEY" required>
                  </div>
                </div>
                <div class="form-text">说明：填写Media Saber服务器的完整地址（如：https://your-domain.com）和对应的apikey。</div>
              </div>
              


              <!-- Webhook Fields -->
              <div v-if="form.type === 'webhook'">
                <div class="mb-3">
                  <label class="form-label">通知URL <span class="text-danger">*</span></label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-link-45deg"></i></span>
                    <input type="text" class="form-control" v-model="form.WEBHOOK_URL" required placeholder="Webhook URL">
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">请求方法</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-arrow-left-right"></i></span>
                      <select class="form-select" v-model="form.WEBHOOK_METHOD">
                          <option value="POST">POST</option>
                          <option value="GET">GET</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Content-Type</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-file-earmark-code"></i></span>
                      <select class="form-select" v-model="form.WEBHOOK_CONTENT_TYPE">
                          <option value="application/json">application/json</option>
                          <option value="application/x-www-form-urlencoded">application/x-www-form-urlencoded</option>
                          <option value="text/plain">text/plain</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label">请求头 (可选)</label>
                    <textarea class="form-control" v-model="form.WEBHOOK_HEADERS" rows="3" placeholder="Authorization: Bearer token&#10;X-Custom: value"></textarea>
                    <div class="form-text">请求头，一行一个；例如：X-Requested-With:XMLHttpRequest</div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">请求体</label>
                    <textarea class="form-control" v-model="form.WEBHOOK_BODY" rows="3" placeholder='{"title": "$title", "text": "$content"}'></textarea>
                    <div class="form-text">JSON: {"title": "$title", "text": "$content"}；表单: title=$title&text=$content</div>
                  </div>
                </div>
              </div>

              <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="hitokoto" v-model="form.HITOKOTO">
                <label class="form-check-label" for="hitokoto">启用一言 (随机句子)</label>
              </div>

              <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="enable" v-model="form.enable">
                <label class="form-check-label" for="enable">启用此渠道</label>
              </div>

            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="$emit('close')">取消</button>
            <button type="button" class="btn btn-primary" @click="save">保存</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { reactive, onMounted, watch } from 'vue';
import { useToast } from 'vue-toastification';

const props = defineProps<{
  initialData?: any;
  isEdit?: boolean;
}>();

const emit = defineEmits(['close', 'save']);
const toast = useToast();

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
/* Mobile Responsiveness Fixes */
@media (max-width: 767.98px) {
  .modal-dialog {
    margin: 0.5rem auto; /* Center horizontally with small margin */
    max-width: calc(100% - 1rem) !important; /* Force max width to be screen width minus margin */
    width: calc(100% - 1rem) !important; /* Explicitly set width */
    height: calc(100% - 1rem); /* Full height minus margins */
    display: flex;
    align-items: center; /* Center vertically */
  }

  .modal-content {
    max-height: 100%; /* Ensure it fits within viewport */
    width: 100%; /* Ensure content fills dialog */
    display: flex;
    flex-direction: column;
    overflow: hidden; /* Prevent overflow */
  }

  .modal-body {
    overflow-y: auto; /* Scrollable body */
    overflow-x: hidden; /* Prevent horizontal scroll */
    padding: 1rem; /* Slightly less padding on mobile */
  }

  .modal-header, .modal-footer {
    padding: 1rem; /* Consistent padding */
    flex-shrink: 0; /* Prevent header/footer from shrinking */
  }
}
</style>
