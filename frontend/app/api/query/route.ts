import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();
    
    if (!query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }

    // Make request to your FastAPI backend
    // Use environment variable for backend URL, fallback to localhost for local development
    const backendBaseUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const backendUrl = `${backendBaseUrl}/query?q=${encodeURIComponent(query)}`;
    const response = await fetch(backendUrl);
    
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error querying backend:', error);
    return NextResponse.json(
      { error: 'Failed to query backend' }, 
      { status: 500 }
    );
  }
}