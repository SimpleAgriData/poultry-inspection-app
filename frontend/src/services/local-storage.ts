const PREFIX = "siad_stallkarte_";

const getKey = (key: string) => `${PREFIX}${key}`;

class LocalStorageService {
	setItem(key: string, value: string): void {
		localStorage.setItem(getKey(key), value);
	}

	setJsonItem<T>(key: string, value: T): void {
		const jsonString = JSON.stringify(value);
		localStorage.setItem(getKey(key), jsonString);
	}

	getJsonItem<T>(key: string): T | null {
		const jsonString = localStorage.getItem(getKey(key));
		if (jsonString) {
			try {
				return JSON.parse(jsonString) as T;
			} catch (error) {
				console.error("Failed to parse JSON from localStorage:", error);
			}
		}
		return null;
	}

	getItem(key: string): string | null {
		return localStorage.getItem(getKey(key));
	}

	removeItem(key: string): void {
		localStorage.removeItem(getKey(key));
	}

	clear(): void {
		Object.keys(localStorage).forEach((key) => {
			if (key.startsWith(PREFIX)) {
				localStorage.removeItem(key);
			}
		});
	}
}

export const localStorageService = new LocalStorageService();
