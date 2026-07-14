interface Section {
	id: number;
	name: string;
}

type FarmType = "rearing" | "fattening" | "combined";

interface Farm {
	id: number;
	type: FarmType;
	name: string;
	vvvoNumber: string;

	sections: Section[];
}

interface Holding {
	id: number;
	ownerUserId: string;
	name: string;
	hatchery: string;
	ecoControlNumber: string;
	breed: string;
	addressStreet: string;
	addressZip: string;
	addressCity: string;

	farms: Farm[];
}

type AddSectionCandidate = Omit<Section, "id"> & { farmId: number };
type UpdateSectionCandidate = Omit<Section, "id"> & { sectionId: number };
type AddFarmCandidate = Omit<Farm, "id" | "sections"> & { agriculturalHoldingId: number };
type UpdateFarmCandidate = Omit<Farm, "id" | "sections"> & { farmId: number };
type AddHoldingCandidate = Omit<Holding, "id" | "ownerUserId" | "farms">;
type UpdateHoldingCandidate = Omit<Holding, "id" | "ownerUserId" | "farms"> & {
	holdingId: number;
};

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
};

export const getSections = (holding: Holding): Section[] => {
	return holding.farms.flatMap((farm) => farm.sections);
};
