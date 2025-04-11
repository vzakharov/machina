import { NextResponse } from 'next/server';

export async function GET() {
  console.log('===== TEST WEBHOOK ENDPOINT ACCESSED =====');
  return NextResponse.json({
    status: 'success',
    message: 'Test webhook endpoint is working'
  });
} 