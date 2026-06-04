export const APP_NAME = "ПЛАНИФИКАТОР-3000" as const;

export type PlanStatus = "draft" | "active" | "completed";

export interface PlanSummary {
  id: string;
  title: string;
  status: PlanStatus;
  updatedAt: string;
}
