export class GithubClient {
  private accessToken: string;
  private baseUrl: string = "https://api.github.com";
  private owner: string = "openclaw-kong"; // Default owner
  private repo: string = "openclaw-workspace"; // Default repo

  constructor() {
    this.accessToken = process.env.GITHUB_TOKEN || "";
    // Note: In a real scenario, owner/repo might come from config
  }

  async fetchDirectory(path: string) {
    const url = `${this.baseUrl}/repos/${this.owner}/${this.repo}/contents/${path}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.accessToken}`,
        Accept: "application/vnd.github.v3+json",
      },
      next: { revalidate: 3600 } // ISR 1 hour
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    return response.json();
  }

  async fetchContent(path: string) {
    const url = `${this.baseUrl}/repos/${this.owner}/${this.repo}/contents/${path}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.accessToken}`,
        Accept: "application/vnd.github.v3.raw",
      },
      next: { revalidate: 3600 }
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.statusText}`);
    }

    return response.text();
  }
}
