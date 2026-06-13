# ScholarBridge Frontend MVP

Premium, modern, student-facing frontend for ScholarBridge, built with Next.js, Tailwind CSS, and TypeScript.

## Stack Overview
- **Framework**: Next.js (App Router)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Forms**: React Hook Form
- **Language**: TypeScript

## Getting Started

### 1. Prerequisites
Ensure you have Node.js (v18+) and npm installed.

### 2. Configure Environment
Copy the example environment file:
```bash
cp .env.local.example .env.local
```
Ensure `NEXT_PUBLIC_API_BASE_URL` points to your running FastAPI backend (defaults to `http://127.0.0.1:8000`).

### 3. Install Dependencies
```bash
npm install
```

### 4. Run Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

### 5. Production Checks (Build & Lint)
```bash
npm run lint
```
```bash
npm run build
```
