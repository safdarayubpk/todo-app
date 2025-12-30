import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * POST /api/chatkit/session
 *
 * Creates a ChatKit session by:
 * 1. Validating the user's Better Auth session
 * 2. Getting a JWT token from Better Auth
 * 3. Forwarding to backend to create a ChatKit client_secret
 */
export async function POST(request: NextRequest) {
  try {
    // Get the session from Better Auth
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session?.session || !session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'UNAUTHORIZED' },
        { status: 401 }
      );
    }

    // Get JWT token from Better Auth
    const tokenResponse = await auth.api.getToken({
      headers: await headers(),
    });

    if (!tokenResponse?.token) {
      return NextResponse.json(
        { error: 'Failed to get auth token', code: 'TOKEN_ERROR' },
        { status: 500 }
      );
    }

    // Forward to backend session endpoint
    const backendUrl = API_URL.replace('/api/v1', '');
    const response = await fetch(`${backendUrl}/api/chatkit/session`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokenResponse.token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Backend error' }));
      return NextResponse.json(
        { error: error.error || 'Failed to create session', code: 'SESSION_ERROR' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('ChatKit session error:', error);
    return NextResponse.json(
      { error: 'Internal server error', code: 'INTERNAL_ERROR' },
      { status: 500 }
    );
  }
}
