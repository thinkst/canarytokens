<template>
	<BaseModal
		documentation-link="" :has-back-button="false" :title="`Delete token`">
		<span class="relative mb-16">
			<img
				:src="getImageUrl(`token_icons/${tokenServices[props.type].icon}`)" :alt="`${tokenServices[props.type].label}`"
				class="w-[6rem]">
			<img
				:src="getImageUrl(`token_icons/delete_token_badge.png`)" :alt="`${tokenServices[props.type].label}`"
				class="absolute w-[1.3rem] bottom-[.5rem] right-[.3rem]" />
		</span>
		<div class="text-center">
			<p class="text-xl font-semibold leading-normal text-grey-800">Are you sure you want to delete this token?</p>
			<p class="text-normal leading-normal text-grey-300 mt-8">All associated alerts will be permanently lost</p>
		</div>
		<template #footer>
			<div>
				<BaseMessageBox
					v-if="errorMessage || successMessage"
					:class="`w-[90%] m-auto ${errorMessage ? 'mb-16' : ''}`"
					:variant="successMessage ? 'success' : 'danger'"
					:message="errorMessage || successMessage" />
				<div v-if="!successMessage" class="w-full flex flex-row justify-center">
					<BaseButton variant="grey" class="mr-8" @click="closeModal()">No, keep it</BaseButton>
					<BaseButton variant="danger" :loading="isLoading" @click="deleteToken()">Yes, delete</BaseButton>
				</div>
			</div>
		</template>
	</BaseModal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { tokenServices } from '@/utils/tokenServices';
import getImageUrl from '@/utils/getImageUrl';
import { deleteToken as deleteTokenFnc } from '@/api/main';

const router = useRouter();

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const props = defineProps<{
	auth: string;
	token: string;
	type: string;
	closeModal: () => void;
}>();

const deleteToken = async () => {
	isLoading.value = true;
	errorMessage.value = '';
	const params = {
		auth: props.auth,
		token: props.token,
	};

	try {
		const res = await deleteTokenFnc(params);
		if (res.status === 200) {
			successMessage.value = 'Yay! Your token, plus associated alerts, has been successfully deleted.'
			setTimeout(() => {
				props.closeModal()
				router.push({ name: 'home' });
			}, 3000);
		}
		else if (res.status === 404) {
			props.closeModal();
			router.push({ name: 'error' });
		}
		else errorMessage.value = 'Oh no! Something went wrong when deleting your token.';
	} catch (err: any) {
		console.log(err, 'err!');
		errorMessage.value = err.toString();
	} finally {
		isLoading.value = false;
	}
}
</script>
