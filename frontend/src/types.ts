export interface AnalysisResponse {
    match_score: number
    recommendation: 'APPLY' | 'MAYBE' | 'SKIP'
    matching_skills: string[]
    missing_skills: string[]
    weak_skills: string[]
    experience_gaps: string[]
    strengths: string[]
    reasoning: string[]
    learning_recommendations: string[]
    profile_summary: string[]
    technologies: string[]
    experience_years: number
    education: string[]
}

export interface AnalysisHistoryItem extends AnalysisResponse {
    id: string
    created_at: string
}
