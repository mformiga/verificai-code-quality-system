export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    PROFILE: '/auth/profile',
  },
  PROMPTS: {
    BASE: '/prompts',
    BY_TYPE: '/prompts',
  },
  FILES: {
    UPLOAD: '/files/upload',
    CONFIG: '/files/config',
  },
  ANALYSIS: {
    BASE: '/analysis',
    RESULTS: '/analysis',
    SUMMARY: '/analysis',
    EXPORT: '/analysis',
  },
  SESSIONS: {
    BASE: '/sessions',
    CURRENT: '/sessions/current',
  },
  USERS: {
    BASE: '/users',
    PROFILE: '/users/profile',
  },
} as const;

export const FILE_TYPES = {
  JAVASCRIPT: 'application/javascript',
  TYPESCRIPT: 'text/typescript',
  PYTHON: 'text/x-python',
  JAVA: 'text/x-java-source',
  C: 'text/x-csrc',
  CPP: 'text/x-c++src',
} as const;

export const ANALYSIS_TYPES = {
  GENERAL: 'general',
  ARCHITECTURAL: 'architectural',
  BUSINESS: 'business',
} as const;

export const STATUS_COLORS = {
  pending: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-yellow-100 text-yellow-800',
  pass: 'bg-green-100 text-green-800',
  fail: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
} as const;

export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const MAX_FILES_COUNT = 100;

export const LOCAL_STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
} as const;