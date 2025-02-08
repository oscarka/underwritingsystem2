<template>
  <div class="basic-info">
    <h1 class="page-title">基本信息</h1>
    
    <van-form @submit="handleSubmit" class="basic-info__form">
      <van-cell-group inset>
        <van-field
          v-model="form.name"
          name="name"
          label="姓名"
          placeholder="请输入姓名"
          :rules="[{ required: true, message: '请输入姓名' }]"
        />
        
        <van-field
          v-model="form.age"
          type="digit"
          name="age"
          label="年龄"
          placeholder="请输入年龄"
          :rules="[
            { required: true, message: '请输入年龄' },
            { validator: validateAge, message: '年龄必须在18-80岁之间' }
          ]"
        />
        
        <van-field name="gender" label="性别">
          <template #input>
            <van-radio-group v-model="form.gender" direction="horizontal">
              <van-radio name="male">男</van-radio>
              <van-radio name="female">女</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        
        <van-field
          v-model="form.height"
          type="digit"
          name="height"
          label="身高(CM)"
          placeholder="请输入身高"
          :rules="[
            { required: true, message: '请输入身高' },
            { validator: validateHeight, message: '请输入有效身高(140-200cm)' }
          ]"
        />
        
        <van-field
          v-model="form.weight"
          type="digit"
          name="weight"
          label="体重(KG)"
          placeholder="请输入体重"
          :rules="[
            { required: true, message: '请输入体重' },
            { validator: validateWeight, message: '请输入有效体重(30-150kg)' }
          ]"
        />
        
        <van-field
          v-model="form.policyNumber"
          name="policyNumber"
          label="保单号"
          placeholder="请输入保单号"
          :rules="[
            { required: true, message: '请输入保单号' },
            { pattern: /^P\d{13}$/, message: '保单号格式不正确' }
          ]"
        />
        
        <van-field name="idType" label="证件类型">
          <template #input>
            <van-radio-group v-model="form.idType" direction="horizontal">
              <van-radio name="id_card">身份证</van-radio>
              <van-radio name="passport">护照</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        
        <van-field
          v-model="form.idNumber"
          name="idNumber"
          label="证件号码"
          placeholder="请输入证件号码"
          :rules="[
            { required: true, message: '请输入证件号码' },
            { validator: validateIdNo, message: '请输入有效的证件号码' }
          ]"
        />
      </van-cell-group>

      <div class="form-actions">
        <van-button 
          round 
          block 
          type="primary" 
          native-type="submit"
          :loading="loading"
        >
          {{ loading ? '保存中...' : '下一步' }}
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import type { UserInfo } from '@/api/types/user';
import { showToast, showDialog } from 'vant';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const form = ref<UserInfo>({
  name: '张三',
  age: 30,
  gender: 'male',
  height: 175,
  weight: 65,
  policyNumber: 'P' + new Date().getTime(),
  idType: 'id_card',
  idNumber: '110101199001011234',
  phone: '13800138000',
  email: 'zhangsan@example.com'
});

const loading = ref(false);

// 证件类型选项
const idTypeOptions = [
  { text: '身份证', value: 'id_card' },
  { text: '护照', value: 'passport' },
  { text: '其他', value: 'other' },
];

// 表单验证函数
const validateAge = (val: string) => {
  const age = parseInt(val);
  return age >= 18 && age <= 80;
};

const validateHeight = (val: string) => {
  const height = parseInt(val);
  return height >= 140 && height <= 200;
};

const validateWeight = (val: string) => {
  const weight = parseInt(val);
  return weight >= 30 && weight <= 150;
};

const validateIdNo = (val: string) => {
  if (form.value.idType === 'id_card') {
    return /^\d{17}[\dX]$/.test(val);
  }
  return true;
};

// 提交表单
const handleSubmit = async () => {
  loading.value = true;
  try {
    console.log('正在保存用户信息...', form.value);
    userStore.setUserInfo(form.value);
    
    if (userStore.isComplete) {
      const productId = route.params.productId;
      await router.push(`/product/${productId}/disease`);
    } else {
      showDialog({
        title: '提示',
        message: '请填写完整的信息',
      });
    }
  } catch (error) {
    console.error('保存失败:', error);
    showToast({
      type: 'fail',
      message: '保存失败，请重试',
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.basic-info {
  padding: 16px;
}

.basic-info__form {
  margin-top: 16px;
}

:deep(.van-radio-group) {
  display: flex;
  gap: 16px;
}

:deep(.van-dropdown-menu) {
  height: 24px;
}

:deep(.van-dropdown-menu__bar) {
  box-shadow: none;
}
</style> 