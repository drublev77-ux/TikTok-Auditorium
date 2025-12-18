import { apiFetch } from "./http";

export type AudienceAvatar = {
  id: string;
  project_id: string;
  name: string;
  hashtags: string[];
  geolocation: string;
  language: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type CreateAvatarPayload = {
  project_id: string;
  name: string;
  hashtags: string[];
  geolocation: string;
  language?: string;
  notes?: string;
};

export type UpdateAvatarPayload = {
  name?: string;
  hashtags?: string[];
  geolocation?: string;
  language?: string;
  notes?: string;
};

export async function createAudienceAvatar(payload: CreateAvatarPayload): Promise<AudienceAvatar> {
  return apiFetch<AudienceAvatar>("/audience/avatars", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listAudienceAvatars(projectId: string): Promise<AudienceAvatar[]> {
  return apiFetch<AudienceAvatar[]>(`/audience/avatars?project_id=${projectId}`);
}

export async function getAudienceAvatar(avatarId: string): Promise<AudienceAvatar> {
  return apiFetch<AudienceAvatar>(`/audience/avatars/${avatarId}`);
}

export async function updateAudienceAvatar(
  avatarId: string,
  payload: UpdateAvatarPayload
): Promise<AudienceAvatar> {
  return apiFetch<AudienceAvatar>(`/audience/avatars/${avatarId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteAudienceAvatar(avatarId: string): Promise<{ status: string; id: string }> {
  return apiFetch<{ status: string; id: string }>(`/audience/avatars/${avatarId}`, {
    method: "DELETE",
  });
}
