#!/usr/bin/env python3
"""
JWT Auth Scaffolding Generator
==============================
Generates authentication boilerplate for FastAPI backend and Next.js frontend.

Usage:
    python generate_auth.py --output-dir <path>
    python generate_auth.py --backend-only --output-dir backend
    python generate_auth.py --frontend-only --output-dir frontend

Examples:
    python generate_auth.py --output-dir .
    python generate_auth.py --backend-only --output-dir backend/app
    python generate_auth.py --frontend-only --output-dir frontend/src
"""

import argparse
import os
from pathlib import Path


# Backend templates
BACKEND_AUTH_PY = '''"""
JWT Authentication Utilities
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
'''

BACKEND_DEPENDENCIES_PY = '''"""
FastAPI Authentication Dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.models.user import User
from app.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await session.get(User, int(user_id))
    if user is None:
        raise credentials_exception

    return user
'''

BACKEND_ENV_EXAMPLE = '''# Authentication
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/todoapp
'''

# Frontend templates
FRONTEND_AUTH_CONTEXT = ''''use client';

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface User {
  id: number;
  email: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const fetchUser = useCallback(async (authToken: string) => {
    try {
      const res = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (res.ok) {
        setUser(await res.json());
        return true;
      }
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      return false;
    } catch {
      return false;
    }
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken).finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [fetchUser]);

  const login = async (email: string, password: string) => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: email, password }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail);
    }
    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
    await fetchUser(data.access_token);
    router.push('/dashboard');
  };

  const signup = async (email: string, username: string, password: string) => {
    const res = await fetch(`${API_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password }),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Signup failed' }));
      throw new Error(error.detail);
    }
    await login(email, password);
  };

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    router.push('/login');
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, isAuthenticated: !!user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

export const getAuthToken = () => typeof window !== 'undefined' ? localStorage.getItem('token') : null;
'''

FRONTEND_ENV_EXAMPLE = '''NEXT_PUBLIC_API_URL=http://localhost:8000
'''


def generate_backend(output_dir: str) -> list[str]:
    """Generate backend auth files."""
    files = []
    base = Path(output_dir)

    # Create directories
    (base / "app").mkdir(parents=True, exist_ok=True)

    # Write files
    auth_file = base / "app" / "auth.py"
    auth_file.write_text(BACKEND_AUTH_PY)
    files.append(str(auth_file))

    deps_file = base / "app" / "dependencies.py"
    deps_file.write_text(BACKEND_DEPENDENCIES_PY)
    files.append(str(deps_file))

    env_file = base / ".env.example"
    env_file.write_text(BACKEND_ENV_EXAMPLE)
    files.append(str(env_file))

    return files


def generate_frontend(output_dir: str) -> list[str]:
    """Generate frontend auth files."""
    files = []
    base = Path(output_dir)

    # Create directories
    (base / "lib").mkdir(parents=True, exist_ok=True)
    (base / "components").mkdir(parents=True, exist_ok=True)

    # Write files
    auth_file = base / "components" / "AuthProvider.tsx"
    auth_file.write_text(FRONTEND_AUTH_CONTEXT)
    files.append(str(auth_file))

    env_file = base / ".env.example"
    env_file.write_text(FRONTEND_ENV_EXAMPLE)
    files.append(str(env_file))

    return files


def main():
    parser = argparse.ArgumentParser(description="Generate JWT auth scaffolding")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory")
    parser.add_argument("--backend-only", action="store_true", help="Generate backend only")
    parser.add_argument("--frontend-only", action="store_true", help="Generate frontend only")

    args = parser.parse_args()

    files = []

    if args.backend_only:
        files = generate_backend(args.output_dir)
        print("Generated backend auth files:")
    elif args.frontend_only:
        files = generate_frontend(args.output_dir)
        print("Generated frontend auth files:")
    else:
        # Generate both
        backend_dir = Path(args.output_dir) / "backend"
        frontend_dir = Path(args.output_dir) / "frontend"
        files.extend(generate_backend(str(backend_dir)))
        files.extend(generate_frontend(str(frontend_dir)))
        print("Generated auth scaffolding:")

    for f in files:
        print(f"  {f}")

    print()
    print("Next steps:")
    print("  1. Copy .env.example to .env and configure secrets")
    print("  2. Install dependencies (python-jose, passlib, bcrypt)")
    print("  3. Add auth routes to your FastAPI app")
    print("  4. Wrap your Next.js app with AuthProvider")


if __name__ == "__main__":
    main()
