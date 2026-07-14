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

	private async fetch(url: string, isProtected: boolean, options: RequestInit): Promise<Response> {
		if (isProtected) {
			const token = await this.auth.token(false);
			options.headers = {
				...options.headers,
				authorization: `Bearer ${token}`,
			};
		}

		const response = await fetch(url, options);

		if (!response.ok) {
			throw await parseErrorResponse(response);
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

	async runCommand<TRes, TReq>(
		url: string,
		isProtected: boolean,
		requestBody: TReq,
		signal: AbortSignal,
	): Promise<TRes> {
		const response = await this.fetch(url, isProtected, {
			method: "POST",
			headers: {
				"content-type": "application/json",
			},
			body: JSON.stringify(requestBody),
			signal,
		});

		return (await response.json()) as TRes;
	}
}

export const httpClient = new HttpClient(authService);
export type { HttpClient };
export { DomainError, HttpError };
