export type User = {
  id: number;
  name: string;
  email: string;
  created_at: string;
  total_trips: number;
};

export type RegisterInput = {
  name: string;
  email: string;
  password: string;
};

export type LoginInput = {
  email: string;
  password: string;
};
