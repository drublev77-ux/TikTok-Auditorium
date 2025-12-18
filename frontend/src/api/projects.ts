import { apiFetch } from "./http";
import type { Project } from "../store/projectStore";

export type Org = {
  id: string;
  name: string;
  created_at: string;
};

export async function listOrgs(): Promise<Org[]> {
  return apiFetch<Org[]>("/orgs");
}

export async function createOrg(name: string): Promise<Org> {
  return apiFetch<Org>("/orgs", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function listProjects(orgId?: string): Promise<Project[]> {
  const q = orgId ? `?org_id=${encodeURIComponent(orgId)}` : "";
  return apiFetch<Project[]>(`/projects${q}`);
}

export async function createProject(input: {
  org_id: string;
  name: string;
  timezone: string;
  language: "ru" | "en";
}): Promise<Project> {
  return apiFetch<Project>("/projects", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function getProject(id: string): Promise<Project> {
  return apiFetch<Project>(`/projects/${id}`);
}
