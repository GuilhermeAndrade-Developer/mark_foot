// Polls Types
export interface Poll {
  id: number
  title: string
  slug: string
  description: string
  question: string
  author: {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
    full_name: string
  }
  status: 'draft' | 'active' | 'closed' | 'archived'
  featured_image: string
  is_multiple_choice: boolean
  is_anonymous: boolean
  is_featured: boolean
  total_votes: number
  views: number
  participation_rate: number
  options_count: number
  comments_count: number
  time_remaining: number | null
  start_date: string | null
  end_date: string | null
  created_at: string
  updated_at: string
  options?: PollOption[]
  comments?: PollComment[]
}

export interface PollOption {
  id: number
  text: string
  description: string
  image: string
  votes: number
  percentage: number
  order: number
  is_active: boolean
  created_at: string
}

export interface PollVote {
  id: number
  option: number
  user?: {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
    full_name: string
  }
  created_at: string
}

export interface PollComment {
  id: number
  content: string
  author: {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
    full_name: string
  }
  parent: number | null
  is_approved: boolean
  likes: number
  replies: PollComment[]
  created_at: string
  updated_at: string
}

// Polls Stats
export interface PollsStats {
  total_polls: number
  active_polls: number
  closed_polls: number
  total_votes: number
  total_comments: number
  popular_polls: Array<{
    id: number
    title: string
    total_votes: number
    views: number
    author__username: string
  }>
  recent_polls: number
  recent_votes: number
  participation_rate: number
  average_votes_per_poll: number
}

// API Response Types
export interface PollsApiResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface PollFormData {
  title: string
  description: string
  question: string
  status: string
  featured_image: string
  is_multiple_choice: boolean
  is_anonymous: boolean
  is_featured: boolean
  start_date: string | null
  end_date: string | null
  options: Array<{
    text: string
    description: string
    image: string
    order: number
    is_active: boolean
  }>
}

export interface PollResults {
  poll_id: number
  title: string
  total_votes: number
  results: Array<{
    id: number
    text: string
    votes: number
    percentage: number
  }>
}
