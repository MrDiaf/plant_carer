export type PlantState = "seedling" | "growing" | "thirsty" | "dead" | "bloomed";

export type Plant = {
  id: number;
  state: PlantState;
  created_at: string;
  last_watered_at: string | null;
  bloom_at: string;
  bloom_color: string | null;
  days_alive: number;
  can_water: boolean;
  message: string;
  thirsty_at: string;
  dies_at: string;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function requestPlant(path: string, options?: RequestInit): Promise<Plant> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json"
    },
    ...options
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : detail?.message ?? "The plant could not be updated.";
    throw new Error(message);
  }

  return data as Plant;
}

export function getPlant(): Promise<Plant> {
  return requestPlant("/api/plant");
}

export function waterPlant(): Promise<Plant> {
  return requestPlant("/api/plant/water", { method: "POST" });
}

export function replacePlant(): Promise<Plant> {
  return requestPlant("/api/plant/replace", { method: "POST" });
}
