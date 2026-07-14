import type { Farm } from "@/services/api";

const toOptions = (farms: Farm[]) =>
	farms.map((farm) => ({
		value: farm.id,
		label: `${farm.name} (${farm.sections.length} ${farm.sections.length === 1 ? "Abteil" : "Abteile"})`,
	}));

const rearingFarmOptions = (farms: Farm[], fatteningFarmId: number | null) => {
	const rearingFarms = farms.filter((f) => f.type === "rearing" || f.type === "combined");
	const fatteningFarm = farms.find((f) => f.id === fatteningFarmId);

	let matchingFarms = rearingFarms;
	if (fatteningFarm) {
		matchingFarms = rearingFarms.filter((f) => f.sections.length === fatteningFarm.sections.length);
	}
	return toOptions(matchingFarms);
};

const fatteningFarmOptions = (farms: Farm[], rearingFarmId: number | null) => {
	const fatteningFarms = farms.filter((f) => f.type === "fattening" || f.type === "combined");
	const rearingFarm = farms.find((f) => f.id === rearingFarmId);

	let matchingFarms = fatteningFarms;
	if (rearingFarm) {
		matchingFarms = fatteningFarms.filter((f) => f.sections.length === rearingFarm.sections.length);
	}
	return toOptions(matchingFarms);
};

export { fatteningFarmOptions, rearingFarmOptions };
