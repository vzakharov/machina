import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Parse the webhook payload
    const data = await request.json();
    
    // Log the webhook event
    console.log('Webhook received:', JSON.stringify(data, null, 2));
    
    // Extract info from the webhook
    const { table, schema, operation, new_record } = data;
    
    console.log(`Operation '${operation}' on ${schema}.${table}`);
    
    // Return a successful response
    return NextResponse.json({
      status: 'success',
      message: `Webhook for ${operation} on ${schema}.${table} processed`
    });
  } catch (error) {
    console.error('Error processing webhook:', error);
    
    return NextResponse.json(
      { status: 'error', message: 'Error processing webhook' },
      { status: 500 }
    );
  }
} 