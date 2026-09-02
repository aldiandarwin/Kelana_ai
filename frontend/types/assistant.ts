export type AssistantSource = {
  document: string;
  excerpt: string;
  // null on the managed Knowledge Base path, which returns no score
  score: number | null;
};

export type AssistantAnswer = {
  question: string;
  answer: string;
  sources: AssistantSource[];
  // false when nothing was retrieved, so the UI never presents a guess as grounded
  grounded: boolean;
  mode: string;
};

export type AssistantRequest = {
  question: string;
};
