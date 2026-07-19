# Travel Management Application

A full-stack **Travel Management System** built with **Next.js**, **Supabase**, **NextAuth.js**, and **Docker**. The application enables users to securely plan trips, create itineraries, and manage travel activities through an intuitive and responsive interface.

---

##  Features

-  Secure Google OAuth Authentication using NextAuth.js
-  Create and manage travel trips
-  Build detailed itineraries
-  Add and organize trip activities
-  Supabase backend for database and authentication
-  Responsive and modern UI
-  Docker support for containerized deployment

---

##  Tech Stack

### Frontend
- Next.js
- React.js
- Tailwind CSS

### Backend
- Supabase
- NextAuth.js

### Authentication
- Google OAuth

### Deployment
- Docker

---

##  Project Structure

```text
Travel-Management-App/
├── app/
├── components/
├── lib/
├── public/
├── styles/
├── supabase/
├── Dockerfile
├── package.json
├── next.config.js
└── README.md
```

---

##  Getting Started

### Prerequisites

Make sure you have installed:

- Node.js (v18 or later)
- npm or yarn
- Docker (optional)
- Supabase Account

---

##  Installation

Clone the repository:

```bash
git clone https://github.com/your-username/travel-management-app.git
```

Navigate to the project directory:

```bash
cd travel-management-app
```

Install dependencies:

```bash
npm install
```

---

##  Environment Variables

Create a `.env.local` file in the project root.

```env
NEXTAUTH_URL=http://localhost:3000

NEXTAUTH_SECRET=your_nextauth_secret

GOOGLE_CLIENT_ID=your_google_client_id

GOOGLE_CLIENT_SECRET=your_google_client_secret

NEXT_PUBLIC_SUPABASE_URL=your_supabase_url

NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

##  Run Locally

Start the development server:

```bash
npm run dev
```

Open:

```
http://localhost:3000
```

---

##  Run with Docker

Build the Docker image:

```bash
docker build -t travel-management-app .
```

Run the container:

```bash
docker run -p 3000:3000 travel-management-app
```

---

##  Demo

Add your screenshots here.

```
docs/
├── home.png
├── dashboard.png
├── create-trip.png
└── itinerary.png
```

---

##  Future Enhancements

- Flight and hotel booking integration
- Expense tracking
- AI-powered itinerary recommendations
- Weather forecast integration
- Collaborative trip planning
- Email notifications

---

##  Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a new branch.

```bash
git checkout -b feature-name
```

3. Commit your changes.

```bash
git commit -m "Add new feature"
```

4. Push the branch.

```bash
git push origin feature-name
```

5. Open a Pull Request.

---

##  License

This project is licensed under the MIT License.

---

