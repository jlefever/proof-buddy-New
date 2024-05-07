import axios from 'axios';
import apiCondig from '../config/apiConfig'
import Cookies from "js-cookie";

const axiosInstanceProof = axios.create({
  baseURL: apiCondig.proofApiBaseUrl
});

// Request interceptor for API calls.
axiosInstanceProof.interceptors.request.use(
  (config) => {
    const token = Cookies.get("accessToken");
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for API calls.
axiosInstanceProof.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // TODO: Handle 401 error globally, e.g., redirecting to login or refreshing the token.
    }
    return Promise.reject(error);
  }
);

export default axiosInstanceProof;
