// This is a minimal Edge Function to demonstrate functionality
// You can expand this with your actual business logic

import { serve } from "https://deno.land/std@0.131.0/http/server.ts"

console.log("Hello from Functions!")

serve(async (req) => {
  const { name } = await req.json()
  const data = {
    message: `Hello ${name || 'World'}!`,
  }

  return new Response(
    JSON.stringify(data),
    { headers: { "Content-Type": "application/json" } },
  )
}) 