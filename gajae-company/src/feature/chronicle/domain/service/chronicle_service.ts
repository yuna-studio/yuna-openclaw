import { GithubRepositoryImpl } from "../../data/repository/github_repository_impl";
import { Chronicle } from "../model/chronicle";

export class ChronicleService {
  private repository: GithubRepositoryImpl;

  constructor() {
    this.repository = new GithubRepositoryImpl();
  }

  async getTimelineIndex() {
    return this.repository.getDailyIndex();
  }

  async getDailyTimeline(date: string): Promise<Chronicle[]> {
    return this.repository.getChroniclesByDate(date);
  }
}
