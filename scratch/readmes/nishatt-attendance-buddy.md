# Attendance Buddy

A lightweight, modern attendance tracking app designed for students. Stay on top of your schedule, monitor your attendance percentages, and never miss a goal.

## Features

- **Timetable Management**: Organize your weekly schedule effortlessly.
- **Quick Attendance**: Mark presence or absence for today's classes with one click.
- **Smart Insights**: Automatically calculate how many classes you can afford to miss while staying above your target (e.g., 75%).
- **Interactive Stats**: View subject-wise breakdowns and overall performance.
- **Cross-Platform**: Built with Capacitor for a seamless experience on Web, Android, and iOS.
- **Data Sync**: Powered by Supabase for real-time updates and secure authentication.

## Tech Stack

- **UI/UX**: React, Tailwind CSS, shadcn/ui, Framer Motion
- **Core**: TypeScript, Vite
- **Backend**: Supabase (Database & Auth)
- **Mobile**: Capacitor
- **Charts**: Recharts

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd attendance-buddy
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Environment Variables**:
   Create a `.env` file and add your Supabase credentials:
   ```env
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. **Launch**:
   ```bash
   npm run dev
   ```
