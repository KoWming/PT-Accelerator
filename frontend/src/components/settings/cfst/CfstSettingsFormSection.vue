<template>
  <div class="settings-auth-body">
    <form @submit.prevent="$emit('submit')">
      <div class="settings-inline-note settings-inline-note-no-bottom-padding" role="alert">
        <i class="bx bx-info-circle"></i>
        <div>
          <span class="settings-inline-note-title">这些参数会直接影响 CFST 二进制测速行为。</span>
          <div class="settings-inline-note-text">
            CloudflareSpeedTest 默认流程是：先做延迟测速与过滤，再对最低延迟的候选 IP 依次进行下载测速，最后按速度排序输出结果。启用"禁用下载测速 (-dd)"后只按延迟排序，不执行下载测速。
          </div>
        </div>
      </div>

      <section class="settings-form-block">

        <div class="settings-block-heading settings-block-heading-split">
          <h4>基础测速参数</h4>
          <p>对应官方 `-n`、`-t`、`-dn`、`-dt`、`-tp`、`-url` 以及额外命令行参数，用于控制延迟测速、下载测速与自定义补充行为。</p>
        </div>

        <div class="settings-field-grid settings-field-grid-cfst-base">
          <div class="settings-field-card">
            <label class="form-label settings-form-label">延迟测速线程 (-n) <span class="settings-default-badge">默认 200</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.threads ?? ''" min="1" max="1000" placeholder="200" @input="updateNumberField('threads', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">官方说明：线程越多延迟测速越快，默认 200、最高 1000；性能弱的设备如路由器不建议设太高。</div>
          </div>
          <div class="settings-field-card">
            <label class="form-label settings-form-label">延迟测速次数 (-t) <span class="settings-default-badge">默认 4 次</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.ping_times ?? ''" min="1" placeholder="4" @input="updateNumberField('ping_times', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">单个 IP 的延迟测速次数，默认 4 次；次数越多结果越稳，但总耗时会同步增加。</div>
          </div>
          <div class="settings-field-card">
            <label class="form-label settings-form-label">下载测速数量 (-dn) <span class="settings-default-badge">默认 20 个</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.download_count" min="1" @input="updateNumberField('download_count', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">延迟测速排序后，从最低延迟起进入下载测速的数量；当前默认 20 个。</div>
          </div>

          <div class="settings-field-card">
            <label class="form-label settings-form-label">下载测速时间 (-dt) <span class="settings-default-badge">默认 10 秒</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.download_time ?? ''" min="1" placeholder="10" @input="updateNumberField('download_time', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">单个 IP 下载测速的最长时间，官方默认 10 秒；该值不宜过短，否则测速结果容易失真。</div>
          </div>
          <div class="settings-field-card">
            <label class="form-label settings-form-label">测速端口 (-tp) <span class="settings-default-badge">默认 443</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.tcp_port ?? ''" min="1" max="65535" placeholder="443" @input="updateNumberField('tcp_port', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">延迟测速与下载测速共用的端口，官方默认 443；仅在目标站点明确使用其他端口时调整。</div>
          </div>
          <div class="settings-field-card">
            <label class="form-label settings-form-label">执行超时（秒） <span class="settings-default-badge settings-default-badge-warning">默认 300 秒</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.timeout_seconds ?? ''" min="30" max="3600" placeholder="300" @input="updateNumberField('timeout_seconds', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">后端等待本次 CFST 执行完成的最长时间，默认 300 秒（5 分钟）；网络慢、IP 段多或禁用下载测速时可适当调大。</div>
          </div>
          <div class="settings-field-card settings-field-card-full">
            <label class="form-label settings-form-label">测速地址 (-url) <span class="settings-default-badge">默认官方地址</span></label>
            <input type="text" class="form-control settings-standalone-input" :value="cfstForm.url" placeholder="https://cf.xiu2.xyz/url" @input="updateStringField('url', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">官方说明默认地址不保证长期可用，建议自建；HTTPing 与下载测速都会使用该地址。</div>
          </div>

          <div class="settings-field-card settings-field-card-full">
            <label class="form-label settings-form-label">额外命令行参数</label>
            <input type="text" class="form-control settings-standalone-input" :value="cfstForm.additional_args" placeholder="例如：-tl 300 -dn 20" @input="updateStringField('additional_args', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">将追加到显式配置参数之后；如需覆盖高级行为请确保与已配置参数不冲突，例如 `-dd`、`-p 0`、`-o result.csv` 等。</div>
          </div>
        </div>
      </section>

      <section class="settings-form-block">
        <div class="settings-block-heading settings-block-heading-split">
          <h4>过滤与阈值</h4>
          <p>对应官方 `-tl`、`-tll`、`-tlr`、`-sl` 参数，用于延迟排序后的过滤条件。</p>
        </div>

        <div class="settings-field-grid settings-field-grid-cfst-filter">
          <div class="settings-field-card">
            <label class="form-label settings-form-label">平均延迟下限 (-tll) <span class="settings-default-badge">默认 0 ms</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.min_delay ?? ''" min="0" placeholder="0" @input="updateNumberField('min_delay', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">只输出高于指定平均延迟的 IP，官方默认 0 ms；一般保持默认，仅在需要排除过低异常值时调整。</div>
          </div>
          <div class="settings-field-card">
            <label class="form-label settings-form-label">平均延迟上限 (-tl) <span class="settings-default-badge">默认 200 ms</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.max_delay" min="0" @input="updateNumberField('max_delay', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">只输出低于指定平均延迟的 IP；当前默认 200 ms。</div>
          </div>

          <div class="settings-field-card">
            <label class="form-label settings-form-label">丢包率上限 (-tlr) <span class="settings-default-badge">默认 1.00</span></label>
            <input type="number" step="0.01" class="form-control settings-standalone-input" :value="cfstForm.max_loss_rate ?? ''" min="0" max="1" placeholder="1" @input="updateNumberField('max_loss_rate', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">范围 0.00~1.00，0 表示过滤掉任何存在丢包的 IP；官方默认 1.00。</div>
          </div>
          <div class="settings-field-card">
            <label class="form-label settings-form-label">下载速度下限 (-sl) <span class="settings-default-badge">默认 0.00 MB/s</span></label>
            <input type="number" step="0.01" class="form-control settings-standalone-input" :value="cfstForm.min_speed ?? ''" min="0" placeholder="0" @input="updateNumberField('min_speed', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">只输出高于指定下载速度的 IP，官方默认 0.00 MB/s；如设置较高，建议同时设置 `-tl` 缩小候选范围。</div>
          </div>
        </div>
      </section>

      <section class="settings-form-block">
        <div class="settings-block-heading settings-block-heading-split">
          <h4>高级选项</h4>
          <p>对应官方 `-httping`、`-httping-code`、`-cfcolo`、`-allip`、`-debug` 参数。</p>
        </div>

        <div class="settings-auth-toggle-card settings-backup-toggle-card mb-3">
          <div class="settings-auth-toggle-copy">
            <span class="settings-field-label">测速模式</span>
            <strong>启用 HTTPing (-httping)</strong>
            <p>启用后延迟测速从默认 TCPing 切换为 HTTP 协议，并使用 `-url` 作为测试地址；服务器环境建议适当降低 `-n` 以减少被判定为扫描行为的风险。</p>
          </div>
          <label class="switch settings-auth-switch" for="cfst-httping">
            <input type="checkbox" id="cfst-httping" :checked="cfstForm.httping" @change="updateBooleanField('httping', ($event.target as HTMLInputElement).checked)">
            <div class="slider"><div class="circle"><svg class="cross" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 365.696 365.696" y="0" x="0" height="6" width="6" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"></path></g></svg><svg class="checkmark" xml:space="preserve" style="enable-background:new 0 0 512 512" viewBox="0 0 24 24" y="0" x="0" height="10" width="10" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" xmlns="http://www.w3.org/2000/svg"><g><path data-original="#000000" fill="currentColor" d="M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"></path></g></svg></div></div>
          </label>
        </div>

        <div class="settings-field-grid settings-field-grid-cfst-advanced">
          <div class="settings-field-card">
            <label class="form-label settings-form-label">有效状态码 (-httping-code) <span class="settings-default-badge">默认 200/301/302</span></label>
            <input type="text" class="form-control settings-standalone-input" :value="cfstForm.httping_code" placeholder="200" @input="updateStringField('httping_code', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">仅在 HTTPing 模式下生效；官方说明该参数用于指定有效 HTTP 状态码，默认接受 200 / 301 / 302。</div>
          </div>
          <div class="settings-field-card">
            <label class="form-label settings-form-label">地区码过滤 (-cfcolo)</label>
            <input type="text" class="form-control settings-standalone-input" :value="cfstForm.cfcolo" placeholder="HKG,LAX,SEA" @input="updateStringField('cfcolo', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">仅 HTTPing 模式可用；支持 <a href="https://www.cloudflarestatus.com/" target="_blank" rel="noreferrer">IATA 三字机场地区码</a> 或 <a href="https://zh.wikipedia.org/wiki/ISO_3166-1%E4%BA%8C%E4%BD%8D%E5%AD%97%E6%AF%8D%E4%BB%A3%E7%A0%81#%E6%AD%A3%E5%BC%8F%E5%88%86%E9%85%8D%E4%BB%A3%E7%A0%81" target="_blank" rel="noreferrer">二字国家码/城市码</a>，多个值用英文逗号分隔，大小写均可。</div>
          </div>
        </div>

        <div class="settings-toggle-grid mt-3">
          <label class="form-check settings-check-card">
            <input class="form-check-input" type="checkbox" :checked="cfstForm.test_all" @change="updateBooleanField('test_all', ($event.target as HTMLInputElement).checked)">
            <span>
              <strong>测速全部 IP (-allip)</strong>
              <small>官方说明仅支持 IPv4；开启后会对 IP 段中的每个 IP 逐个测速，耗时会显著增加。</small>
            </span>
          </label>
          <label class="form-check settings-check-card">
            <input class="form-check-input" type="checkbox" :checked="cfstForm.debug" @change="updateBooleanField('debug', ($event.target as HTMLInputElement).checked)">
            <span>
              <strong>调试输出 (-debug)</strong>
              <small>输出更多延迟测速与下载测速日志，适合排查 0 速、403、超时或 HTTP 状态码不符等问题。</small>
            </span>
          </label>
        </div>
      </section>

      <section class="settings-form-block">
        <div class="settings-block-heading settings-block-heading-split">
          <h4>结果与执行控制</h4>
          <p>对应官方 `-p` 与 `-dd` 参数，用于控制最终显示结果数量，以及是否跳过下载测速。</p>
        </div>

        <div class="settings-field-grid settings-field-grid-cfst-filter settings-cfst-result-control-grid">
          <div class="settings-field-card">
            <label class="form-label settings-form-label">显示结果数量 (-p) <span class="settings-default-badge">默认 10 个</span></label>
            <input type="number" class="form-control settings-standalone-input" :value="cfstForm.show_count ?? ''" min="0" placeholder="10" @input="updateNumberField('show_count', ($event.target as HTMLInputElement).value)">
            <div class="settings-field-hint">测速结束后直接展示的结果数量；设为 0 时不显示结果直接退出。</div>
          </div>

          <label class="form-check settings-check-card settings-check-card-half">
            <input class="form-check-input" type="checkbox" :checked="cfstForm.disable_download" @change="updateBooleanField('disable_download', ($event.target as HTMLInputElement).checked)">
            <span>
              <strong>禁用下载测速 (-dd)</strong>
              <small>开启后只按延迟排序，不执行下载测速，适合只看延迟优选或快速预筛选。</small>
            </span>
          </label>
        </div>
      </section>


      <slot />

      <div class="settings-auth-actions settings-cfst-bottom-actions cfst-inline-actions">
        <button type="button" class="settings-action-btn settings-action-neutral settings-refresh-like-test-btn justify-content-center" @click="$emit('refresh-results')" :disabled="loadingCfstResults || runningCfst">
          <span v-if="loadingCfstResults" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bx bx-refresh me-2"></i>刷新结果
        </button>
        <button type="button" class="settings-action-btn settings-action-success justify-content-center" @click="$emit('run-now')" :disabled="runningCfst || savingCfst">
          <span v-if="runningCfst" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bx bx-play-circle me-2"></i>
          {{ runningCfst ? '测速进行中' : '开始优选' }}
        </button>
        <button type="submit" class="settings-save-btn" :disabled="savingCfst">
          <span>
            <span v-if="savingCfst" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bx bx-save"></i>
            保存设置
          </span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { CfstFormState } from '@/types/settings';



type CfstNumberField =

  | 'threads'
  | 'ping_times'
  | 'download_count'
  | 'download_time'
  | 'timeout_seconds'
  | 'tcp_port'
  | 'min_delay'
  | 'max_delay'
  | 'max_loss_rate'
  | 'min_speed'
  | 'show_count';

type CfstStringField = 'url' | 'httping_code' | 'cfcolo' | 'additional_args';
type CfstBooleanField = 'httping' | 'test_all' | 'disable_download' | 'debug';

defineProps<{
  cfstForm: CfstFormState;
  savingCfst: boolean;
  runningCfst: boolean;
  loadingCfstResults: boolean;
}>();


const emit = defineEmits<{
  (event: 'submit'): void;
  (event: 'refresh-results'): void;
  (event: 'run-now'): void;
  <K extends keyof CfstFormState>(event: 'updateField', field: K, value: CfstFormState[K]): void;
}>();

const updateStringField = (field: CfstStringField, value: string) => {
  emit('updateField', field, value);
};

const updateNumberField = (field: CfstNumberField, value: string) => {
  emit('updateField', field, value === '' ? null : Number(value));
};

const updateBooleanField = (field: CfstBooleanField, value: boolean) => {
  emit('updateField', field, value);
};
</script>

<style scoped>
@media (max-width: 767.98px) {
  .cfst-inline-actions {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 0.55rem;
    align-items: stretch;
  }

  .cfst-inline-actions.settings-cfst-bottom-actions {
    flex-direction: row !important;
    align-items: stretch;
  }

  .cfst-inline-actions > *,
  .cfst-inline-actions.settings-cfst-bottom-actions > * {
    min-width: 0;
    width: auto !important;
  }

  .cfst-inline-actions .settings-action-btn,
  .cfst-inline-actions .settings-save-btn {
    width: 100% !important;
    min-width: 0;
    padding-inline: 0.65rem;
    font-size: 0.82rem;
    justify-content: center;
  }
}
</style>
