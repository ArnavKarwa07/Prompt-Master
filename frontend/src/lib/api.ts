/**
 * API Client for Prompt Master Backend
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface OptimizeRequest {
  prompt: string;
  goal: string;
  force_agent?: "coding" | "creative" | "analyst" | "general" | null;
  project_id?: string | null;
}

export interface RoutingInfo {
  confidence: number;
  reasoning: string;
}

export interface OptimizeResponse {
  original_prompt: string;
  goal: string;
  agent: string;
  routing: RoutingInfo;
  score: number;
  feedback: string;
  optimized_prompt: string;
  error?: string | null;
}

export interface Agent {
  name: string;
  description: string;
}

export interface AgentsResponse {
  agents: Agent[];
}

export interface Project {
  id: string;
  name: string;
  created_at?: string;
}

export interface ProjectsResponse {
  projects: Project[];
}

export interface PromptHistoryItem {
  id: string;
  prompt_text: string;
  agent_used: string;
  score: number;
  optimized_prompt?: string;
  created_at?: string;
  project_name?: string; // Name of project if associated
}

export interface PromptHistoryResponse {
  history: PromptHistoryItem[];
}

class ApiClient {
  private token: string | null = null;
  private tokenRefreshCallback: (() => Promise<string | null>) | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  setTokenRefreshCallback(callback: () => Promise<string | null>) {
    this.tokenRefreshCallback = callback;
  }

  private async refreshToken(): Promise<string | null> {
    if (this.tokenRefreshCallback) {
      const newToken = await this.tokenRefreshCallback();
      this.token = newToken;
      return newToken;
    }
    return this.token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryOnAuth: boolean = true
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`[API] ${options.method || "GET"} ${endpoint}`, {
      hasToken: !!this.token,
    });

    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    console.log(`[API] Response ${endpoint}: ${response.status}`);

    // Handle token expiration - refresh and retry once
    if (response.status === 401 && retryOnAuth && this.tokenRefreshCallback) {
      console.log(`[API] 401 received, refreshing token...`);
      const newToken = await this.refreshToken();
      if (newToken) {
        console.log(`[API] Token refreshed, retrying request`);
        // Retry the request with new token
        return this.request<T>(endpoint, options, false);
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      console.error(`[API] Error ${endpoint}:`, error);
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    const data = await response.json();
    console.log(`[API] Success ${endpoint}:`, data);
    return data;
  }

  // ============ Prompt Endpoints ============

  async optimizePrompt(request: OptimizeRequest): Promise<OptimizeResponse> {
    return this.request<OptimizeResponse>("/prompts/optimize", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async listAgents(): Promise<AgentsResponse> {
    return this.request<AgentsResponse>("/prompts/agents");
  }

  async analyzePrompt(request: OptimizeRequest): Promise<{
    prompt: string;
    goal: string;
    recommended_agent: string;
    confidence: number;
    reasoning: string;
  }> {
    return this.request("/prompts/analyze-only", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  // ============ Project Endpoints ============

  async createProject(name: string): Promise<Project> {
    return this.request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  }

  async listProjects(): Promise<ProjectsResponse> {
    return this.request<ProjectsResponse>("/projects");
  }

  async getProject(projectId: string): Promise<Project> {
    return this.request<Project>(`/projects/${projectId}`);
  }

  async deleteProject(projectId: string): Promise<void> {
    await this.request(`/projects/${projectId}`, {
      method: "DELETE",
    });
  }

  async getPromptHistory(
    projectId: string,
    limit: number = 20
  ): Promise<PromptHistoryResponse> {
    return this.request<PromptHistoryResponse>(
      `/projects/${projectId}/history?limit=${limit}`
    );
  }

  async getHistory(
    limit: number = 10,
    projectId?: string | null
  ): Promise<PromptHistoryResponse> {
    let url = `/history?limit=${limit}`;
    if (projectId) {
      url += `&project_id=${projectId}`;
    }
    return this.request<PromptHistoryResponse>(url);
  }

  /** @deprecated Use getHistory() instead */
  async getGlobalPromptHistory(
    limit: number = 10
  ): Promise<PromptHistoryResponse> {
    return this.getHistory(limit);
  }

  async uploadContextFile(
    projectId: string,
    file: File
  ): Promise<{ message: string; storage_path: string; filename: string }> {
    const formData = new FormData();
    formData.append("file", file);

    const url = `${API_BASE_URL}/projects/${projectId}/upload`;
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: this.token ? `Bearer ${this.token}` : "",
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Upload failed: ${response.status}`);
    }

    return response.json();
  }

  // ============ Health Check ============

  async healthCheck(): Promise<{
    status: string;
    version: string;
    agents_available: string[];
  }> {
    const url = `${API_BASE_URL.replace("/api/v1", "")}/health`;
    const response = await fetch(url);
    return response.json();
  }
}

// Singleton instance
export const api = new ApiClient();
