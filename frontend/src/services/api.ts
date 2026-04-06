import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for auth
api.interceptors.request.use((config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor for token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
                    refresh: refreshToken,
                });

                const { access } = response.data;
                localStorage.setItem('access_token', access);

                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
            } catch (refreshError) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    login: (email: string, password: string) =>
        api.post('/auth/login/', { email, password }),

    register: (data: { email: string; password: string; username: string }) =>
        api.post('/auth/register/', data),

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    getProfile: () => api.get('/auth/profile/'),
};

// Student API
export const studentAPI = {
    getProfile: () => api.get('/students/profile/'),
    updateProfile: (data: any) => api.patch('/students/profile/', data),
    getProgress: () => api.get('/students/progress/'),
    getAnalytics: () => api.get('/students/analytics/'),
    getWeaknesses: () => api.get('/students/weaknesses/'),
};

// Digital Twin API
export const digitalTwinAPI = {
    getState: () => api.get('/digital-twin/state/'),
    getPredictions: () => api.get('/digital-twin/predictions/'),
    getCognitiveEvents: (limit = 50) => api.get(`/digital-twin/events/?limit=${limit}`),
    syncState: () => api.post('/digital-twin/sync/'),
};

// Courses API
export const coursesAPI = {
    list: (params?: { category?: string; difficulty?: string }) =>
        api.get('/courses/', { params }),

    get: (id: string) => api.get(`/courses/${id}/`),

    getModules: (courseId: string) => api.get(`/courses/${courseId}/modules/`),

    enroll: (courseId: string) => api.post(`/courses/${courseId}/enroll/`),

    getEnrollments: () => api.get('/courses/enrollments/'),
};

// Content API
export const contentAPI = {
    getTopicContent: (topicId: string) => api.get(`/content/topic/${topicId}/`),

    getNextContent: () => api.get('/content/next/'),

    markComplete: (contentId: string) => api.post(`/content/${contentId}/complete/`),

    uploadDocument: (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/content/upload/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    processImage: (file: File) => {
        const formData = new FormData();
        formData.append('image', file);
        return api.post('/process/image/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    processVideo: (file: File) => {
        const formData = new FormData();
        formData.append('video', file);
        return api.post('/process/video/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
};

// Learning API
export const learningAPI = {
    explainConcept: (concept: string, difficulty?: number) =>
        api.post('/learn/explain/', { concept, difficulty }),

    validateAnswer: (questionId: string, answer: string) =>
        api.post('/learn/validate/', { question_id: questionId, answer }),

    startSession: (courseId?: string) =>
        api.post('/learn/session/start/', { course_id: courseId }),

    endSession: (sessionId: string, metrics?: any) =>
        api.post('/learn/session/end/', { session_id: sessionId, metrics }),
};

// Assessment API
export const assessmentAPI = {
    generateQuiz: (topicId: string, numQuestions = 10) =>
        api.post('/quiz/generate/', { topic_id: topicId, num_questions: numQuestions }),

    getQuiz: (quizId: string) => api.get(`/quiz/${quizId}/`),

    submitQuiz: (quizId: string, answers: Record<string, any>) =>
        api.post('/quiz/submit/', { quiz_id: quizId, answers }),

    getResults: (attemptId: string) => api.get(`/quiz/results/${attemptId}/`),
};

// Reports API
export const reportsAPI = {
    generate: (type: string, params?: any) =>
        api.post('/reports/generate/', { type, ...params }),

    download: (reportId: string, format: 'pdf' | 'docx' = 'pdf') =>
        api.get(`/reports/download/${reportId}/?format=${format}`, {
            responseType: 'blob',
        }),

    list: () => api.get('/reports/'),
};

// Analytics API
export const analyticsAPI = {
    getDashboard: () => api.get('/analytics/dashboard/'),
    getLearningMetrics: (dateRange?: { start: string; end: string }) =>
        api.get('/analytics/metrics/', { params: dateRange }),
    getTopicBreakdown: () => api.get('/analytics/topics/'),
};

export default api;
