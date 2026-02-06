import { ChronicleService } from "@/feature/chronicle/domain/service/chronicle_service";
import { TimelineView } from "@/feature/chronicle/presentation/view/timeline_view";

export default async function TimelinePage() {
  const service = new ChronicleService();
  const dates = await service.getTimelineIndex();

  return (
    <div className="container mx-auto px-6 py-12">
      <TimelineView initialDates={dates} />
    </div>
  );
}
