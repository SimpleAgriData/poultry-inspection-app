import { type AuthService, authService } from "@/services/auth";
import { Notifier, type ReadOnlyNotifier } from "@/services/reactive";

class HttpError extends Error {
	response: Response;

	constructor(response: Response) {
		super(`HTTP Error: ${response.status} ${response.statusText}`);
		this.response = response;
	}

	get status(): number {
		return this.response.status;
	}
}

class DomainError extends HttpError {
	detail: string | null = null;

	constructor(response: Response, detail: string | null) {
		super(response);
		this.detail = detail;
	}
}

const parseErrorResponse = async (response: Response): Promise<DomainError | HttpError> => {
	interface PossibleDomainError {
		type?: string;
		detail?: string;
	}
	let errorData: PossibleDomainError | null = null;
	try {
		errorData = (await response.json()) as PossibleDomainError;
	} catch {
		// Ignore JSON parse errors
	}

	if (errorData && errorData?.type === "Domain Exception" && errorData?.detail) {
		return new DomainError(response, errorData.detail);
	} else {
		return new HttpError(response);
	}
};

class HttpClient {
	private auth: AuthService;
	private _onSuccessfulResponse: Notifier<Response | null> = new Notifier<Response | null>(null);

	get onSuccessfulResponse(): ReadOnlyNotifier<Response | null> {
		return this._onSuccessfulResponse;
	}

	constructor(auth: AuthService) {
		this.auth = auth;
	}

	private async fetch(url: string, isProtected: boolean, options: RequestInit, throwOnHttpError = true): Promise<Response> {
		if (isProtected) {
			const token = await this.auth.token(false);
			options.headers = {
				...options.headers,
				authorization: `Bearer ${token}`,
			};
		}

		const response = await fetch(url, options);

		if (!response.ok) {
			if (throwOnHttpError) {
				throw await parseErrorResponse(response);
			}
			return response;
		}

		this._onSuccessfulResponse.notify(response);

		return response;
	}

	async runQuery(url: string, isProtected: boolean, signal: AbortSignal): Promise<Response> {
		return await this.fetch(url, isProtected, {
			method: "GET",
			signal,
		});
	}

	// soley used for stallkarte import, throwing http errors is turned off because the error is used to show why the import has failed in the UI
	async runCommandRaw<TReq>(
		url: string,
		isProtected: boolean,
		requestBody: TReq,
		signal: AbortSignal,
	): Promise<Response> {
		const isFormData = requestBody instanceof FormData;

		return this.fetch(url, isProtected, {
			method: "POST",
			headers: isFormData
				? {}
				: {
					"content-type": "application/json",
				},
			body: isFormData
				? requestBody
				: JSON.stringify(requestBody),
			signal,
		}, false);
	}
}

export const httpClient = new HttpClient(authService);
export type { HttpClient };
export { DomainError, HttpError };
