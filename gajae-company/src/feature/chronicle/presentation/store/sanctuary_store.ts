import { create } from "zustand";
import { Chronicle } from "../../domain/model/chronicle";

interface SanctuaryState {
  dates: string[];
  selectedDate: string | null;
  timeline: Chronicle[];
  isLoading: boolean;
  setDates: (dates: string[]) => void;
  setSelectedDate: (date: string) => void;
  setTimeline: (timeline: Chronicle[]) => void;
  setIsLoading: (isLoading: boolean) => void;
}

export const useSanctuaryStore = create<SanctuaryState>((set) => ({
  dates: [],
  selectedDate: null,
  timeline: [],
  isLoading: false,
  setDates: (dates) => set({ dates }),
  setSelectedDate: (selectedDate) => set({ selectedDate }),
  setTimeline: (timeline) => set({ timeline }),
  setIsLoading: (isLoading) => set({ isLoading }),
}));
