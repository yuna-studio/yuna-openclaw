import { NextRequest, NextResponse } from "next/server";
import { ChronicleService } from "@/feature/chronicle/domain/service/chronicle_service";

export async function GET(
  request: NextRequest,
  { params }: { params: { date: string } }
) {
  const date = params.date;
  const service = new ChronicleService();
  
  try {
    const chronicles = await service.getDailyTimeline(date);
    return NextResponse.json(chronicles);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch chronicles" }, { status: 500 });
  }
}
