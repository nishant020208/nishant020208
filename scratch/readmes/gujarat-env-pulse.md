# 🌿 EnviroSense Pro: Hyperlocal Pollution Evidence Engine (Gujarat)

[![Vite](https://img.shields.io/badge/Vite-7.x-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vite.dev/)
[![React](https://img.shields.io/badge/React-19.x-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Database%20%26%20Auth-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#)

Gujarat has **192+ industrial sensor nodes** spread across villages and industrial corridors (Vapi, Ankleshwar, Vatva, etc.). However, district-level monitoring stations often miss hyperlocal spikes. Citizen complaints take days to process, and accountability is near zero.

**EnviroSense Pro** is a real-time air quality intelligence platform built specifically for Gujarat's industrial zones and villages. It connects to live sensor data via the WAQI API and gives citizens, researchers, and authorities a single command center to monitor spikes, map wind patterns, and generate legally-formatted GSPCB Form-A complaint PDFs in under 60 seconds—backed by real, tamper-evident sensor evidence.

---

## 🔬 Core Capabilities & Features

### 1. Unified Command Center
A cockpit dashboard displaying state-wide or village-specific telemetry, active surge warnings, and key metrics.
* **Hyperlocal AQI Tracking**: Continuous live monitoring of PM2.5, PM10, NO₂, SO₂, O₃, and CO.
* **Dynamic Indicators**: Auto-updates telemetry dynamically with color-coded AQI severity classes.

### 2. Live GIS AQI Map
An interactive map utilizing Leaflet to visualize:
* Hyperlocal villages and active sensor nodes.
* Wind vectors (speed & direction) and animated pollution plumes.
* Industrial zone overlays to map the spatial relationship between residential areas and factories.

### 3. AI Source Inference Engine
Pinpoints which industrial cluster is likely causing a pollution spike.
* Integrates real-time wind speed/bearing, industrial shift schedules, and historical surge patterns.
* Computes confidence scores and generates a transparent, step-by-step reasoning chain (e.g., *"Spike of 240 ug/m³ occurs while wind blows from 220° (Ankleshwar GIDC Sector-III). Shift schedules indicate active chemical production."*).

### 4. Legally-Formatted GSPCB Form-A Generator
* Instantly compiles a citizen pollution complaint PDF matching the official GSPCB layout.
* Auto-fills:
  1. Complainant details (Village, Sarpanch, affected population).
  2. Location and geo-coordinates.
  3. Hyperlocal sensor readings (PM2.5, SO₂, Wind).
  4. AI source-inference outputs and confidence levels.
  5. Legal warning pointing to **Section 31A of the Air (Prevention and Control of Pollution) Act, 1981**.
  6. Unique QR code tracking ID and a tamper-evident SHA-256 evidence hash.

### 5. Multi-Role Permission Matrix
EnviroSense Pro is designed with **10 distinct user roles**, each with a tailored workspace environment:

| Role | Code | Organization | Description / Access Level |
|---|---|---|---|
| **Super Admin** | `super_admin` | HPEE Platform Ops | Unrestricted access to all modules, roles, and logs. |
| **GSPCB Admin** | `gspcb_admin` | GSPCB HQ | HQ operator dashboard; approves user accounts, views audit trails. |
| **GSPCB Inspector** | `inspector` | Regional Office | Handles case files, manages evidence timelines, uploads site inspection photos. |
| **Village Sarpanch** | `sarpanch` | Gram Panchayat | Files complaints, broadcasts WhatsApp/SMS warnings to village residents. |
| **Public Citizen** | `public` | Community | Views public AQI map, active alerts, and health warnings. |
| **Sensor Maintenance**| `maintenance`| HPEE Engineering | Repairs queue, sensor calibration status, battery levels. |
| **Industry Officer** | `industry` | GIDC Association | Submits compliance reports, shift schedules, ESG documentation. |
| **Emergency Responder**| `emergency` | District Ops | Triggers siren broadcasts, safety notices, and evacuation orders. |
| **Environmental Analyst**| `analyst` | Intelligence Cell | Performs predictive modelling, seasonal trend analysis. |
| **District Officer** | `district` | District Administration| Views district-wide comparisons and AQI heatmaps. |

---

## ⚙️ Technical Stack

* **Frontend**: [React 19](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Vite](https://vite.dev/), [TanStack Router](https://tanstack.com/router) (file-based routing), [TanStack Query](https://tanstack.com/query) (data fetching & caching).
* **Styling & Motion**: [Tailwind CSS v4](https://tailwindcss.com/), [Framer Motion](https://www.framer.com/motion/) (animations), [Lucide React](https://lucide.dev/) (icons).
* **Charts & GIS**: [Recharts](https://recharts.org/) (visual trends), [Leaflet](https://leafletjs.com/) & [React Leaflet](https://react-leaflet.js.org/) (maps).
* **Database & Auth**: [Supabase](https://supabase.com/) (PostgreSQL with RLS policy enforcement, custom enums for roles, profiles/roles mapping).
* **PDF Utility**: [jsPDF](https://github.com/parallax/jsPDF).
* **Package Manager**: [Bun](https://bun.sh/) (using `bun.lock` for rapid, deterministic package resolution).

---

## 🗄️ Database Architecture

EnviroSense Pro uses a cloud-backed Supabase database for authentication, profile mapping, and admin approvals.

### Core Schemas:
1. **`public.profiles`**: Contains user info, linked to `auth.users` via UUID.
   * Fields: `id` (UUID, Primary Key), `full_name`, `email`, `approval_status` (Enum: `pending`, `approved`, `rejected`), `created_at`, `updated_at`.
2. **`public.user_roles`**: Contains the role mapping for profiles.
   * Fields: `id` (UUID), `user_id` (References `auth.users`), `role` (Enum: `super_admin`, `gspcb_admin`, etc.).

### Security Policies (RLS):
* Users can view and update their own profiles.
* Only admins (`super_admin` / `gspcb_admin`) can view and update other users' profiles/roles.
* Trigger `on_auth_user_created` runs `public.handle_new_user()` upon email registration. The user starts with a `pending` status and a default `public` role.

---

## 🚀 Getting Started

Follow these steps to run EnviroSense Pro locally:

### 1. Prerequisites
Ensure you have [Bun](https://bun.sh/) or [Node.js](https://nodejs.org/) installed. We recommend using Bun for faster builds and deterministic dependency resolution.

### 2. Clone the Repository
```bash
git clone https://github.com/[YOUR_USERNAME]/gujarat-env-pulse.git
cd gujarat-env-pulse
```

### 3. Install Dependencies
```bash
bun install
# or: npm install
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and specify the following variables:
```env
VITE_SUPABASE_URL="https://your-supabase-url.supabase.co"
VITE_SUPABASE_PUBLISHABLE_KEY="your-supabase-anon-key"
VITE_WAQI_API_KEY="your-waqi-api-token"
```

### 5. Running the Application
* **Development Server**:
  ```bash
  bun dev
  ```
  Open `http://localhost:5173` in your browser.
* **Production Build**:
  ```bash
  bun build
  ```
* **Linting & Formatting**:
  ```bash
  bun lint
  bun format
  ```

---

## 🧪 Testing User Roles (Demo Logins)

The application has a built-in fallback credentials layer to make manual testing of the multi-role matrix straightforward. You can log in using these demo credentials:

| Email | Password | Role | Organization |
|---|---|---|---|
| `admin@hppe.gov.in` | `Hppe@2026` | Super Admin | HPEE Platform Ops |
| `gspcb@hppe.gov.in` | `Gspcb@2026` | GSPCB Admin | Gujarat Pollution Control Board |
| `inspector@hppe.gov.in` | `Field@2026` | GSPCB Inspector | GSPCB Vapi Regional Office |
| `sarpanch@hppe.gov.in` | `Gram@2026` | Village Sarpanch | Sarigam Gram Panchayat |
| `analyst@hppe.gov.in` | `Data@2026` | Environmental Analyst | HPEE Intelligence Cell |
| `emergency@hppe.gov.in` | `Ero@2026` | Emergency Responder | District Emergency Ops |
| `district@hppe.gov.in` | `Dmo@2026` | District Officer | Bharuch District Monitoring |
| `industry@hppe.gov.in` | `Comply@2026` | Industry Officer | Ankleshwar Industries Assoc. |
| `maintenance@hppe.gov.in`| `Mesh@2026` | Maintenance Engineer | HPEE Field Engineering |
| `public@hppe.gov.in` | `Public@2026` | Public Citizen | Community |

---

## 🚧 Roadmap & Current MVP Status

This is an early MVP. The core dashboard, live WAQI pipeline, Leaflet map, and demo auth are fully operational. The remaining items on the roadmap are:
- [x] Hyperlocal sensor telemetry and wind vector streaming
- [x] Multi-role permission system and custom workspaces
- [x] PDF Complaint compiler (GSPCB Form-A)
- [ ] Production-grade database migrations approval workflow
- [ ] Integration of actual SMS/WhatsApp gate alerts (currently simulated)
- [ ] Advanced LSTM/ML models for seasonal forecasting (currently heuristic-based source-inference)
- [ ] Mobile application wrappers (Capacitor/PWA)

---

## 🤝 Contributing & Civic Tech

We love civic technology and environmental monitoring! If you are interested in making industrial emissions transparent, or helping villages defend their right to clean air, please contribute.
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

*Built for real-world environmental action in Gujarat.* 🌿
