import { ref } from 'vue';

const show = ref(false);
const title = ref('');
const message = ref('');
let resolvePromise: ((value: boolean) => void) | null = null;

export function useConfirm() {
    const confirm = (msg: string, ttl: string = '确认操作') => {
        message.value = msg;
        title.value = ttl;
        show.value = true;
        return new Promise<boolean>((resolve) => {
            resolvePromise = resolve;
        });
    };

    const handleConfirm = () => {
        show.value = false;
        if (resolvePromise) {
            resolvePromise(true);
            resolvePromise = null;
        }
    };

    const handleCancel = () => {
        show.value = false;
        if (resolvePromise) {
            resolvePromise(false);
            resolvePromise = null;
        }
    };

    return {
        show,
        title,
        message,
        confirm,
        handleConfirm,
        handleCancel
    };
}
