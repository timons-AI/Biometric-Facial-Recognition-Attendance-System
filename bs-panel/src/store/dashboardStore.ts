import { atom } from "jotai";

export const dashboardLoadingAtom = atom<boolean>(false);
export const dashboardErrorAtom = atom<string | null>(null);
