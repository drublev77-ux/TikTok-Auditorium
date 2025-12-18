import { apiFetch } from "./http";

export type Creator = {
  id: string;
  project_id: string;
  name: string;
  tiktok_url: string;
  category: string;
  notes: string | null;
  followers: number | null;
  avg_views: number | null;
  engagement_rate: number | null;
  audience_match_score: number | null;
  created_at: string;
  updated_at: string;
};

export type CreateCreatorPayload = {
  project_id: string;
  name: string;
  tiktok_url: string;
  category?: string;
  notes?: string;
};

export type UpdateCreatorPayload = {
  name?: string;
  tiktok_url?: string;
  category?: string;
  notes?: string;
};

export async function createCreator(payload: CreateCreatorPayload): Promise<Creator> {
  return apiFetch<Creator>("/creators", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listCreators(projectId: string, category?: string): Promise<Creator[]> {
  let url = `/creators?project_id=${projectId}`;
  if (category) url += `&category=${encodeURIComponent(category)}`;
  return apiFetch<Creator[]>(url);
}

export async function getCreator(creatorId: string): Promise<Creator> {
  return apiFetch<Creator>(`/creators/${creatorId}`);
}

export async function updateCreator(
  creatorId: string,
  payload: UpdateCreatorPayload
): Promise<Creator> {
  return apiFetch<Creator>(`/creators/${creatorId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteCreator(creatorId: string): Promise<{ status: string; id: string }> {
  return apiFetch<{ status: string; id: string }>(`/creators/${creatorId}`, {
    method: "DELETE",
  });
}

export async function listCreatorCategories(projectId: string): Promise<string[]> {
  return apiFetch<string[]>(`/creators/categories/list?project_id=${projectId}`);
}
