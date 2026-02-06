import { GithubClient } from "../data_source/github_client";
import { Chronicle } from "../../domain/model/chronicle";

export class GithubRepositoryImpl {
  private client: GithubClient;

  constructor() {
    this.client = new GithubClient();
  }

  async getDailyIndex(): Promise<string[]> {
    const data = await this.client.fetchDirectory("docs/chronicle/daily");
    if (!Array.isArray(data)) return [];

    // Filter valid date directories and sort latest first
    return data
      .filter((item: any) => item.type === "dir" && /^\d{4}-\d{2}-\d{2}$/.test(item.name))
      .map((item: any) => item.name)
      .sort((a, b) => b.localeCompare(a));
  }

  async getChroniclesByDate(date: string): Promise<Chronicle[]> {
    try {
      const meetingPath = `docs/chronicle/daily/${date}/meeting`;
      const meetingData = await this.client.fetchDirectory(meetingPath);
      
      const commandPath = `docs/chronicle/daily/${date}/command`;
      const commandData = await this.client.fetchDirectory(commandPath);
      
      const allItems = [
        ...(Array.isArray(meetingData) ? meetingData : []),
        ...(Array.isArray(commandData) ? commandData : [])
      ];

      // CRITICAL: Remove duplicates by SHA to prevent double rendering
      const uniqueMap = new Map<string, any>();
      allItems.forEach(item => {
        if (item.sha && !uniqueMap.has(item.sha)) {
          uniqueMap.set(item.sha, item);
        }
      });
      
      const uniqueItems = Array.from(uniqueMap.values());

      return uniqueItems
        .filter((item: any) => item.type === "file" && item.name.endsWith(".md"))
        .map((item: any) => this.toEntity(item))
        .filter((c): c is Chronicle => c !== null)
        // Sort by time HH:MM
        .sort((a, b) => a.time.localeCompare(b.time));
    } catch (error) {
      console.error(`Failed to fetch chronicles for ${date}:`, error);
      return [];
    }
  }

  private toEntity(dto: any): Chronicle | null {
    const name = dto.name;
    
    // Strategy 1: YYYY-MM-DD-HHMM-slug.md
    const match1 = name.match(/^(\d{4}-\d{2}-\d{2})-(\d{4})-(.*)\.md$/);
    if (match1) {
      const [_, dateStr, time, title] = match1;
      return {
        id: dto.sha,
        date: dateStr.replace(/-/g, ""),
        time: `${time.slice(0, 2)}:${time.slice(2, 4)}`,
        title: title.replace(/-/g, " "),
        path: dto.path,
      };
    }

    // Strategy 2: YYYYMMDD_HHMM_Title.md
    const match2 = name.match(/^(\d{8})_(\d{4})_(.*)\.md$/);
    if (match2) {
      const [_, date, time, title] = match2;
      return {
        id: dto.sha,
        date,
        time: `${time.slice(0, 2)}:${time.slice(2, 4)}`,
        title: title.replace(/-/g, " "),
        path: dto.path,
      };
    }

    // Fallback: Just use filename without extension
    return {
        id: dto.sha,
        date: "unknown",
        time: "00:00", // Fallback time
        title: name.replace(".md", "").replace(/-/g, " "),
        path: dto.path
    };
  }
}
