export class GithubClient {
  private accessToken: string;
  private baseUrl: string = "https://api.github.com";
  private owner: string = "yuna-studio";
  private repo: string = "yuna-openclaw";

  constructor() {
    this.accessToken = process.env.GITHUB_TOKEN || "";
  }

  async fetchDirectory(path: string) {
    if (!this.accessToken) {
      return this.getMockDirectory(path);
    }

    const url = `${this.baseUrl}/repos/${this.owner}/${this.repo}/contents/${path}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.accessToken}`,
        Accept: "application/vnd.github.v3+json",
      },
      next: { revalidate: 60 }
    });

    if (!response.ok) {
      return this.getMockDirectory(path);
    }

    return response.json();
  }

  async fetchContent(path: string) {
    if (!this.accessToken) return "# Mock Content\nThis is a demo content.";

    const url = `${this.baseUrl}/repos/${this.owner}/${this.repo}/contents/${path}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.accessToken}`,
        Accept: "application/vnd.github.v3.raw",
      },
      next: { revalidate: 60 }
    });

    if (!response.ok) return "# Mock Content\nFailed to fetch real content.";

    return response.text();
  }

  private getMockDirectory(path: string) {
    // Return dates for the daily index
    if (path === "docs/chronicle/daily") {
      return [
        { name: "2026-02-06", type: "dir" },
        { name: "2026-02-05", type: "dir" },
      ];
    }
    
    // Return meeting logs for 2026-02-06
    if (path === "docs/chronicle/daily/2026-02-06/meeting") {
      return [
        { name: "2026-02-06-0930-1st-sync-meeting.md", type: "file", sha: "m1", path: "p1" },
        { name: "2026-02-06-1505-dev-plan-review-session.md", type: "file", sha: "m2", path: "p2" },
        { name: "2026-02-06-1713-sync.md", type: "file", sha: "m3", path: "p3" },
      ];
    }

    // Return command logs for 2026-02-06
    if (path === "docs/chronicle/daily/2026-02-06/command") {
      return [
        { name: "2026-02-06-1617-ceo-command-lunch-break.md", type: "file", sha: "c1", path: "p4" },
        { name: "2026-02-06-1722-ceo-command-deployment-success.md", type: "file", sha: "c2", path: "p5" },
      ];
    }

    return [];
  }
}
