import { NextRequest } from 'next/server';

// Use internal backend URL for server-side requests
const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 'http://localhost:8000';

/**
 * POST /api/chatkit/chat
 *
 * Proxies chat requests to the backend ChatKit endpoint with streaming support.
 * This allows the browser to make requests to a relative URL which Next.js proxies to the backend.
 */
export async function POST(request: NextRequest) {
  try {
    // Get Authorization header (client_secret)
    const authHeader = request.headers.get('Authorization');

    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized', code: 'UNAUTHORIZED' }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Get request body
    const body = await request.json();

    // Forward to backend chatkit endpoint
    const response = await fetch(`${BACKEND_URL}/chatkit`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Backend error' }));
      return new Response(
        JSON.stringify({
          error: error.error || 'Chat request failed',
          code: 'CHAT_ERROR'
        }),
        {
          status: response.status,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Stream the response back to the client
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    console.error('ChatKit proxy error:', error);
    return new Response(
      JSON.stringify({
        error: 'Internal server error',
        code: 'INTERNAL_ERROR'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}
