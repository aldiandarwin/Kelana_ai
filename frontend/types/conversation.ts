export type ConversationSummary = {
  id: number;
  title: string;
  created_at: string;
};

export type ConversationMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export type ConversationDetail = ConversationSummary & {
  messages: ConversationMessage[];
};

export type ConversationTurn = {
  conversation_id: number;
  title: string;
  user_message: ConversationMessage;
  assistant_message: ConversationMessage;
};

export type ConversationCreateResponse = {
  conversation_id: number;
};
