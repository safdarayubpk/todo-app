/**
 * ChatKit configuration for the AI Todo Chatbot.
 */

export const CHATKIT_CONFIG = {
  /** Backend ChatKit endpoint URL */
  backendUrl: process.env.NEXT_PUBLIC_CHATKIT_URL || 'http://localhost:8000/chatkit',

  /** Theme for the chat widget */
  theme: 'light' as const,

  /** Start screen configuration */
  startScreen: {
    greeting: 'Hi! I can help you manage your tasks. What would you like to do?',
    prompts: [
      {
        label: 'Show my tasks',
        prompt: 'Show me all my tasks',
        icon: 'list',
      },
      {
        label: 'Add a task',
        prompt: 'Add a task to ',
        icon: 'plus',
      },
      {
        label: 'What can you do?',
        prompt: 'What can you help me with?',
        icon: 'help-circle',
      },
    ],
  },
};

/** API URL for session management */
export const CHATKIT_SESSION_URL = '/api/chatkit/session';

/** Chat backend URL for direct streaming */
export const CHAT_API_URL = process.env.NEXT_PUBLIC_CHATKIT_URL || 'http://localhost:8000/chatkit';
