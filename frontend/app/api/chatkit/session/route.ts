import { NextRequest, NextResponse } from 'next/server';

// Use internal backend URL for server-side requests
const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || 'http://localhost:8000';

/**
 * POST /api/chatkit/session
 *
 * Creates a ChatKit session by:
 * 1. Extracting the JWT token from Authorization header
 * 2. Forwarding to backend to create a ChatKit client_secret
 *
 * The frontend should send the JWT token from localStorage in the Authorization header.
 */
export async function POST(request: NextRequest) {
  try {
    // Get JWT token from Authorization header
    const authHeader = request.headers.get('Authorization');

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Unauthorized', code: 'UNAUTHORIZED' },
        { status: 401 }
      );
    }

    const token = authHeader.replace('Bearer ', '');

    // Forward to backend session endpoint
    const response = await fetch(`${BACKEND_URL}/api/chatkit/session`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
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
