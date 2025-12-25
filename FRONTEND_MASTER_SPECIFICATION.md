# 🔥 GDB React Frontend — MASTER SPECIFICATION & EXECUTION GUIDE

**Status:** Ready for Development  
**Date:** December 25, 2025  
**Audience:** Frontend Engineers & Trainees  
**Priority:** PRODUCTION GRADE  

---

## 📑 Table of Contents

1. [Core Identity](#1-core-identity)
2. [UI Theme & Design System](#2-ui-theme--design-system)
3. [Technology Stack](#3-technology-stack)
4. [Backend Integration](#4-backend-integration)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [Folder Structure](#6-folder-structure)
7. [Phase-by-Phase Implementation](#7-phase-by-phase-implementation)
8. [Coding Standards](#8-coding-standards)
9. [Quality Checklist](#9-quality-checklist)

---

## 1. Core Identity

### 🎯 What We're Building

A **professional enterprise banking UI** for GDB (Global Digital Bank) — a microservices-based digital banking system.

| Aspect | Details |
|--------|---------|
| **Purpose** | Production-grade banking frontend for internal use, demos, and training |
| **Audience** | Bank employees, customers, trainees |
| **Inspiration** | ICICI / HDFC / Axis banking portals |
| **Scope** | User management, Account management, Transactions |
| **Constraint** | **BACKEND IS LOCKED — NO CHANGES ALLOWED** |

### 🚫 What We're NOT Building

```
❌ Flashy animations
❌ Gimmicky effects
❌ Consumer-facing design
❌ Gaming elements
❌ Experimental UX
```

---

## 2. UI Theme & Design System

### 🎨 Design Philosophy

**Clean. Minimal. Corporate. Professional.**

* **Typography:** System fonts (San Francisco, Segoe UI)
* **Spacing:** 8px grid system
* **Borders:** Subtle, professional
* **Animations:** None (unless critical UX)
* **Accessibility:** WCAG AA compliant

### 🎯 Color Palette (MANDATORY)

```
┌─────────────────────────────────────────────────────────┐
│ PRIMARY COLORS                                          │
├─────────────────────────────────────────────────────────┤
│ Deep Blue        #1E3A8A  (Primary brand color)        │
│ Dark Slate       #0F172A  (Secondary, dark contexts)   │
│ Action Blue      #2563EB  (Buttons, links, interactive)│
├─────────────────────────────────────────────────────────┤
│ SEMANTIC COLORS                                         │
├─────────────────────────────────────────────────────────┤
│ Success Green    #16A34A  (Confirmations, success)     │
│ Error Red        #DC2626  (Errors, warnings, danger)   │
│ Warning Amber    #D97706  (Cautions, attention needed) │
│ Info Blue        #0284C7  (Info messages)              │
├─────────────────────────────────────────────────────────┤
│ NEUTRAL COLORS                                          │
├─────────────────────────────────────────────────────────┤
│ Background      #F8FAFC  (Page background)             │
│ Card/Surface    #FFFFFF  (Card backgrounds)            │
│ Border Light    #E2E8F0  (Subtle borders)              │
│ Border Dark     #CBD5E1  (Stronger borders)            │
│ Text Primary    #0F172A  (Main text)                   │
│ Text Secondary  #475569  (Secondary text)              │
│ Text Tertiary   #94A3B8  (Disabled, helper text)       │
└─────────────────────────────────────────────────────────┘
```

### 🧱 Layout Architecture

#### Sidebar Navigation (Left)
```
┌────────────────────┐
│  GDB LOGO          │  ← 64px height
├────────────────────┤
│ Dashboard          │  ← Current user info
│ Users              │     Role badge
│ Accounts           │  ← Navigation menu
│ Transactions       │
│ Settings           │
│ Logout             │
└────────────────────┘
```

**Rules:**
- Width: 256px (expanded) / 80px (collapsed)
- Background: `#0F172A` (dark slate)
- Text: White
- Collapse button: Hamburger icon
- Active menu item highlight: `#2563EB`

#### Top Navbar
```
┌──────────────────────────────────────────────────┐
│ GDB LOGO  |  Page Title              John Doe ✓ │
│           |                         Customer | ↓│
│           |                         Logout   |  │
└──────────────────────────────────────────────────┘
```

**Rules:**
- Height: 64px
- Background: `#FFFFFF` with subtle border
- Shadow: Light box-shadow (0 1px 3px rgba)
- Elements right-aligned: username, role badge, logout

#### Main Content Area
```
┌─────────────────────────────────────┐
│  ← Sidebar                          │
│                                     │
│  ┌────────────────────────────────┐ │
│  │  PAGE TITLE                    │ │
│  │  Breadcrumbs (if applicable)   │ │
│  ├────────────────────────────────┤ │
│  │                                │ │
│  │  Content in Cards/Tables       │ │
│  │                                │ │
│  └────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

**Rules:**
- Background: `#F8FAFC` (light)
- Cards: `#FFFFFF` with 1px border (`#E2E8F0`)
- Padding: 24px
- Card shadow: `0 1px 3px rgba(0,0,0,0.1)`
- Max content width: 1400px (centered)

### 🧩 Component Styles

#### Buttons

```
┌─────────────────────────────────────────────────┐
│ PRIMARY (SOLID BLUE)                            │
├─────────────────────────────────────────────────┤
│ Background:  #2563EB                            │
│ Text:        #FFFFFF                            │
│ Padding:     10px 16px                          │
│ Border:      None                               │
│ Hover:       #1D4ED8                            │
│ Active:      #1E40AF                            │
├─────────────────────────────────────────────────┤
│ SECONDARY (GHOST)                               │
├─────────────────────────────────────────────────┤
│ Background:  Transparent                        │
│ Text:        #1E3A8A                            │
│ Border:      1px #CBD5E1                        │
│ Hover:       Background: #F1F5F9                │
├─────────────────────────────────────────────────┤
│ DANGER (RED)                                    │
├─────────────────────────────────────────────────┤
│ Background:  #DC2626                            │
│ Text:        #FFFFFF                            │
│ Hover:       #B91C1C                            │
├─────────────────────────────────────────────────┤
│ DISABLED                                        │
├─────────────────────────────────────────────────┤
│ Background:  #E2E8F0                            │
│ Text:        #94A3B8                            │
│ Cursor:      not-allowed                        │
└─────────────────────────────────────────────────┘
```

#### Form Inputs

```
┌─────────────────────────────────────────────────┐
│ STRUCTURE                                       │
├─────────────────────────────────────────────────┤
│ Label (top)                                     │
│ Input field (border, subtle)                    │
│ Helper text (below, gray)                       │
│ Error message (below, red) [if error]           │
│                                                 │
│ Border:        1px #CBD5E1                      │
│ Focus:         Border #2563EB, shadow blue      │
│ Background:    #FFFFFF                          │
│ Padding:       10px 12px                        │
│ Border-radius: 6px                              │
│                                                 │
│ Error Border:  1px #DC2626                      │
│ Error BG:      #FEE2E2 (light red)              │
└─────────────────────────────────────────────────┘
```

#### Tables

```
┌─────────────────────────────────────────────────┐
│ Header Row (Dark background)                    │
├─────────────────────────────────────────────────┤
│ Column 1 │ Column 2 │ Column 3                 │
├─────────────────────────────────────────────────┤
│ Data 1   │ Data 2   │ Data 3                   │
├─────────────────────────────────────────────────┤
│ Data 4   │ Data 5   │ Data 6                   │
├─────────────────────────────────────────────────┤
│ Data 7   │ Data 8   │ Data 9                   │
└─────────────────────────────────────────────────┘

Rules:
- Header: #F1F5F9 background, bold text
- Borders: 1px #E2E8F0 (horizontal row dividers)
- Row hover: #F8FAFC background
- Sortable headers: cursor pointer, sort icon
- Pagination: centered, below table
```

#### Cards

```
┌─────────────────────────────────────────────────┐
│  CARD TITLE                            [Action] │
├─────────────────────────────────────────────────┤
│                                                 │
│  Card content displayed here                    │
│                                                 │
└─────────────────────────────────────────────────┘

Rules:
- Background: #FFFFFF
- Border: 1px #E2E8F0
- Border-radius: 8px
- Shadow: 0 1px 3px rgba(0,0,0,0.1)
- Padding: 16px
```

#### Status Badges

```
┌─────────────────────────────────────────────────┐
│ ACTIVE          ✓ Green background (#D1FAE5)   │
│ INACTIVE        ✗ Red background (#FEE2E2)     │
│ PREMIUM         ◆ Blue background (#DBEAFE)    │
│ GOLD            ◆ Amber background (#FEF3C7)   │
│ SILVER          ◆ Gray background (#E5E7EB)    │
│ ADMIN           🔐 Dark background              │
│ TELLER          👤 Light blue background        │
│ CUSTOMER        👥 Light gray background        │
└─────────────────────────────────────────────────┘
```

### 📱 Responsive Design (Desktop-First)

| Breakpoint | Width | Priority |
|-----------|-------|----------|
| Desktop | 1400px+ | **PRIMARY** |
| Tablet | 768px-1399px | Secondary |
| Mobile | <768px | Tertiary (basic support) |

---

## 3. Technology Stack

### 🔧 Locked Stack (NO ALTERNATIVES)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 18.x | UI library |
| **Language** | TypeScript | Type safety |
| **Build Tool** | Vite | Fast builds |
| **Routing** | React Router v6 | Client-side routing |
| **HTTP Client** | Axios | API calls |
| **State Management** | Context API | Global auth state |
| **Styling** | Tailwind CSS OR MUI | Pick ONE |
| **Icons** | lucide-react OR heroicons | Optional |

### ⚠️ What's Forbidden

```
❌ Redux (use Context API)
❌ Vue / Angular (must be React)
❌ CSS Modules (use Tailwind)
❌ Styled Components (use Tailwind)
❌ GraphQL (use REST API)
❌ Custom auth (use Context + JWT)
```

### 📦 Essential Dependencies

```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "react-router-dom": "^6.x",
    "axios": "^1.x",
    "tailwindcss": "^3.x"
  },
  "devDependencies": {
    "typescript": "^5.x",
    "vite": "^5.x",
    "@types/react": "^18.x",
    "@types/react-dom": "^18.x"
  }
}
```

---

## 4. Backend Integration

### 🔌 Service Endpoints (LOCKED)

| Service | Port | Base URL |
|---------|------|----------|
| Auth Service | 8004 | `http://localhost:8004` |
| Users Service | 8003 | `http://localhost:8003` |
| Accounts Service | 8001 | `http://localhost:8001` |
| Transactions Service | 8002 | `http://localhost:8002` |

### 📡 API Endpoints Reference

#### Auth Service (Port 8004)

```
POST /api/v1/auth/login
  Request:  { login_id, password }
  Response: { access_token, token_type, expires_in, user_id, login_id, role }

POST /api/v1/auth/verify-token
  Request:  { token }
  Response: { valid, message }

GET /api/v1/auth/me
  Headers:  Authorization: Bearer <token>
  Response: { user_id, login_id, role }
```

#### Users Service (Port 8003)

```
POST /api/v1/users
  Headers:  Authorization: Bearer <token>
  Request:  { username, login_id, password, role }
  Response: { user_id, username, login_id, role, is_active }

GET /api/v1/users/{user_id}
  Headers:  Authorization: Bearer <token>
  Response: { user_id, username, login_id, role, is_active, created_at }

PATCH /api/v1/users/{user_id}
  Headers:  Authorization: Bearer <token>
  Request:  { username?, password?, role? }
  Response: { user_id, ... }

PUT /api/v1/users/{user_id}/activate
  Headers:  Authorization: Bearer <token>
  Response: { user_id, is_active: true }

PUT /api/v1/users/{user_id}/inactivate
  Headers:  Authorization: Bearer <token>
  Response: { user_id, is_active: false }
```

#### Accounts Service (Port 8001)

```
POST /api/v1/accounts/savings
  Headers:  Authorization: Bearer <token>
  Request:  { name, privilege, pin, date_of_birth, gender, phone_no }
  Response: { account_number, account_type, balance, is_active }

POST /api/v1/accounts/current
  Headers:  Authorization: Bearer <token>
  Request:  { name, privilege, pin, company_name, website, registration_no }
  Response: { account_number, account_type, balance, is_active }

GET /api/v1/accounts/{account_number}
  Headers:  Authorization: Bearer <token>
  Response: { account_number, account_type, balance, privilege, is_active, ... }

PATCH /api/v1/accounts/{account_number}
  Headers:  Authorization: Bearer <token>
  Request:  { name?, privilege? }
  Response: { account_number, ... }

PUT /api/v1/accounts/{account_number}/activate
  Headers:  Authorization: Bearer <token>
  Response: { account_number, is_active: true }

PUT /api/v1/accounts/{account_number}/inactivate
  Headers:  Authorization: Bearer <token>
  Response: { account_number, is_active: false }
```

#### Transactions Service (Port 8002)

```
POST /api/v1/deposits
  Headers:  Authorization: Bearer <token>
  Request:  { account_number, amount }
  Response: { transaction_id, amount, status, created_at }

POST /api/v1/withdrawals
  Headers:  Authorization: Bearer <token>
  Request:  { account_number, amount, pin }
  Response: { transaction_id, amount, status, created_at }

POST /api/v1/transfers
  Headers:  Authorization: Bearer <token>
  Request:  { from_account, to_account, transfer_amount, transfer_mode }
  Response: { transaction_id, transfer_amount, status, created_at }

GET /api/v1/transfer-limits/{account_number}
  Headers:  Authorization: Bearer <token>
  Response: { daily_limit, remaining_limit, transaction_count, remaining_count }

GET /api/v1/transaction-logs/{account_number}
  Headers:  Authorization: Bearer <token>
  Response: [ { transaction_id, amount, type, created_at } ]
```

### 🔐 Token Handling

#### JWT Structure
```json
{
  "sub": "1001",
  "login_id": "john.doe",
  "role": "CUSTOMER",
  "iat": 1737110000,
  "exp": 1737111800,
  "jti": "unique-token-id"
}
```

**Token Lifespan:** 30 minutes

#### Token Storage
- **Location:** localStorage
- **Key:** `gdb_auth_token`
- **Backup:** AuthContext (in-memory)

#### Token Injection
```
Every API request must include:
Authorization: Bearer <token>
```

#### Token Expiry Handling
```
On 401 Response:
  1. Clear token from localStorage
  2. Clear AuthContext
  3. Redirect to /login
  4. Show "Session expired" message
```

---

## 5. Authentication & Authorization

### 🔐 Authentication Flow

```
┌─────────────┐
│  Login Page │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│ User enters credentials      │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ POST /api/v1/auth/login      │
│ (Auth Service: 8004)         │
└──────┬───────────────────────┘
       │
       ├─ SUCCESS ──┬─ FAILURE ──┐
       │            │             │
       ▼            ▼             ▼
   ┌────────┐  ┌────────┐    ┌─────────┐
   │ Token  │  │ Error  │    │ Retry   │
   │ Stored │  │ Show   │    │ Message │
   └───┬────┘  └────────┘    └─────────┘
       │
       ▼
   ┌─────────────────────────┐
   │ Redirect to Dashboard   │
   └─────────────────────────┘
```

### 👥 Role-Based Access Control (RBAC)

#### Permission Matrix

| Feature | ADMIN | TELLER | CUSTOMER |
|---------|:-----:|:------:|:--------:|
| **User Management** | | | |
| Create Users | ✅ | ❌ | ❌ |
| View All Users | ✅ | ✅ | ❌ |
| Edit Users | ✅ | ❌ | ❌ |
| Activate/Inactivate Users | ✅ | ❌ | ❌ |
| **Account Management** | | | |
| Create Accounts | ✅ | ✅ | ❌ |
| View All Accounts | ✅ | ✅ | ❌ |
| View Own Accounts | ✅ | ✅ | ✅ |
| Edit Account Details | ✅ | ❌ | ✅ (own) |
| Activate/Inactivate Accounts | ✅ | ❌ | ❌ |
| **Transactions** | | | |
| Deposit | ✅ | ✅ | ✅ (own) |
| Withdraw | ✅ | ✅ | ✅ (own) |
| Transfer | ✅ | ✅ | ✅ (own) |
| View All Transactions | ✅ | ✅ | ❌ |
| View Own Transactions | ✅ | ✅ | ✅ |
| **Dashboard** | | | |
| Admin Dashboard | ✅ | ❌ | ❌ |
| Teller Dashboard | ✅ | ✅ | ❌ |
| Customer Dashboard | ✅ | ✅ | ✅ |

#### Implementation Rules

1. **UI Enforcement (First Line)**
   - Hide menu items based on role
   - Disable form fields based on role
   - Redirect to 403 if unauthorized

2. **Route Guards (Second Line)**
   - ProtectedRoute component wraps routes
   - RoleGuard verifies role before rendering

3. **Backend Validation (Final Authority)**
   - Backend enforces all permissions
   - UI enforcement is UX only

### 🚪 Authorization Scenarios

#### Scenario 1: ADMIN Views Dashboard
```
✅ Access granted
✅ All tabs visible (Users, Accounts, Transactions)
✅ Create buttons visible
```

#### Scenario 2: TELLER Views Users
```
✅ Access granted
✅ Can view users list
❌ Cannot create users
❌ Cannot edit users
```

#### Scenario 3: CUSTOMER Views Transactions
```
✅ Access granted (for own account)
❌ Cannot see other customers' data
```

#### Scenario 4: CUSTOMER Accesses /admin
```
❌ Access denied → Redirect to 403 page
```

---

## 6. Folder Structure

### 📁 Strict Directory Layout

```
gdb-frontend/
├── src/
│   ├── api/
│   │   ├── auth.ts              (Auth API calls)
│   │   ├── users.ts             (Users API calls)
│   │   ├── accounts.ts          (Accounts API calls)
│   │   ├── transactions.ts      (Transactions API calls)
│   │   └── client.ts            (Axios setup + interceptors)
│   │
│   ├── auth/
│   │   ├── AuthContext.tsx      (Auth state management)
│   │   ├── AuthProvider.tsx     (Auth context wrapper)
│   │   └── useAuth.ts           (Auth hook)
│   │
│   ├── pages/
│   │   ├── Login.tsx            (Login page)
│   │   ├── Unauthorized.tsx     (403 page)
│   │   ├── NotFound.tsx         (404 page)
│   │   │
│   │   ├── dashboard/
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── TellerDashboard.tsx
│   │   │   └── CustomerDashboard.tsx
│   │   │
│   │   ├── users/
│   │   │   ├── UsersList.tsx
│   │   │   ├── CreateUser.tsx
│   │   │   └── UserDetail.tsx
│   │   │
│   │   ├── accounts/
│   │   │   ├── AccountsList.tsx
│   │   │   ├── CreateAccount.tsx
│   │   │   └── AccountDetail.tsx
│   │   │
│   │   └── transactions/
│   │       ├── TransactionsList.tsx
│   │       ├── Deposit.tsx
│   │       ├── Withdraw.tsx
│   │       └── Transfer.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Navbar.tsx
│   │   │   └── MainLayout.tsx
│   │   │
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Form.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── Loading.tsx
│   │   │
│   │   └── guards/
│   │       ├── ProtectedRoute.tsx
│   │       └── RoleGuard.tsx
│   │
│   ├── hooks/
│   │   ├── useAuth.ts           (Already in /auth but can reference)
│   │   ├── useFetch.ts          (Data fetching)
│   │   └── useLoading.ts        (Loading states)
│   │
│   ├── routes/
│   │   └── routes.tsx           (Route definitions)
│   │
│   ├── utils/
│   │   ├── constants.ts         (API URLs, error messages)
│   │   ├── helpers.ts           (Utility functions)
│   │   ├── validators.ts        (Form validation)
│   │   └── formatters.ts        (Date, currency formatting)
│   │
│   ├── types/
│   │   ├── api.ts              (API request/response types)
│   │   ├── auth.ts             (Auth types)
│   │   ├── user.ts             (User types)
│   │   ├── account.ts          (Account types)
│   │   └── transaction.ts      (Transaction types)
│   │
│   ├── styles/
│   │   ├── globals.css         (Global styles)
│   │   └── tailwind.config.js  (Tailwind config with color palette)
│   │
│   ├── App.tsx                 (Main app wrapper)
│   └── main.tsx                (Entry point)
│
├── public/
│   └── favicon.ico
│
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

### 🔧 Critical Files Explained

#### `src/api/client.ts` — Axios Setup

```typescript
// Central Axios instance with interceptors
// Automatically injects JWT token
// Handles 401 responses
// Logs API calls (dev only)
```

#### `src/auth/AuthContext.tsx` — Auth State

```typescript
// Stores: token, user, isAuthenticated, role
// Methods: login, logout, setToken
// Persists to localStorage
```

#### `src/routes/routes.tsx` — Route Definitions

```typescript
// Define all routes here
// Apply ProtectedRoute wrapper
// Apply RoleGuard wrapper
// NOT in App.tsx
```

#### `src/utils/constants.ts` — Configuration

```typescript
// API URLs for all services
// Error messages (standardized)
// Role permissions
// Color palette
```

---

## 7. Phase-by-Phase Implementation

### ✅ PHASE 1: PROJECT SETUP

**Goal:** Bootstrap project with all tools configured

**Tasks:**
1. [ ] Create Vite + React + TypeScript project
   ```bash
   npm create vite@latest gdb-frontend -- --template react-ts
   cd gdb-frontend
   npm install
   ```

2. [ ] Install dependencies
   ```bash
   npm install axios react-router-dom
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

3. [ ] Configure Tailwind with color palette
   ```javascript
   // tailwind.config.js
   export default {
     theme: {
       colors: {
         blue: { primary: '#1E3A8A', dark: '#0F172A', action: '#2563EB' },
         green: { success: '#16A34A' },
         red: { error: '#DC2626' },
         // ... rest of palette
       },
     },
   }
   ```

4. [ ] Setup global styles
   ```css
   /* src/styles/globals.css */
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   
   @layer base {
     body { @apply bg-gray-50 text-gray-900; }
     h1 { @apply text-2xl font-bold; }
   }
   ```

5. [ ] Create folder structure (see Section 6)

6. [ ] Create basic App.tsx with React Router v6 setup
   ```typescript
   function App() {
     return <BrowserRouter><Routes>...</Routes></BrowserRouter>;
   }
   export default App;
   ```

**Completion Criteria:**
- ✅ Project runs without errors (`npm run dev`)
- ✅ Tailwind compiles successfully
- ✅ Folder structure matches spec
- ✅ React Router works (test with dummy route)

---

### ✅ PHASE 2: AUTH FOUNDATION

**Goal:** Implement JWT authentication + login

**Tasks:**

1. [ ] Create `src/types/auth.ts`
   ```typescript
   export interface AuthToken {
     access_token: string;
     token_type: string;
     expires_in: number;
     user_id: number;
     login_id: string;
     role: 'ADMIN' | 'TELLER' | 'CUSTOMER';
   }
   
   export interface AuthUser {
     user_id: number;
     login_id: string;
     role: 'ADMIN' | 'TELLER' | 'CUSTOMER';
   }
   ```

2. [ ] Create `src/api/client.ts` — Axios with interceptors
   ```typescript
   import axios from 'axios';
   
   const client = axios.create({
     baseURL: 'http://localhost',
   });
   
   // Request interceptor: inject token
   client.interceptors.request.use((config) => {
     const token = localStorage.getItem('gdb_auth_token');
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   
   // Response interceptor: handle 401
   client.interceptors.response.use(
     (response) => response,
     (error) => {
       if (error.response?.status === 401) {
         localStorage.removeItem('gdb_auth_token');
         window.location.href = '/login';
       }
       return Promise.reject(error);
     }
   );
   
   export default client;
   ```

3. [ ] Create `src/api/auth.ts` — Auth API functions
   ```typescript
   import client from './client';
   
   export const authAPI = {
     login: (login_id: string, password: string) =>
       client.post('/api/v1/auth/login', { login_id, password }, {
         baseURL: 'http://localhost:8004',
       }),
     
     verifyToken: (token: string) =>
       client.post('/api/v1/auth/verify-token', { token }, {
         baseURL: 'http://localhost:8004',
       }),
   };
   ```

4. [ ] Create `src/auth/AuthContext.tsx`
   ```typescript
   import { createContext, useState, useCallback } from 'react';
   import { AuthUser, AuthToken } from '../types/auth';
   
   export interface AuthContextType {
     token: string | null;
     user: AuthUser | null;
     isAuthenticated: boolean;
     login: (token: string, user: AuthUser) => void;
     logout: () => void;
   }
   
   export const AuthContext = createContext<AuthContextType | null>(null);
   ```

5. [ ] Create `src/auth/AuthProvider.tsx`
   ```typescript
   import { AuthContext, AuthContextType } from './AuthContext';
   
   export function AuthProvider({ children }: { children: React.ReactNode }) {
     const [token, setToken] = useState<string | null>(
       localStorage.getItem('gdb_auth_token')
     );
     const [user, setUser] = useState<AuthUser | null>(() => {
       const stored = localStorage.getItem('gdb_auth_user');
       return stored ? JSON.parse(stored) : null;
     });
   
     const login = useCallback((token: string, user: AuthUser) => {
       localStorage.setItem('gdb_auth_token', token);
       localStorage.setItem('gdb_auth_user', JSON.stringify(user));
       setToken(token);
       setUser(user);
     }, []);
   
     const logout = useCallback(() => {
       localStorage.removeItem('gdb_auth_token');
       localStorage.removeItem('gdb_auth_user');
       setToken(null);
       setUser(null);
     }, []);
   
     return (
       <AuthContext.Provider value={{ token, user, isAuthenticated: !!token, login, logout }}>
         {children}
       </AuthContext.Provider>
     );
   }
   ```

6. [ ] Create `src/auth/useAuth.ts` hook
   ```typescript
   import { useContext } from 'react';
   import { AuthContext } from './AuthContext';
   
   export function useAuth() {
     const context = useContext(AuthContext);
     if (!context) throw new Error('useAuth must be used inside AuthProvider');
     return context;
   }
   ```

7. [ ] Create `src/pages/Login.tsx`
   ```typescript
   import { useState } from 'react';
   import { useNavigate } from 'react-router-dom';
   import { useAuth } from '../auth/useAuth';
   import { authAPI } from '../api/auth';
   
   export function Login() {
     const [loginId, setLoginId] = useState('');
     const [password, setPassword] = useState('');
     const [loading, setLoading] = useState(false);
     const [error, setError] = useState('');
     const { login } = useAuth();
     const navigate = useNavigate();
   
     const handleLogin = async (e: React.FormEvent) => {
       e.preventDefault();
       setLoading(true);
       setError('');
   
       try {
         const response = await authAPI.login(loginId, password);
         const { access_token, user_id, login_id, role } = response.data;
         login(access_token, { user_id, login_id, role });
         navigate('/dashboard');
       } catch (err: any) {
         setError(err.response?.data?.message || 'Login failed');
       } finally {
         setLoading(false);
       }
     };
   
     return (
       <div className="min-h-screen flex items-center justify-center bg-gray-50">
         <div className="bg-white p-8 rounded border border-gray-200">
           <h1 className="text-2xl font-bold mb-6">GDB Login</h1>
           {error && <div className="bg-red-50 text-red-600 p-3 mb-4">{error}</div>}
           <form onSubmit={handleLogin}>
             <div className="mb-4">
               <label className="block font-medium mb-2">Login ID</label>
               <input
                 type="text"
                 value={loginId}
                 onChange={(e) => setLoginId(e.target.value)}
                 className="w-full border border-gray-300 px-3 py-2 rounded"
               />
             </div>
             <div className="mb-6">
               <label className="block font-medium mb-2">Password</label>
               <input
                 type="password"
                 value={password}
                 onChange={(e) => setPassword(e.target.value)}
                 className="w-full border border-gray-300 px-3 py-2 rounded"
               />
             </div>
             <button
               type="submit"
               disabled={loading}
               className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700"
             >
               {loading ? 'Logging in...' : 'Login'}
             </button>
           </form>
         </div>
       </div>
     );
   }
   ```

8. [ ] Update `src/App.tsx` with AuthProvider
   ```typescript
   import { BrowserRouter, Routes, Route } from 'react-router-dom';
   import { AuthProvider } from './auth/AuthProvider';
   import { Login } from './pages/Login';
   
   function App() {
     return (
       <AuthProvider>
         <BrowserRouter>
           <Routes>
             <Route path="/login" element={<Login />} />
             {/* More routes later */}
           </Routes>
         </BrowserRouter>
       </AuthProvider>
     );
   }
   
   export default App;
   ```

**Completion Criteria:**
- ✅ Login page renders without errors
- ✅ Can submit login credentials
- ✅ Token stored in localStorage
- ✅ AuthContext works correctly
- ✅ Can logout (clears token)

---

### ✅ PHASE 3: ROUTE GUARDS

**Goal:** Protect routes, enforce RBAC

**Tasks:**

1. [ ] Create `src/components/guards/ProtectedRoute.tsx`
   ```typescript
   import { Navigate } from 'react-router-dom';
   import { useAuth } from '../../auth/useAuth';
   
   export function ProtectedRoute({ children }: { children: React.ReactNode }) {
     const { isAuthenticated } = useAuth();
     return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
   }
   ```

2. [ ] Create `src/components/guards/RoleGuard.tsx`
   ```typescript
   import { Navigate } from 'react-router-dom';
   import { useAuth } from '../../auth/useAuth';
   
   export function RoleGuard({
     children,
     roles,
   }: {
     children: React.ReactNode;
     roles: string[];
   }) {
     const { user } = useAuth();
     return user && roles.includes(user.role) ? (
       <>{children}</>
     ) : (
       <Navigate to="/unauthorized" />
     );
   }
   ```

3. [ ] Create `src/pages/Unauthorized.tsx`
   ```typescript
   export function Unauthorized() {
     return (
       <div className="min-h-screen flex items-center justify-center">
         <div className="text-center">
           <h1 className="text-4xl font-bold text-red-600 mb-4">403</h1>
           <p className="text-xl text-gray-600">Unauthorized Access</p>
           <p className="text-gray-500 mt-2">You don't have permission to view this page.</p>
           <a href="/dashboard" className="mt-6 inline-block bg-blue-600 text-white px-4 py-2 rounded">
             Back to Dashboard
           </a>
         </div>
       </div>
     );
   }
   ```

4. [ ] Create `src/pages/NotFound.tsx`
   ```typescript
   export function NotFound() {
     return (
       <div className="min-h-screen flex items-center justify-center">
         <div className="text-center">
           <h1 className="text-4xl font-bold text-gray-600 mb-4">404</h1>
           <p className="text-xl text-gray-600">Page Not Found</p>
           <a href="/dashboard" className="mt-6 inline-block bg-blue-600 text-white px-4 py-2 rounded">
             Back to Home
           </a>
         </div>
       </div>
     );
   }
   ```

5. [ ] Create `src/routes/routes.tsx`
   ```typescript
   import { Navigate } from 'react-router-dom';
   import { ProtectedRoute } from '../components/guards/ProtectedRoute';
   import { RoleGuard } from '../components/guards/RoleGuard';
   import { Login } from '../pages/Login';
   import { Unauthorized } from '../pages/Unauthorized';
   import { NotFound } from '../pages/NotFound';
   
   export const routeConfig = [
     { path: '/login', element: <Login /> },
     { path: '/unauthorized', element: <Unauthorized /> },
     {
       path: '/dashboard',
       element: (
         <ProtectedRoute>
           {/* Dashboard will go here */}
         </ProtectedRoute>
       ),
     },
     { path: '*', element: <NotFound /> },
   ];
   ```

6. [ ] Update `src/App.tsx` with routes
   ```typescript
   function App() {
     return (
       <AuthProvider>
         <BrowserRouter>
           <Routes>
             {routeConfig.map((route) => (
               <Route key={route.path} path={route.path} element={route.element} />
             ))}
           </Routes>
         </BrowserRouter>
       </AuthProvider>
     );
   }
   ```

**Completion Criteria:**
- ✅ Non-authenticated users redirected to /login
- ✅ Unauthorized role redirected to /unauthorized
- ✅ 404 page works for unknown routes
- ✅ Route guards tested manually

---

### ✅ PHASE 4: API LAYER

**Goal:** Centralize all API calls

**Tasks:**

1. [ ] Create `src/types/api.ts`
   ```typescript
   export interface User {
     user_id: number;
     username: string;
     login_id: string;
     role: 'ADMIN' | 'TELLER' | 'CUSTOMER';
     is_active: boolean;
     created_at: string;
   }
   
   export interface Account {
     account_number: number;
     account_type: 'SAVINGS' | 'CURRENT';
     name: string;
     balance: number;
     privilege: 'PREMIUM' | 'GOLD' | 'SILVER';
     is_active: boolean;
   }
   
   export interface Transaction {
     transaction_id: number;
     amount: number;
     transaction_type: 'DEPOSIT' | 'WITHDRAW' | 'TRANSFER';
     created_at: string;
   }
   ```

2. [ ] Create `src/api/users.ts`
   ```typescript
   import client from './client';
   import { User } from '../types/api';
   
   export const usersAPI = {
     getUsers: () => client.get('/api/v1/users', { baseURL: 'http://localhost:8003' }),
     getUser: (userId: number) => client.get(`/api/v1/users/${userId}`, { baseURL: 'http://localhost:8003' }),
     createUser: (data: any) => client.post('/api/v1/users', data, { baseURL: 'http://localhost:8003' }),
     updateUser: (userId: number, data: any) => client.patch(`/api/v1/users/${userId}`, data, { baseURL: 'http://localhost:8003' }),
     activateUser: (userId: number) => client.put(`/api/v1/users/${userId}/activate`, {}, { baseURL: 'http://localhost:8003' }),
     inactivateUser: (userId: number) => client.put(`/api/v1/users/${userId}/inactivate`, {}, { baseURL: 'http://localhost:8003' }),
   };
   ```

3. [ ] Create `src/api/accounts.ts`
   ```typescript
   import client from './client';
   
   export const accountsAPI = {
     getAccounts: () => client.get('/api/v1/accounts', { baseURL: 'http://localhost:8001' }),
     getAccount: (accountNumber: number) => client.get(`/api/v1/accounts/${accountNumber}`, { baseURL: 'http://localhost:8001' }),
     createSavingsAccount: (data: any) => client.post('/api/v1/accounts/savings', data, { baseURL: 'http://localhost:8001' }),
     createCurrentAccount: (data: any) => client.post('/api/v1/accounts/current', data, { baseURL: 'http://localhost:8001' }),
     updateAccount: (accountNumber: number, data: any) => client.patch(`/api/v1/accounts/${accountNumber}`, data, { baseURL: 'http://localhost:8001' }),
     activateAccount: (accountNumber: number) => client.put(`/api/v1/accounts/${accountNumber}/activate`, {}, { baseURL: 'http://localhost:8001' }),
     inactivateAccount: (accountNumber: number) => client.put(`/api/v1/accounts/${accountNumber}/inactivate`, {}, { baseURL: 'http://localhost:8001' }),
   };
   ```

4. [ ] Create `src/api/transactions.ts`
   ```typescript
   import client from './client';
   
   export const transactionsAPI = {
     deposit: (data: any) => client.post('/api/v1/deposits', data, { baseURL: 'http://localhost:8002' }),
     withdraw: (data: any) => client.post('/api/v1/withdrawals', data, { baseURL: 'http://localhost:8002' }),
     transfer: (data: any) => client.post('/api/v1/transfers', data, { baseURL: 'http://localhost:8002' }),
     getTransferLimits: (accountNumber: number) => client.get(`/api/v1/transfer-limits/${accountNumber}`, { baseURL: 'http://localhost:8002' }),
     getTransactionLogs: (accountNumber: number) => client.get(`/api/v1/transaction-logs/${accountNumber}`, { baseURL: 'http://localhost:8002' }),
   };
   ```

5. [ ] Create `src/utils/constants.ts`
   ```typescript
   export const API_URLS = {
     AUTH: 'http://localhost:8004',
     USERS: 'http://localhost:8003',
     ACCOUNTS: 'http://localhost:8001',
     TRANSACTIONS: 'http://localhost:8002',
   };
   
   export const ROLES = {
     ADMIN: 'ADMIN',
     TELLER: 'TELLER',
     CUSTOMER: 'CUSTOMER',
   };
   
   export const PRIVILEGES = {
     PREMIUM: 'PREMIUM',
     GOLD: 'GOLD',
     SILVER: 'SILVER',
   };
   ```

**Completion Criteria:**
- ✅ All API functions exported
- ✅ No API calls in UI components yet (just setup)
- ✅ Axios client works with interceptors
- ✅ Constants defined and accessible

---

### ✅ PHASE 5: LAYOUT COMPONENTS

**Goal:** Build reusable layout (Sidebar, Navbar, MainLayout)

**Tasks:**

1. [ ] Create `src/components/layout/Sidebar.tsx`
   ```typescript
   import { useAuth } from '../../auth/useAuth';
   import { useState } from 'react';
   
   export function Sidebar() {
     const { user, logout } = useAuth();
     const [collapsed, setCollapsed] = useState(false);
   
     const menuItems = {
       ADMIN: ['Dashboard', 'Users', 'Accounts', 'Transactions'],
       TELLER: ['Dashboard', 'Users', 'Accounts', 'Transactions'],
       CUSTOMER: ['Dashboard', 'Accounts', 'Transactions'],
     };
   
     return (
       <aside className={`${collapsed ? 'w-20' : 'w-64'} bg-slate-900 text-white h-screen p-4 flex flex-col transition-all`}>
         <div className="flex justify-between items-center mb-8">
           <span className={collapsed ? '' : 'text-2xl font-bold'}>GDB</span>
           <button onClick={() => setCollapsed(!collapsed)} className="text-xl">☰</button>
         </div>
   
         <nav className="flex-1">
           {(menuItems[user?.role as keyof typeof menuItems] || []).map((item) => (
             <a key={item} href={`/${item.toLowerCase()}`} className="block py-2 px-4 hover:bg-blue-600 rounded mb-2">
               {!collapsed && item}
             </a>
           ))}
         </nav>
   
         <button onClick={logout} className="w-full bg-red-600 py-2 rounded hover:bg-red-700">
           {collapsed ? '🚪' : 'Logout'}
         </button>
       </aside>
     );
   }
   ```

2. [ ] Create `src/components/layout/Navbar.tsx`
   ```typescript
   import { useAuth } from '../../auth/useAuth';
   
   export function Navbar() {
     const { user } = useAuth();
   
     return (
       <nav className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
         <h1 className="text-2xl font-bold">GDB Banking</h1>
         <div className="flex items-center gap-4">
           <span className="text-gray-600">{user?.login_id}</span>
           <span className={`px-3 py-1 rounded text-white text-sm font-medium ${
             user?.role === 'ADMIN' ? 'bg-red-600' :
             user?.role === 'TELLER' ? 'bg-blue-600' :
             'bg-green-600'
           }`}>
             {user?.role}
           </span>
         </div>
       </nav>
     );
   }
   ```

3. [ ] Create `src/components/layout/MainLayout.tsx`
   ```typescript
   import { Sidebar } from './Sidebar';
   import { Navbar } from './Navbar';
   
   export function MainLayout({ children }: { children: React.ReactNode }) {
     return (
       <div className="flex h-screen">
         <Sidebar />
         <div className="flex-1 flex flex-col">
           <Navbar />
           <main className="flex-1 overflow-auto bg-gray-50 p-6">
             {children}
           </main>
         </div>
       </div>
     );
   }
   ```

4. [ ] Create common components (`src/components/common/`)
   - `Button.tsx` — Styled button component
   - `Card.tsx` — Card wrapper
   - `Table.tsx` — Reusable table
   - `Form.tsx` — Form wrapper
   - `Badge.tsx` — Status badges
   - `Loading.tsx` — Loading skeleton

**Completion Criteria:**
- ✅ Sidebar renders with menu items based on role
- ✅ Navbar shows user info
- ✅ Layout responsive (basic)
- ✅ Logout works

---

### ✅ PHASE 6-8: FEATURE MODULES

**Goal:** Build Users, Accounts, Transactions modules

These are dashboard-specific implementations. Follow the same pattern:
1. Create page component
2. Call API in useEffect
3. Render table/form
4. Handle loading + errors
5. Apply role guards

*Detailed templates provided in next sections*

---

### ✅ PHASE 9: POLISH & HARDEN

**Goal:** Final quality pass

**Tasks:**

1. [ ] Add loading states to all API calls
2. [ ] Add error boundary component
3. [ ] Add toast notifications (optional: react-toastify)
4. [ ] Handle empty states (no data)
5. [ ] Test token expiry (manually set exp to past time)
6. [ ] Test all RBAC rules
7. [ ] Verify all API endpoints work
8. [ ] Check responsive design on mobile
9. [ ] Add console.log cleanup
10. [ ] Build for production (`npm run build`)

---

## 8. Coding Standards

### ✅ DO's

```typescript
// ✅ GOOD: API calls in separate files
const response = await usersAPI.getUsers();

// ✅ GOOD: Types everywhere
const user: User = data;

// ✅ GOOD: Error handling
try { ... } catch (err: unknown) { ... }

// ✅ GOOD: Reusable components
<Button variant="primary">Click me</Button>

// ✅ GOOD: Constants for magic strings
const { ADMIN, TELLER, CUSTOMER } = ROLES;

// ✅ GOOD: useAuth hook for auth
const { user, logout } = useAuth();
```

### ❌ DON'Ts

```typescript
// ❌ BAD: API calls in components
function MyComponent() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch('/api/users')  // Direct fetch
      .then(res => res.json())
      .then(setData);
  }, []);
}

// ❌ BAD: No types
const user = data;  // What is data?

// ❌ BAD: Silent errors
try { ... } catch (err) { }  // No error handling

// ❌ BAD: Magic strings
if (user.role === 'ADMIN') { }  // Should use ROLES.ADMIN

// ❌ BAD: Direct Redux (use Context)
import { useSelector } from 'react-redux';

// ❌ BAD: Auth logic in component
const [token, setToken] = useState(localStorage.getItem('token'));
```

### 📋 Code Quality Checklist

- [ ] All files have clear purpose (name + docstring)
- [ ] No unused imports
- [ ] All TypeScript errors resolved
- [ ] Components under 200 lines
- [ ] Functions have type signatures
- [ ] Error messages are user-friendly
- [ ] API calls use constants (not hardcoded URLs)
- [ ] All routes are protected appropriately

---

## 9. Quality Checklist

### 🎨 UI/UX Quality

- [ ] Color palette matches spec
- [ ] All buttons styled consistently
- [ ] Forms have proper labels + validation
- [ ] Tables are sortable/paginated
- [ ] Loading states visible
- [ ] Error messages clear
- [ ] Empty states handled
- [ ] Mobile responsive (basic)

### 🔐 Security

- [ ] JWT stored in localStorage
- [ ] Token in all API requests
- [ ] 401 responses redirect to login
- [ ] Logout clears token
- [ ] RBAC enforced in UI
- [ ] No auth logic duplication
- [ ] No hardcoded credentials

### 🧪 Functionality

- [ ] Login works (test with all roles)
- [ ] Dashboard renders based on role
- [ ] Users module CRUD works
- [ ] Accounts module CRUD works
- [ ] Transactions CRUD works
- [ ] All API calls succeed
- [ ] Error handling works
- [ ] No console errors

### 📦 Code Quality

- [ ] No hardcoded URLs (use constants)
- [ ] No API calls in components (use hooks/context)
- [ ] All TypeScript strict mode compliant
- [ ] Components < 200 LOC
- [ ] Reusable components identified
- [ ] No console.log in production code
- [ ] All imports are used

### ✅ Deployment Ready

- [ ] Production build succeeds (`npm run build`)
- [ ] No build warnings
- [ ] Bundle size reasonable
- [ ] Environment variables configured
- [ ] Docker image ready (optional)

---

## 🚀 Next Steps

Once all phases complete, you can request:

1. **🧪 Frontend Test Checklist** — Jest/Vitest tests
2. **🔐 Security Audit** — OWASP compliance check
3. **📦 Production Build** — Optimization + env setup
4. **🧠 Interview Explanation** — How to explain architecture

---

## 📞 Quick Reference

### Starting Dev Server
```bash
npm install
npm run dev
# Open http://localhost:5173
```

### Login Credentials (From Backend)
```
ADMIN:    admin.user / Welcome@1
TELLER:   john.doe / Welcome@1
CUSTOMER: jane.smith / Welcome@1
```

### Backend Services Status
```bash
# All must be running on these ports:
Auth Service:         http://localhost:8004
Users Service:        http://localhost:8003
Accounts Service:     http://localhost:8001
Transactions Service: http://localhost:8002
```

### Common Issues

| Issue | Solution |
|-------|----------|
| CORS errors | Ensure all backend services are running |
| 404 on login | Check Auth Service port (8004) |
| Token not persisting | Check localStorage in DevTools |
| API calls failing | Verify token in Authorization header |
| Components not updating | Check useAuth hook usage |

---

## ✨ Final Notes

This specification is **production-grade** and suitable for:
- ✅ Training environments
- ✅ Interview demos
- ✅ Internal banking simulations
- ✅ Enterprise deployments

**Key Principles:**
1. **Theme first** — Colors, typography, layout locked
2. **No backend changes** — API is final
3. **Clean code** — Types, separation of concerns, reusability
4. **Production ready** — Error handling, loading states, security

---

**Document Version:** 1.0  
**Created:** December 25, 2025  
**Status:** ✅ READY FOR DEVELOPMENT  
