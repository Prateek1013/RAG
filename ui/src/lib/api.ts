import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

// Assuming API Gateway routes
const API_URL = 'http://localhost:8081';
const DOC_PROCESSOR_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
});

export const docClient = axios.create({
  baseURL: DOC_PROCESSOR_URL,
});

const setupInterceptors = (client: any) => {
  client.interceptors.request.use((config: any) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        // Add Authorization header if needed by Spring Security
        config.headers.Authorization = `Bearer ${token}`;
        
        // Add X-user-id header expected by FileController
        try {
          const decoded: any = jwtDecode(token);
          if (decoded.user_id) {
            config.headers['X-user-id'] = decoded.user_id;
          }
        } catch (e) {
          console.error("Invalid token", e);
        }
      }
    }
    return config;
  });
};

setupInterceptors(apiClient);
setupInterceptors(docClient);
