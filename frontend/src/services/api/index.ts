// Although these types are not defined in the api module, they are used by the api service and are part of the public interface of the module, so we re-export them here for convenience.
export type {
	AddFarmCandidate,
	AddHoldingCandidate,
	AddSectionCandidate,
	Farm,
	FarmType,
	Holding,
	Section,
	UpdateFarmCandidate,
	UpdateHoldingCandidate,
	UpdateSectionCandidate,
} from "../domain/holding";
export { type ApiService, apiService } from "./service";
