import { GithubClient } from "../data_source/github_client";
import { Chronicle } from "../../domain/model/chronicle";

export class GithubRepositoryImpl {
  private client: GithubClient;
  private filenameRegex = /^(\d{8})_(\d{4})_(.*)\.md$/;

  constructor() {
    this.client = new GithubClient();
  }

  async getDailyIndex(): Promise<string[]> {
    const data = await this.client.fetchDirectory("docs/chronicle/daily");
    if (!Array.isArray(data)) return [];

    return data
      .filter((item: any) => item.type === "dir")
      .map((item: any) => item.name)
      .sort((a, b) => b.localeCompare(a)); // Latest first
  }

  async getChroniclesByDate(date: string): Promise<Chronicle[]> {
    try {
      // Try 'meeting' folder first as per spec
      const path = `docs/chronicle/daily/${date}/meeting`;
      const data = await this.client.fetchDirectory(path);
      
      if (!Array.isArray(data)) return [];

      return data
        .filter((item: any) => item.type === "file" && item.name.endsWith(".md"))
        .map((item: any) => this.toEntity(item))
        .filter((c): c is Chronicle => c !== null)
        .sort((a, b) => a.time.localeCompare(b.time));
    } catch (error) {
      console.error(`Failed to fetch chronicles for ${date}:`, error);
      return [];
    }
  }

  private toEntity(dto: any): Chronicle | null {
    const match = dto.name.match(this.filenameRegex);
    if (!match) return null;

    const [_, date, time, titleSlug] = match;
    const formattedTime = `${time.slice(0, 2)}:${time.slice(2, 4)}`;

    return {
      id: dto.sha,
      date,
      time: formattedTime,
      title: titleSlug.replace(/-/g, " "), // Basic slug to title conversion
      path: dto.path,
    };
  }
}
