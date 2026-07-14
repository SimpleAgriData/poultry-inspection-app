import { type ApiClient, apiHttpClient } from "@/services/api/client";
import { StallkarteService } from "@/services/api/stallkarte/service";
import { responseHoldingToDomain } from "@/services/api/translate";
import type {
	AddFarmCandidate,
	AddHoldingCandidate,
	AddSectionCandidate,
	Holding,
	UpdateFarmCandidate,
	UpdateHoldingCandidate,
	UpdateSectionCandidate,
} from "@/services/domain/holding";

class Service {
	public readonly client: ApiClient;
	public readonly stallkarte: StallkarteService;

	constructor(client: ApiClient) {
		this.client = client;
		this.stallkarte = new StallkarteService(client);
	}

	async getHolding(signal: AbortSignal | null = null): Promise<Holding | null> {
		try {
			const response = await this.client.runQuery("/api/v1/find-my-agricultural-holding", {
				signal,
			});
			if (response.holding === null) {
				return null;
			}
			return responseHoldingToDomain(response.holding);
		} catch (error: unknown) {
			if (error instanceof Error && error.name === "AbortError") {
				return null; // User aborted the request
			}
			throw error;
		}
	}

	async addHolding(candidate: AddHoldingCandidate, signal: AbortSignal | null = null) {
		return this.client.runCommand(
			"/api/v1/add-agricultural-holding",
			{
				name: candidate.name,
				breed: candidate.breed,
				hatchery: candidate.hatchery,
				eco_control_number: candidate.ecoControlNumber,
				address_street: candidate.addressStreet,
				address_zip: candidate.addressZip,
				address_city: candidate.addressCity,
			},
			{ signal },
		);
	}

	async updateHolding(candidate: UpdateHoldingCandidate, signal: AbortSignal | null = null) {
		return this.client.runCommand(
			"/api/v1/update-agricultural-holding",
			{
				holding_id: candidate.holdingId,
				name: candidate.name,
				breed: candidate.breed,
				hatchery: candidate.hatchery,
				eco_control_number: candidate.ecoControlNumber,
				address_street: candidate.addressStreet,
				address_zip: candidate.addressZip,
				address_city: candidate.addressCity,
			},
			{ signal },
		);
	}

	async addFarm(candidate: AddFarmCandidate, signal: AbortSignal | null = null) {
		return this.client.runCommand(
			"/api/v1/add-farm",
			{
				type: candidate.type,
				name: candidate.name,
				agricultural_holding_id: candidate.agriculturalHoldingId,
				vvvo_number: candidate.vvvoNumber,
			},
			{ signal },
		);
	}

	async updateFarm(candidate: UpdateFarmCandidate, signal: AbortSignal | null = null) {
		return this.client.runCommand(
			"/api/v1/update-farm",
			{
				type: candidate.type,
				name: candidate.name,
				farm_id: candidate.farmId,
				vvvo_number: candidate.vvvoNumber,
			},
			{ signal },
		);
	}

	async deleteFarm(farmId: number, signal: AbortSignal | null = null) {
		return this.client.runCommand(`/api/v1/delete-farm`, { farm_id: farmId }, { signal });
	}

	async addSection(candidate: AddSectionCandidate, signal: AbortSignal | null = null) {
		return this.client.runCommand(
			"/api/v1/add-section",
			{
				farm_id: candidate.farmId,
				name: candidate.name,
			},
			{ signal },
		);
	}

	async updateSection(candidate: UpdateSectionCandidate, signal: AbortSignal | null = null) {
		return this.client.runCommand(
			"/api/v1/update-section",
			{
				section_id: candidate.sectionId,
				name: candidate.name,
			},
			{ signal },
		);
	}

	async deleteSection(sectionId: number, signal: AbortSignal | null = null) {
		return this.client.runCommand("/api/v1/delete-section", { section_id: sectionId }, { signal });
	}
}

export const apiService = new Service(apiHttpClient);
export type { Service as ApiService };
