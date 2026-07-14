import Keycloak from "keycloak-js";
import { localStorageService } from "@/services/local-storage";

const keycloak = new Keycloak({
	url: process.env.NEXT_PUBLIC_KEYCLOAK_URL,
	realm: process.env.NEXT_PUBLIC_KEYCLOAK_REALM,
	clientId: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID,
});

export interface User {
	id: string;
	username: string;
	firstName: string;
	lastName: string;
}

const LOCAL_STORAGE_KC_TOKEN = "kc_token";
const LOCAL_STORAGE_KC_REFRESH_TOKEN = "kc_refresh_token";
const LOCAL_STORAGE_KC_ID_TOKEN = "kc_id_token";
const TOKEN_MIN_VALIDITY_SECONDS = 20;

class AuthService {
	private isInitialized = false;
	private resolveInitialization!: (value: boolean) => void;
	initialized: Promise<boolean>;

	constructor() {
		this.initialized = new Promise<boolean>((resolve) => {
			this.resolveInitialization = resolve;
		});
	}

	async initialize(): Promise<boolean> {
		const authenticated = await this.initializeKeycloak();
		this.resolveInitialization(authenticated);
		return authenticated;
	}

	private async initializeKeycloak(): Promise<boolean> {
		if (this.isInitialized) {
			return this.isAuthenticated();
		}

		const {
			token: storedToken,
			refreshToken: storedRefreshToken,
			idToken: storedIdToken,
		} = this.loadTokens();

		const authenticated = await keycloak.init({
			onLoad: "login-required",
			token: storedToken || undefined,
			refreshToken: storedRefreshToken || undefined,
			idToken: storedIdToken || undefined,
		});
		this.isInitialized = true;

		if (!authenticated) {
			return false;
		}

		await this.refreshTokens();

		setInterval(
			async () => {
				await this.refreshTokens();
			},
			(TOKEN_MIN_VALIDITY_SECONDS - 5) * 1000,
		); // Refresh a bit earlier than min validity

		return authenticated;
	}

	private async refreshTokens(): Promise<void> {
		const refreshed = await keycloak.updateToken(TOKEN_MIN_VALIDITY_SECONDS);
		if (refreshed) {
			this.saveTokens();
		}
	}

	private saveTokens(): void {
		localStorageService.setItem(LOCAL_STORAGE_KC_TOKEN, keycloak.token || "");
		localStorageService.setItem(LOCAL_STORAGE_KC_REFRESH_TOKEN, keycloak.refreshToken || "");
		localStorageService.setItem(LOCAL_STORAGE_KC_ID_TOKEN, keycloak.idToken || "");
	}

	private loadTokens() {
		const storedToken = localStorageService.getItem(LOCAL_STORAGE_KC_TOKEN);
		const storedRefreshToken = localStorageService.getItem(LOCAL_STORAGE_KC_REFRESH_TOKEN);
		const storedIdToken = localStorageService.getItem(LOCAL_STORAGE_KC_ID_TOKEN);

		return {
			token: storedToken || undefined,
			refreshToken: storedRefreshToken || undefined,
			idToken: storedIdToken || undefined,
		};
	}

	private clearTokens(): void {
		localStorageService.removeItem(LOCAL_STORAGE_KC_TOKEN);
		localStorageService.removeItem(LOCAL_STORAGE_KC_REFRESH_TOKEN);
		localStorageService.removeItem(LOCAL_STORAGE_KC_ID_TOKEN);
	}

	hasSavedCredentials(): boolean {
		const { token, refreshToken, idToken } = this.loadTokens();
		return !!(token && refreshToken && idToken);
	}

	async isAuthenticated(): Promise<boolean> {
		return keycloak.authenticated || false;
	}

	async getUserInfo(): Promise<User> {
		if (!(await this.isAuthenticated())) {
			throw new Error("User is not authenticated");
		}
		const userInfo = await keycloak.loadUserInfo();
		return {
			id: userInfo.sub || "",
			username: userInfo.preferred_username || "",
			firstName: userInfo.given_name || "",
			lastName: userInfo.family_name || "",
		};
	}

	/**
	 * Acquires an authentication token.
	 *
	 * @param optimistic - If true, allows returning a token without ensuring authentication (if the service is not initialized).
	 * @returns A promise that resolves to the authentication token.
	 * @throws An error if no token is available.
	 */
	async token(optimistic: boolean = true): Promise<string> {
		const { token: storedToken } = this.loadTokens();
		const requireAuthentication = !optimistic || this.isInitialized || !storedToken;

		let token = storedToken;

		if (requireAuthentication) {
			await this.initialized;

			const authenticated = await this.isAuthenticated();
			if (!authenticated) {
				await this.login();
			}

			if (!keycloak.token) {
				throw new Error("No authentication token available after login");
			}
			token = keycloak.token;
		}

		if (!token) {
			throw new Error("No authentication token available");
		}

		return token;
	}

	/**
	 * Triggers the login process using Keycloak.
	 *
	 * @returns A promise that resolves when the login process is initiated.
	 */
	async login(): Promise<void> {
		await keycloak.login();
	}

	async logout(): Promise<void> {
		await keycloak.logout();
		this.clearTokens();
	}
}

export const authService = new AuthService();
export type { AuthService };
