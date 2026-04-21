import axios from "axios";

const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const analyzeRepo = async (url, analysisId) =>
  (await axios.post(`${BASE}/analyze`, { url, analysis_id: analysisId }, { timeout: 240000 })).data;

export const askQuestion = async (question) =>
  (await axios.post(`${BASE}/ask`, { question }, { timeout: 60000 })).data;

export const getStatus = async () => (await axios.get(`${BASE}/status`)).data;
