import { ref, onMounted, onUnmounted } from 'vue';

export function useMobile(breakpoint = 992) {
    const isMobile = ref(window.innerWidth < breakpoint);

    const checkMobile = () => {
        isMobile.value = window.innerWidth < breakpoint;
    };

    onMounted(() => {
        window.addEventListener('resize', checkMobile);
        checkMobile(); // Initial check
    });

    onUnmounted(() => {
        window.removeEventListener('resize', checkMobile);
    });

    return {
        isMobile
    };
}
