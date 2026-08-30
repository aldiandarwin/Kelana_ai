export type Trip = {
  id: number;
  user_id: number;
  destination: string;
  days: number;
  budget: number;
  daily_budget: number;
  category: string;
  created_at: string;
  travel_style: string | null;
  ai_recommendation: string | null;
};

export type TripRequest = {
  destination: string;
  days: number;
  budget: number;
  travel_style: string;
};

export type GeneratedTrip = {
  trip_id: number;
  destination: string;
  recommendation: string;
};

export type TripUpdate = {
  budget: number;
};
