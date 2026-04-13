<template>
  <n-form :model="modelValue" label-placement="left" label-width="120px">
    <n-form-item v-if="showName" label="应用名称" required>
      <n-input
        :value="modelValue.name"
        placeholder="my-service"
        :disabled="nameDisabled"
        @update:value="updateField('name', $event)"
      />
    </n-form-item>
    <n-form-item label="应用说明">
      <n-input
        :value="modelValue.description"
        placeholder="例如：PL2 录制源 / VT 缺陷环境"
        @update:value="updateField('description', $event)"
      />
    </n-form-item>
    <n-form-item label="SSH Host" required>
      <n-input
        :value="modelValue.ssh_host"
        placeholder="192.168.1.100"
        @update:value="updateField('ssh_host', $event)"
      />
    </n-form-item>
    <n-form-item label="SSH User" required>
      <n-input
        :value="modelValue.ssh_user"
        placeholder="root"
        @update:value="updateField('ssh_user', $event)"
      />
    </n-form-item>
    <n-form-item label="认证方式">
      <n-select
        :value="modelValue.ssh_auth_type"
        :options="authOptions"
        @update:value="updateField('ssh_auth_type', $event)"
      />
    </n-form-item>
    <n-form-item v-if="modelValue.ssh_auth_type === 'KEY'" label="私钥路径">
      <n-input
        :value="modelValue.ssh_key_path"
        placeholder="/root/.ssh/id_rsa"
        @update:value="updateField('ssh_key_path', $event)"
      />
    </n-form-item>
    <n-form-item v-else label="SSH 密码">
      <n-input
        :value="modelValue.ssh_password"
        type="password"
        @update:value="updateField('ssh_password', $event)"
      />
    </n-form-item>
    <n-form-item label="JAR 名称">
      <n-input
        :value="modelValue.java_jar_name"
        placeholder="my-service.jar"
        @update:value="updateField('java_jar_name', $event)"
      />
    </n-form-item>
    <n-form-item label="应用端口">
      <n-input-number
        :value="modelValue.repeater_port"
        :min="1"
        :max="65535"
        @update:value="updateNumberField('repeater_port', $event, 8080)"
      />
    </n-form-item>
    <n-form-item label="高级配置">
      <n-space vertical style="width: 100%">
        <n-button tertiary size="small" @click="emit('update:showAdvanced', !showAdvanced)">
          {{ showAdvanced ? '收起高级配置' : '展开高级配置' }}
        </n-button>
        <n-alert v-if="showAdvanced && showAdvancedGuide" type="info" :show-icon="false">
          银行 / XML 场景建议配置“接口识别字段”和“默认忽略字段”。同一路径多交易码接口会按这里配置的字段识别，例如
          <n-text code>service_id</n-text>、
          <n-text code>trand_id</n-text>。
        </n-alert>
      </n-space>
    </n-form-item>
    <template v-if="showAdvanced">
      <n-form-item label="SSH 端口">
        <n-input-number
          :value="modelValue.ssh_port"
          :min="1"
          :max="65535"
          @update:value="updateNumberField('ssh_port', $event, 22)"
        />
      </n-form-item>
      <n-form-item label="Sandbox 端口">
        <n-input-number
          :value="modelValue.sandbox_port"
          :min="1"
          :max="65535"
          @update:value="updateNumberField('sandbox_port', $event, 39393)"
        />
      </n-form-item>
      <n-form-item label="Sandbox 路径">
        <n-input
          :value="modelValue.sandbox_home"
          placeholder="/root/.sandbox"
          @update:value="updateField('sandbox_home', $event)"
        />
      </n-form-item>
      <n-form-item label="录制数据目录">
        <n-input
          :value="modelValue.repeater_data_dir"
          placeholder="/root/.sandbox-module/repeater-data/record"
          @update:value="updateField('repeater_data_dir', $event)"
        />
      </n-form-item>
      <n-form-item label="采样率">
        <n-space align="center">
          <n-input-number
            :value="modelValue.sample_rate_percent"
            :min="1"
            :max="100"
            @update:value="updateNumberField('sample_rate_percent', $event, 100)"
          />
          <span>%</span>
        </n-space>
      </n-form-item>
      <n-form-item label="接口识别字段">
        <n-dynamic-tags
          :value="modelValue.operation_id_tags"
          @update:value="updateField('operation_id_tags', $event)"
        />
        <template v-if="showAdvancedGuide" #feedback>
          留空也可用，系统会自动识别 <n-text code>service_id</n-text>、<n-text code>trand_id</n-text>、<n-text code>transCode</n-text> 等常见字段。
        </template>
      </n-form-item>
      <n-form-item label="默认忽略字段">
        <n-dynamic-tags
          :value="modelValue.default_ignore_fields"
          @update:value="updateField('default_ignore_fields', $event)"
        />
        <template v-if="showAdvancedGuide" #feedback>
          这里的字段会在发起回放时作为默认值自动带入。
        </template>
      </n-form-item>
    </template>
  </n-form>
</template>

<script setup lang="ts">
import { toRefs } from 'vue'
import {
  NAlert,
  NButton,
  NDynamicTags,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSelect,
  NSpace,
  NText,
} from 'naive-ui'

import type { ApplicationAuthType, ApplicationEditorModel } from '@/utils/applicationEditor'

const props = withDefaults(defineProps<{
  modelValue: ApplicationEditorModel
  showName?: boolean
  nameDisabled?: boolean
  showAdvanced?: boolean
  showAdvancedGuide?: boolean
}>(), {
  showName: true,
  nameDisabled: false,
  showAdvanced: false,
  showAdvancedGuide: true,
})
const { modelValue, nameDisabled, showAdvanced, showAdvancedGuide, showName } = toRefs(props)

const emit = defineEmits<{
  'update:modelValue': [value: ApplicationEditorModel]
  'update:showAdvanced': [value: boolean]
}>()

const authOptions: Array<{ label: string; value: ApplicationAuthType }> = [
  { label: 'SSH Key', value: 'KEY' },
  { label: '密码', value: 'PASSWORD' },
]

function updateField<K extends keyof ApplicationEditorModel>(
  key: K,
  value: ApplicationEditorModel[K],
) {
  emit('update:modelValue', {
    ...props.modelValue,
    [key]: value,
  })
}

function updateNumberField<K extends keyof ApplicationEditorModel>(
  key: K,
  value: number | null,
  fallback: number,
) {
  updateField(key, (value ?? fallback) as ApplicationEditorModel[K])
}
</script>
