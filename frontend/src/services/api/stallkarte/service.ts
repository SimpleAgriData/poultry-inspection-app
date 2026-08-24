import type { ApiClient, RequestBody } from "@/services/api/client";
import type { StallkarteCommand, StallkarteCommands } from "@/services/api/stallkarte/commands";
import { requestBodyMapping } from "@/services/api/stallkarte/mapping";
import {
	responseShallowStallkarteToDomain,
	responseStallkarteToDomain,
} from "@/services/api/stallkarte/translate";
import type { ShallowStallkarte, Stallkarte } from "@/services/domain/stallkarte";

class StallkarteService {
	private readonly client: ApiClient;

	constructor(client: ApiClient) {
		this.client = client;
	}

	async getStallkarten(signal: AbortSignal | null = null): Promise<{
		activeStallkarten: ShallowStallkarte[];
		archivedStallkarten: ShallowStallkarte[];
	}> {
		const response = await this.client.runQuery("/api/v1/find-my-stallkarten", { signal });

		return {
			activeStallkarten: response.active_stallkarten.map(responseShallowStallkarteToDomain),
			archivedStallkarten: response.archived_stallkarten.map(responseShallowStallkarteToDomain),
		};
	}

	async getStallkarte(
		stallkarteId: number,
		signal: AbortSignal | null = null,
	): Promise<Stallkarte | null> {
		const response = await this.client.runQuery("/api/v1/find-stallkarte", {
			signal,
			params: {
				id: stallkarteId,
			},
		});
		if (response.stallkarte === null) {
			return null;
		}
		return responseStallkarteToDomain(response.stallkarte);
	}

	async exportStallkarte(stallkarteId: number, signal: AbortSignal | null = null): Promise<Blob> {
		const response = await this.client.runQueryRaw("/api/v1/export-stallkarte", {
			params: {
				stallkarte_id: stallkarteId,
			},
			signal,
		});
		return response.blob();
	}

	async importStallkarte(upload: FormData, signal: AbortSignal | null = null,): Promise<Response> {
		return this.client.runCommandRaw(
			"/api/v1/import-stallkarte",
			upload as unknown as RequestBody<"/api/v1/import-stallkarte">,
			{
				signal,
			},
		);
	}

	async runCommand<T extends StallkarteCommand>(
		command: T,
		args: StallkarteCommands[T],
		signal: AbortSignal | null = null,
	) {
		const mapper = requestBodyMapping[command];
		const requestBody = mapper(args);
		return await this.client.runCommand(`/api/v1/stallkarte/${command}`, requestBody, {
			signal,
		});
	}
}

export { StallkarteService };
