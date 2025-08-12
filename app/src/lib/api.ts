import { dev } from "$app/environment";

export const baseApi = dev ? "http://127.0.0.1:8000/api" : "/api";
