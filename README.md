# Unfindables

A full-stack web application that curates and showcases obscure but useful websites, tools, and digital gems for indie developers.

## Project Structure

- `/nextjs` - Next.js frontend application
- `/django` - Django backend server used for scraping and storing data
- Supabase stack for database, auth, storage, and API

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Node.js (recommended: v18+)
- Python (recommended: v3.10+)

### Running the project

1. Clone the repository:
```
git clone https://github.com/yourusername/unfindables.git
cd unfindables
```

2. Start the Docker containers:
```
docker compose up
```

3. Access the various services:
   - Frontend: http://unfindables.localhost
   - Django Admin: http://django.unfindables.localhost
   - Supabase Studio: http://studio.unfindables.localhost
   - API: http://api.unfindables.localhost

### Environment Variables

The project uses environment variables defined in `.env` file. You can customize them as needed.

## Supabase Services

Our setup uses a simplified version of the Supabase stack with the following components:

- PostgreSQL Database (db) - The core database
- API Gateway (kong) - Handles API requests
- Studio (studio) - Web interface for managing your database
- Meta API (meta) - Used by Studio to interact with PostgreSQL

### Accessing Supabase

- Supabase Studio: http://studio.unfindables.localhost
- Supabase API: http://api.unfindables.localhost

### Default Credentials

The following default credentials are set in the `.env` file:

- Postgres Password: postgres
- Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
- Service Role Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU

Note: These are for development only. Use secure credentials in production.

### Using with Next.js

Supabase can be used in your Next.js application by using the Supabase JavaScript client:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'http://localhost:8000',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
)
```

For more information, see the [Supabase documentation](https://supabase.com/docs).

## Development Guidelines

- Write self-explanatory code without comments
- Keep components modular and reusable
- Maintain type safety
- Update this file and README.md on significant changes
- As the app runs in docker, run commands via docker CLI

## About

Unfindables is a full-stack web application that helps developers discover valuable but lesser-known digital resources. The platform combines a modern Next.js frontend with a robust Django backend to deliver a seamless experience for discovering and sharing internet gems.

## Tech Stack

### Frontend
- [Next.js](https://nextjs.org) - React framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [Tailwind CSS](https://tailwindcss.com) - Styling

### Backend
- [Django](https://www.djangoproject.com/) - Python web framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API development
- SQLite (development) / PostgreSQL (production)

## Contributing

We welcome contributions! If you have suggestions for websites or tools to add, or if you'd like to help improve the platform, please feel free to open an issue or submit a pull request.

## License

This project is open source and available under the MIT License.