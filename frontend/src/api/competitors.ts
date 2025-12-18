import { apiFetch } from "./http";

export type Competitor = {
  id: string;
  project_id: string;
  name: string;
  tiktok_url: string;
  notes: string | null;
  followers: number | null;
  avg_views: number | null;
  avg_likes: number | null;
  engagement_rate: number | null;
  created_at: string;
  updated_at: string;
};

export type CreateCompetitorPayload = {
  project_id: string;
  name: string;
  tiktok_url: string;
  notes?: string;
};

export type UpdateCompetitorPayload = {
  name?: string;
  tiktok_url?: string;
  notes?: string;
};

export async function createCompetitor(payload: CreateCompetitorPayload): Promise<Competitor> {
  return apiFetch<Competitor>("/competitors", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listCompetitors(projectId: string): Promise<Competitor[]> {
  return apiFetch<Competitor[]>(`/competitors?project_id=${projectId}`);
}

export async function getCompetitor(competitorId: string): Promise<Competitor> {
  return apiFetch<Competitor>(`/competitors/${competitorId}`);
}

export async function updateCompetitor(
  competitorId: string,
  payload: UpdateCompetitorPayload
): Promise<Competitor> {
  return apiFetch<Competitor>(`/competitors/${competitorId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteCompetitor(competitorId: string): Promise<{ status: string; id: string }> {
  return apiFetch<{ status: string; id: string }>(`/competitors/${competitorId}`, {
    method: "DELETE",
  });
}
