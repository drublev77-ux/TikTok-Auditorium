import { create } from "zustand";
import type { AudienceAvatar } from "../api/audience";

type AvatarState = {
  selectedAvatar: AudienceAvatar | null;
  setSelectedAvatar: (avatar: AudienceAvatar | null) => void;
};

export const useAvatarStore = create<AvatarState>((set) => ({
  selectedAvatar: null,
  setSelectedAvatar: (avatar) => set({ selectedAvatar: avatar }),
}));
