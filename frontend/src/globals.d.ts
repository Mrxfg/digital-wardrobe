export {};

declare global {
  interface Window {
    Telegram: {
      WebApp: {
        ready: () => void;
        expand: () => void;
        enableClosingConfirmation: () => void;
        close: () => void;
        colorScheme: 'light' | 'dark';
        themeParams: {
          bg_color?: string;
          secondary_bg_color?: string;
          button_color?: string;
          button_text_color?: string;
          hint_color?: string;
          text_color?: string;
          accent_text_color?: string;
          destructive_text_color?: string;
        };
        HapticFeedback: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy') => void;
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
          selectionChanged: () => void;
        };
        showAlert: (message: string, callback?: () => void) => void;
        showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void;
        initDataUnsafe?: {
          user?: {
            id: number;
            first_name?: string;
            last_name?: string;
            username?: string;
            language_code?: string;
          };
        };
      };
    };
  }
}
