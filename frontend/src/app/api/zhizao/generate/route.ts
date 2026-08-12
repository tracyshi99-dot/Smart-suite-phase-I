import { NextRequest, NextResponse } from "next/server";

/**
 * POST /api/zhizao/generate
 * Proxies to Lambda backend which runs the full 3-step pipeline:
 * Claude generate → Claude optimize → Qianwen polish
 */

const LAMBDA_API = "https://asq6n6kw78.execute-api.us-east-1.amazonaws.com";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward to Lambda backend
    const res = await fetch(`${LAMBDA_API}/api/zhizao/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        { success: false, drafts: [], message: data?.detail || `Lambda error: ${res.status}` },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      { success: false, drafts: [], message: String(err) },
      { status: 500 }
    );
  }
}
