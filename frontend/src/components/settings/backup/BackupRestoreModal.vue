<template>
  <Teleport to="body">
    <div v-if="visible" class="modal fade show settings-backup-modal" style="display: block;" tabindex="-1" @click.self="$emit('close')">
      <div class="modal-dialog modal-dialog-centered settings-backup-modal-dialog">
        <div class="modal-content settings-backup-modal-content">
          <div class="modal-header settings-backup-modal-header">
            <h5 class="modal-title">恢复备份</h5>
            <button type="button" class="btn-close settings-backup-modal-close" @click="$emit('close')"></button>
          </div>
          <div class="modal-body settings-backup-modal-body">
            <div v-if="loadingBackups" class="settings-backup-modal-state text-center py-4">
              <div class="spinner-border text-primary" role="status"></div>
              <p class="mt-2 text-muted">正在获取备份列表...</p>
            </div>
            <div v-else-if="backups.length === 0" class="settings-backup-modal-state text-center py-4 text-muted">
              未找到备份文件
            </div>
            <div v-else class="list-group list-group-flush settings-backup-list">
              <div
                v-for="group in groupedBackups"
                :key="group.key"
                class="list-group-item d-flex justify-content-between align-items-center bg-transparent text-main border-0 rounded-3 mb-1 backup-item settings-backup-item-row"
              >
                <div class="settings-backup-item-main">
                  <div>
                    <div class="fw-bold">{{ group.file }}</div>
                    <div class="settings-backup-group-list">
                      <div
                        v-for="item in group.items"
                        :key="item.id"
                        class="settings-backup-group-entry"
                      >
                        <div class="settings-backup-group-meta">
                          <span
                            class="settings-chip"
                            :class="item.source === 'remote' ? 'settings-chip-info' : 'settings-chip-success'"
                          >
                            {{ item.source === 'remote' ? '远程' : '本地' }}
                          </span>
                          <small class="text-muted">{{ formatBackupTime(item.created_at) }} ({{ formatSize(item.size) }})</small>
                        </div>

                        <div class="settings-backup-item-actions settings-backup-item-actions-inline">
                          <button
                            type="button"
                            class="settings-action-btn settings-action-success settings-backup-restore-btn"
                            @click="$emit('restore', item)"
                            :disabled="restoringBackup || deletingBackupId === item.id"
                          >
                            <span v-if="restoringBackup" class="spinner-border spinner-border-sm me-1"></span>
                            <i v-else class="bx bx-reset me-1"></i>
                            恢复
                          </button>

                          <button
                            type="button"
                            class="settings-action-btn settings-action-danger settings-backup-delete-btn"
                            @click.stop="$emit('delete', item)"
                            :disabled="restoringBackup || deletingBackupId === item.id"
                          >
                            <span v-if="deletingBackupId === item.id" class="spinner-border spinner-border-sm me-1"></span>
                            <i v-else class="bx bx-trash me-1"></i>
                            删除
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { BackupGroupedItem, BackupItem } from '@/types/settings';

const props = defineProps<{
  visible: boolean;
  loadingBackups: boolean;
  backups: BackupItem[];
  restoringBackup: boolean;
  deletingBackupId: string | null;
  formatBackupTime: (value: string) => string;
  formatSize: (value: number) => string;
}>();

const groupedBackups = computed<BackupGroupedItem[]>(() => {
  const groups = new Map<string, BackupGroupedItem>();

  for (const backup of props.backups) {
    const key = String(backup.file || backup.filename || backup.id || '').trim();
    if (!key) continue;

    const existing = groups.get(key);
    if (existing) {
      existing.items.push(backup);
      existing.total_size += Number(backup.size || 0);
      if (backup.created_at < existing.created_at) {
        existing.created_at = backup.created_at;
      }
      continue;
    }

    groups.set(key, {
      key,
      file: backup.file || backup.filename || backup.id,
      created_at: backup.created_at,
      total_size: Number(backup.size || 0),
      items: [backup],
    });
  }

  return Array.from(groups.values()).map((group) => ({
    ...group,
    items: [...group.items].sort((a, b) => {
      const sourceA = a.source === 'remote' ? 1 : 0;
      const sourceB = b.source === 'remote' ? 1 : 0;
      return sourceA - sourceB;
    }),
  }));
});

defineEmits<{
  close: [];
  restore: [backup: BackupItem];
  delete: [backup: BackupItem];
}>();
</script>
