import { apiFetch } from "./http";

export type ContentIdea = {
  title: string;
  description: string;
  hook: string;
  hashtags: string[];
  best_posting_time: string;
  estimated_duration: string;
  content_tips: string[];
};

export type GenerateIdeasResponse = {
  topic: string;
  content_type: string;
  ideas: ContentIdea[];
  generated_at: string;
};

export type ContentPlan = {
  id: string;
  project_id: string;
  title: string;
  scheduled_date: string;
  scheduled_time: string;
  content_type: string;
  description: string | null;
  hashtags: string[];
  status: "draft" | "scheduled" | "published" | "archived";
  has_ad_label: boolean;
  created_at: string;
  updated_at: string;
};

export type GenerateIdeasPayload = {
  project_id: string;
  topic: string;
  target_audience?: string;
  hashtags?: string[];
  content_type?: "video" | "trend" | "educational" | "promotional";
  count?: number;
};

export type CreatePlanPayload = {
  project_id: string;
  title: string;
  scheduled_date: string;
  scheduled_time: string;
  content_type?: string;
  description?: string;
  hashtags?: string[];
  status?: string;
  has_ad_label?: boolean;
};

export async function generateContentIdeas(
  payload: GenerateIdeasPayload
): Promise<GenerateIdeasResponse> {
  return apiFetch<GenerateIdeasResponse>("/planner/generate-ideas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function optimizeHashtags(
  hashtags: string[],
  topic?: string
): Promise<{ optimized_hashtags: string[]; removed_hashtags: string[]; hashtag_strategy: string }> {
  return apiFetch("/planner/optimize-hashtags", {
    method: "POST",
    body: JSON.stringify({ hashtags, topic }),
  });
}

export async function createContentPlan(payload: CreatePlanPayload): Promise<ContentPlan> {
  return apiFetch<ContentPlan>("/planner/posts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listContentPlans(
  projectId: string,
  status?: string
): Promise<ContentPlan[]> {
  let url = `/planner/posts?project_id=${projectId}`;
  if (status) url += `&status=${status}`;
  return apiFetch<ContentPlan[]>(url);
}

export async function updateContentPlan(
  postId: string,
  payload: Partial<CreatePlanPayload>
): Promise<ContentPlan> {
  return apiFetch<ContentPlan>(`/planner/posts/${postId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteContentPlan(
  postId: string
): Promise<{ status: string; id: string }> {
  return apiFetch<{ status: string; id: string }>(`/planner/posts/${postId}`, {
    method: "DELETE",
  });
}
