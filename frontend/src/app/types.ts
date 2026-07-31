export interface Job {
  id: number;
  title: string;
  company: string;
  location?: string;
  description?: string;
  salary?: string;
  company_email?: string;
  opportunity_type?: string;
  match_score?: number;
}

export interface Application {
  id: number;
  title: string;
  company: string;
  company_email?: string;
  status: string;
  gmail_message_id?: string;
  applied_at: string;
  opportunity_type: string;
  notes?: string;
}

export interface ProfileData {
  summary: string;
  skills: string[];
  experience: any[];
  education: any[];
  projects: any[];
}

export interface AtsMetrics {
  overall_score: number;
  formatting_score: number;
  keyword_density_score: number;
  action_verbs_score: number;
  section_completeness_score: number;
  summary: string;
  strengths: string[];
  missing_skills: string[];
  formatting_suggestions: string[];
  experience_improvements: string[];
}

export interface UserSettings {
  llm_provider: string;
  llm_model: string;
  custom_api_base: string;
  openai_api_key: string;
  google_client_id: string;
  google_client_secret: string;
  adzuna_app_id: string;
  adzuna_app_key: string;
  jooble_api_key: string;
  target_roles: string[];
  target_countries: string[];
  work_mode_preference: string;
  employment_types: string[];
  salary_preference: string;
  experience_level: string;
  visa_sponsorship: string;
  daily_job_goal: number;
  daily_internship_goal: number;
  auto_fulfill_enabled: boolean;
  email: string;
  portfolio_url: string;
  github_url: string;
  other_url: string;
}
