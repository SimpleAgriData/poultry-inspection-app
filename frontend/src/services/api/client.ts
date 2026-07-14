import type { paths } from "@/services/api/generated/schema";
import type {
	QueryParameters,
	RequestBody,
	SuccessCommand,
	SuccessQuery,
} from "@/services/api/openapi";
import type { Status } from "@/services/domain/status";
import { type HttpClient, httpClient } from "@/services/http-client";
import { setFixedDelayInterval } from "@/services/interval";
import { Observable, type ReadOnlyObservable } from "@/services/reactive";

type ConnectionState = "connected" | "disconnected" | "connecting";

const PING_INTERVAL_MS = 15000;

type QueryOptions<TPath extends keyof paths> =
	QueryParameters<TPath> extends never
		? { signal: AbortSignal | null }
		: { signal: AbortSignal | null; params: QueryParameters<TPath> };

type CommandOptions = {
	signal: AbortSignal | null;
};

class ApiClient {
	readonly baseUrl: string;
	private http: HttpClient;
	private _connectionState = new Observable<ConnectionState>("disconnected");
	private _lastStatus = new Observable<Status | null>(null);

	constructor(baseUrl: string, http: HttpClient) {
		if (!baseUrl) {
			throw new Error("API base URL is not defined");
		}

		this.baseUrl = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
		this.http = http;
		void this.setup();
	}

	private async setup() {
		this._connectionState.set("connecting");
		this.http.onSuccessfulResponse.subscribe(() => {
			this._connectionState.set("connected");
		}, false);

		const checkConnection = async () => {
			if (this._connectionState.value === "disconnected") {
				this._connectionState.set("connecting");
			}
			const response = await this.status();
			if (response?.status === "ok") {
				this._connectionState.set("connected");
			} else {
				this._connectionState.set("disconnected");
			}
		};

		setFixedDelayInterval(checkConnection, PING_INTERVAL_MS, { runImmediately: true });
	}

	get connectionState(): ReadOnlyObservable<ConnectionState> {
		return this._connectionState;
	}

	get lastStatus(): ReadOnlyObservable<Status | null> {
		return this._lastStatus;
	}

	async runQueryRaw<TPath extends keyof paths>(
		url: TPath,
		params: QueryOptions<TPath>,
	): Promise<Response> {
		const queryParams = "params" in params ? params.params : undefined;

		const requestUrl = new URL(`${this.baseUrl}${url}`);
		if (queryParams) {
			for (const [key, value] of Object.entries(queryParams)) {
				if (value !== undefined) {
					requestUrl.searchParams.append(key, String(value));
				}
			}
		}

		return this.http.runQuery(
			requestUrl.toString(),
			true,
			params.signal ?? new AbortController().signal,
		);
	}

	async runQuery<TPath extends keyof paths>(
		url: TPath,
		params: QueryOptions<TPath>,
	): Promise<SuccessQuery<TPath>> {
		const response = await this.runQueryRaw(url, params);
		const responseData = await response.json();
		return responseData as SuccessQuery<TPath>;
	}

	async runCommand<TPath extends keyof paths, TRequestBody extends RequestBody<TPath>>(
		url: TPath,
		requestBody: TRequestBody,
		{ signal }: CommandOptions,
	): Promise<SuccessCommand<TPath>> {
		return this.http.runCommand<SuccessCommand<TPath>, TRequestBody>(
			`${this.baseUrl}${url}`,
			true,
			requestBody,
			signal ?? new AbortController().signal,
		);
	}

	async status(signal: AbortSignal | null = null): Promise<Status | null> {
		try {
			const response = await this.runQuery("/api/v1/status", { signal });
			const status = {
				status: response.status,
				version: response.version,
				gitVersion: response.git_version,
			} satisfies Status;

			this._lastStatus.set(status);
			return status;
		} catch (error: unknown) {
			if (error instanceof Error && error.name === "AbortError") {
				return null; // User aborted the request
			}
			this._lastStatus.set(null);
			return null;
		}
	}

	async ping(signal: AbortSignal | null = null): Promise<boolean> {
		try {
			await this.runQuery("/api/v1/ping", { signal });
			return true;
		} catch (error: unknown) {
			if (error instanceof Error && error.name === "AbortError") {
				return false; // User aborted the request
			}
			return false;
		}
	}
}

if (!process.env.NEXT_PUBLIC_API_ENDPOINT) {
	throw new Error("NEXT_PUBLIC_API_ENDPOINT is not defined");
}

export const apiHttpClient = new ApiClient(process.env.NEXT_PUBLIC_API_ENDPOINT, httpClient);
export type { ApiClient, ConnectionState, RequestBody, SuccessQuery };
