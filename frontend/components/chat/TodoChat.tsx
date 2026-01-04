'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getSession } from '@/lib/auth-client';
import { CHATKIT_CONFIG, CHAT_API_URL } from '@/lib/chatkit/config';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
}

interface StartPrompt {
  label: string;
  prompt: string;
  icon: string;
}

/**
 * TodoChat component - AI-powered chat interface for task management.
 *
 * Provides a conversational interface for users to manage their tasks
 * through natural language interactions.
 */
export function TodoChat() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Get client secret on mount with retry logic for race conditions after login
  useEffect(() => {
    let isMounted = true;

    async function initSession(retries = 5, delayMs = 200) {
      for (let attempt = 0; attempt < retries; attempt++) {
        try {
          const res = await fetch('/api/chatkit/session', {
            method: 'POST',
            credentials: 'include',
          });

          if (!res.ok) {
            if (res.status === 401) {
              router.push('/login');
              return;
            }
            // For 503 (service unavailable), retry
            if (res.status === 503 && attempt < retries - 1) {
              await new Promise(resolve => setTimeout(resolve, delayMs * (attempt + 1)));
              continue;
            }
            throw new Error('Failed to create session');
          }

          const data = await res.json();
          if (isMounted) {
            setClientSecret(data.client_secret);
            setError(null);
          }
          return; // Success, exit
        } catch (err) {
          console.error(`Session attempt ${attempt + 1} failed:`, err);
          // Retry on network errors
          if (attempt < retries - 1) {
            await new Promise(resolve => setTimeout(resolve, delayMs * (attempt + 1)));
            continue;
          }
          if (isMounted) {
            setError('Failed to connect to chat service. Please refresh the page.');
          }
        }
      }
    }

    initSession();

    return () => {
      isMounted = false;
    };
  }, [router]);

  const sendMessage = useCallback(async (messageText: string) => {
    if (!messageText.trim() || !clientSecret || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: messageText.trim(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    // Create placeholder for assistant message
    const assistantId = `assistant-${Date.now()}`;
    setMessages(prev => [
      ...prev,
      { id: assistantId, role: 'assistant', content: '', isStreaming: true },
    ]);

    try {
      const response = await fetch(CHAT_API_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${clientSecret}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageText.trim(),
          conversation_id: conversationId,  // Send conversation_id to maintain context
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response stream');

      const decoder = new TextDecoder();
      let fullContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'conversation' && data.conversation_id) {
                // Store conversation_id for subsequent messages
                setConversationId(data.conversation_id);
              } else if (data.type === 'delta' && data.content) {
                fullContent += data.content;
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantId
                      ? { ...msg, content: fullContent }
                      : msg
                  )
                );
              } else if (data.type === 'done') {
                // Stream complete - also capture conversation_id if present
                if (data.conversation_id) {
                  setConversationId(data.conversation_id);
                }
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantId
                      ? { ...msg, content: data.content || fullContent, isStreaming: false }
                      : msg
                  )
                );
              } else if (data.type === 'error') {
                throw new Error(data.error);
              }
            } catch (parseError) {
              // Skip invalid JSON
            }
          }
        }
      }

      // Mark as complete
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantId
            ? { ...msg, isStreaming: false }
            : msg
        )
      );

      // Dispatch refresh event for task list sync
      window.dispatchEvent(new CustomEvent('refresh-tasks'));

    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantId
            ? {
                ...msg,
                content: "I'm having trouble connecting right now. Please try again in a moment.",
                isStreaming: false,
              }
            : msg
        )
      );
      setError(err instanceof Error ? err.message : 'Chat request failed');
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [clientSecret, isLoading, conversationId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handlePromptClick = (prompt: string) => {
    if (prompt.endsWith(' ')) {
      // Partial prompt - put in input for user to complete
      setInput(prompt);
      inputRef.current?.focus();
    } else {
      // Complete prompt - send immediately
      sendMessage(prompt);
    }
  };

  const showStartScreen = messages.length === 0;

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] min-h-[300px] w-full max-w-2xl mx-auto bg-white dark:bg-gray-900 rounded-lg shadow-lg overflow-hidden">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-2 sm:p-4 space-y-3 sm:space-y-4">
        {showStartScreen ? (
          <div className="flex flex-col items-center justify-center h-full space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                {CHATKIT_CONFIG.startScreen.greeting}
              </h2>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {CHATKIT_CONFIG.startScreen.prompts.map((prompt: StartPrompt, index: number) => (
                <button
                  key={index}
                  onClick={() => handlePromptClick(prompt.prompt)}
                  className="px-4 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors text-sm"
                >
                  {prompt.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[80%] rounded-lg px-3 sm:px-4 py-2 text-sm sm:text-base ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  {message.isStreaming && (
                    <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1" />
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="px-4 py-2 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Input area */}
      <form onSubmit={handleSubmit} className="border-t dark:border-gray-700 p-2 sm:p-4">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            disabled={isLoading || !clientSecret}
            className="flex-1 min-w-0 px-3 sm:px-4 py-2 border dark:border-gray-700 rounded-full bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 text-sm sm:text-base"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || !clientSecret}
            className="flex-shrink-0 px-4 sm:px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
          >
            {isLoading ? (
              <span className="inline-block w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              'Send'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
