// Content Types
export interface ContentCategory {
  id: number
  name: string
  slug: string
  description: string
  icon: string
  is_active: boolean
  articles_count: number
  created_at: string
  updated_at: string
}

export interface UserArticle {
  id: number
  title: string
  slug: string
  content?: string
  excerpt: string
  author: {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
    full_name: string
  }
  category: ContentCategory
  status: 'draft' | 'pending' | 'published' | 'rejected' | 'archived'
  featured_image: string
  tags: string
  tags_list: string[]
  read_time: number
  views: number
  likes: number
  dislikes: number
  vote_score: number
  is_featured: boolean
  comments_count: number
  published_at: string | null
  created_at: string
  updated_at: string
}

export interface ArticleComment {
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
  replies: ArticleComment[]
  created_at: string
  updated_at: string
}

export interface ArticleVote {
  id: number
  vote_type: 'like' | 'dislike'
  created_at: string
}

// Content Stats
export interface ContentStats {
  total_articles: number
  published_articles: number
  pending_articles: number
  total_categories: number
  total_comments: number
  total_votes: number
  articles_by_category: Array<{
    category__name: string
    count: number
  }>
  popular_articles: Array<{
    id: number
    title: string
    views: number
    likes: number
    author__username: string
  }>
  recent_activity: number
  engagement_rate: number
  average_read_time: number
}

// API Response Types
export interface ContentApiResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ContentFormData {
  title: string
  content: string
  excerpt: string
  category: number
  status: string
  featured_image: string
  tags: string
  read_time: number
  is_featured: boolean
}
